import django_tables2 as tables
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import DateField, DateTimeField
from django.db.models.fields.related import RelatedField
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django_tables2 import RequestConfig
from django_tables2.columns import library
from django_tables2.data import TableQuerysetData
from django_tables2.utils import Accessor

from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField, CustomLink
from .utils import content_type_identifier, content_type_name
from .paginator import EnhancedPaginator, get_paginate_count


class BaseTable(tables.Table):
    """
    Default table for object lists

    :param user: Personalize table display for the given user (optional). Has no effect if AnonymousUser is passed.
    """
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }

    def __init__(self, *args, user=None, extra_columns=None, **kwargs):
        if extra_columns is None:
            extra_columns = []

        # Add custom field columns
        obj_type = ContentType.objects.get_for_model(self._meta.model)
        cf_columns = [
            (f'cf_{cf.name}', CustomFieldColumn(cf)) for cf in CustomField.objects.filter(content_types=obj_type)
        ]
        cl_columns = [
            (f'cl_{cl.name}', CustomLinkColumn(cl)) for cl in CustomLink.objects.filter(content_type=obj_type)
        ]
        extra_columns.extend([*cf_columns, *cl_columns])

        super().__init__(*args, extra_columns=extra_columns, **kwargs)

        # Set default empty_text if none was provided
        if self.empty_text is None:
            self.empty_text = f"No {self._meta.model._meta.verbose_name_plural} found"

        # Hide non-default columns
        default_columns = getattr(self.Meta, 'default_columns', list())
        if default_columns:
            for column in self.columns:
                if column.name not in default_columns:
                    self.columns.hide(column.name)

        # Apply custom column ordering for user
        if user is not None and not isinstance(user, AnonymousUser):
            selected_columns = user.config.get(f"tables.{self.__class__.__name__}.columns")
            if selected_columns:

                # Show only persistent or selected columns
                for name, column in self.columns.items():
                    if name in ['pk', 'actions', *selected_columns]:
                        self.columns.show(name)
                    else:
                        self.columns.hide(name)

                # Rearrange the sequence to list selected columns first, followed by all remaining columns
                # TODO: There's probably a more clever way to accomplish this
                self.sequence = [
                    *[c for c in selected_columns if c in self.columns.names()],
                    *[c for c in self.columns.names() if c not in selected_columns]
                ]

                # PK column should always come first
                if 'pk' in self.sequence:
                    self.sequence.remove('pk')
                    self.sequence.insert(0, 'pk')

                # Actions column should always come last
                if 'actions' in self.sequence:
                    self.sequence.remove('actions')
                    self.sequence.append('actions')

        # Dynamically update the table's QuerySet to ensure related fields are pre-fetched
        if isinstance(self.data, TableQuerysetData):

            prefetch_fields = []
            for column in self.columns:
                if column.visible:
                    model = getattr(self.Meta, 'model')
                    accessor = column.accessor
                    prefetch_path = []
                    for field_name in accessor.split(accessor.SEPARATOR):
                        try:
                            field = model._meta.get_field(field_name)
                        except FieldDoesNotExist:
                            break
                        if isinstance(field, RelatedField):
                            # Follow ForeignKeys to the related model
                            prefetch_path.append(field_name)
                            model = field.remote_field.model
                        elif isinstance(field, GenericForeignKey):
                            # Can't prefetch beyond a GenericForeignKey
                            prefetch_path.append(field_name)
                            break
                    if prefetch_path:
                        prefetch_fields.append('__'.join(prefetch_path))
            self.data.data = self.data.data.prefetch_related(None).prefetch_related(*prefetch_fields)

    def _get_columns(self, visible=True):
        columns = []
        for name, column in self.columns.items():
            if column.visible == visible and name not in ['pk', 'actions']:
                columns.append((name, column.verbose_name))
        return columns

    @property
    def available_columns(self):
        return self._get_columns(visible=False)

    @property
    def selected_columns(self):
        return self._get_columns(visible=True)

    @property
    def objects_count(self):
        """
        Return the total number of real objects represented by the Table. This is useful when dealing with
        prefixes/IP addresses/etc., where some table rows may represent available address space.
        """
        if not hasattr(self, '_objects_count'):
            self._objects_count = sum(1 for obj in self.data if hasattr(obj, 'pk'))
        return self._objects_count


#
# Table columns
#

class ToggleColumn(tables.CheckBoxColumn):
    """
    Extend CheckBoxColumn to add a "toggle all" checkbox in the column header.
    """
    def __init__(self, *args, **kwargs):
        default = kwargs.pop('default', '')
        visible = kwargs.pop('visible', False)
        if 'attrs' not in kwargs:
            kwargs['attrs'] = {
                'td': {
                    'class': 'min-width',
                },
                'input': {
                    'class': 'form-check-input'
                }
            }
        super().__init__(*args, default=default, visible=visible, **kwargs)

    @property
    def header(self):
        return mark_safe('<input type="checkbox" class="toggle form-check-input" title="Toggle All" />')


class BooleanColumn(tables.Column):
    """
    Custom implementation of BooleanColumn to render a nicely-formatted checkmark or X icon instead of a Unicode
    character.
    """
    def render(self, value):
        if value:
            rendered = '<span class="text-success"><i class="mdi mdi-check-bold"></i></span>'
        elif value is None:
            rendered = '<span class="text-muted">&mdash;</span>'
        else:
            rendered = '<span class="text-danger"><i class="mdi mdi-close-thick"></i></span>'
        return mark_safe(rendered)

    def value(self, value):
        return str(value)


class TemplateColumn(tables.TemplateColumn):
    """
    Overrides the stock TemplateColumn to render a placeholder if the returned value is an empty string.
    """
    PLACEHOLDER = mark_safe('&mdash;')

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        if not ret.strip():
            return self.PLACEHOLDER
        return ret

    def value(self, **kwargs):
        ret = super().value(**kwargs)
        if ret == self.PLACEHOLDER:
            return ''
        return ret


@library.register
class DateColumn(tables.DateColumn):
    """
    Overrides the default implementation of DateColumn to better handle null values, returning a default value for
    tables and null when exporting data. It is registered in the tables library to use this class instead of the
    default, making this behavior consistent in all fields of type DateField.
    """

    def value(self, value):
        return value

    @classmethod
    def from_field(cls, field, **kwargs):
        if isinstance(field, DateField):
            return cls(**kwargs)


@library.register
class DateTimeColumn(tables.DateTimeColumn):
    """
    Overrides the default implementation of DateTimeColumn to better handle null values, returning a default value for
    tables and null when exporting data. It is registered in the tables library to use this class instead of the
    default, making this behavior consistent in all fields of type DateTimeField.
    """

    def value(self, value):
        if value:
            return date_format(value, format="SHORT_DATETIME_FORMAT")
        return None

    @classmethod
    def from_field(cls, field, **kwargs):
        if isinstance(field, DateTimeField):
            return cls(**kwargs)


class ButtonsColumn(tables.TemplateColumn):
    """
    Render edit, delete, and changelog buttons for an object.

    :param model: Model class to use for calculating URL view names
    :param prepend_content: Additional template content to render in the column (optional)
    """
    buttons = ('changelog', 'edit', 'delete')
    attrs = {'td': {'class': 'text-end text-nowrap noprint'}}
    # Note that braces are escaped to allow for string formatting prior to template rendering
    template_code = """
    {{% if "changelog" in buttons %}}
        <a href="{{% url '{app_label}:{model_name}_changelog' pk=record.pk %}}" class="btn btn-outline-dark btn-sm" title="Change log">
            <i class="mdi mdi-history"></i>
        </a>
    {{% endif %}}
    {{% if "edit" in buttons and perms.{app_label}.change_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_edit' pk=record.pk %}}?return_url={{{{ request.path }}}}" class="btn btn-sm btn-warning" title="Edit">
            <i class="mdi mdi-pencil"></i>
        </a>
    {{% endif %}}
    {{% if "delete" in buttons and perms.{app_label}.delete_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_delete' pk=record.pk %}}?return_url={{{{ request.path }}}}" class="btn btn-sm btn-danger" title="Delete">
            <i class="mdi mdi-trash-can-outline"></i>
        </a>
    {{% endif %}}
    """

    def __init__(self, model, *args, buttons=None, prepend_template=None, **kwargs):
        if prepend_template:
            prepend_template = prepend_template.replace('{', '{{')
            prepend_template = prepend_template.replace('}', '}}')
            self.template_code = prepend_template + self.template_code

        template_code = self.template_code.format(
            app_label=model._meta.app_label,
            model_name=model._meta.model_name,
            buttons=buttons
        )

        super().__init__(template_code=template_code, *args, **kwargs)

        # Exclude from export by default
        if 'exclude_from_export' not in kwargs:
            self.exclude_from_export = True

        self.extra_context.update({
            'buttons': buttons or self.buttons,
        })

    def header(self):
        return ''


class ChoiceFieldColumn(tables.Column):
    """
    Render a ChoiceField value inside a <span> indicating a particular CSS class. This is useful for displaying colored
    choices. The CSS class is derived by calling .get_FOO_class() on the row record.
    """
    def render(self, record, bound_column, value):
        if value:
            name = bound_column.name
            css_class = getattr(record, f'get_{name}_class')()
            label = getattr(record, f'get_{name}_display')()
            return mark_safe(
                f'<span class="badge bg-{css_class}">{label}</span>'
            )
        return self.default

    def value(self, value):
        return value


class ContentTypeColumn(tables.Column):
    """
    Display a ContentType instance.
    """
    def render(self, value):
        if value is None:
            return None
        return content_type_name(value)

    def value(self, value):
        if value is None:
            return None
        return content_type_identifier(value)


class ContentTypesColumn(tables.ManyToManyColumn):
    """
    Display a list of ContentType instances.
    """
    def __init__(self, separator=None, *args, **kwargs):
        # Use a line break as the default separator
        if separator is None:
            separator = mark_safe('<br />')
        super().__init__(separator=separator, *args, **kwargs)

    def transform(self, obj):
        return content_type_name(obj)

    def value(self, value):
        return ','.join([
            content_type_identifier(ct) for ct in self.filter(value)
        ])


class ColorColumn(tables.Column):
    """
    Display a color (#RRGGBB).
    """
    def render(self, value):
        return mark_safe(
            f'<span class="color-label" style="background-color: #{value}">&nbsp;</span>'
        )

    def value(self, value):
        return f'#{value}'


class ColoredLabelColumn(tables.TemplateColumn):
    """
    Render a colored label (e.g. for DeviceRoles).
    """
    template_code = """
{% load helpers %}
  {% if value %}
  <span class="badge" style="color: {{ value.color|fgcolor }}; background-color: #{{ value.color }}">
    <a href="{{ value.get_absolute_url }}">{{ value }}</a>
  </span>
{% else %}
  &mdash;
{% endif %}
"""

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value)


class LinkedCountColumn(tables.Column):
    """
    Render a count of related objects linked to a filtered URL.

    :param viewname: The view name to use for URL resolution
    :param view_kwargs: Additional kwargs to pass for URL resolution (optional)
    :param url_params: A dict of query parameters to append to the URL (e.g. ?foo=bar) (optional)
    """
    def __init__(self, viewname, *args, view_kwargs=None, url_params=None, default=0, **kwargs):
        self.viewname = viewname
        self.view_kwargs = view_kwargs or {}
        self.url_params = url_params
        super().__init__(*args, default=default, **kwargs)

    def render(self, record, value):
        if value:
            url = reverse(self.viewname, kwargs=self.view_kwargs)
            if self.url_params:
                url += '?' + '&'.join([
                    f'{k}={getattr(record, v) or settings.FILTERS_NULL_CHOICE_VALUE}'
                    for k, v in self.url_params.items()
                ])
            return mark_safe(f'<a href="{url}">{value}</a>')
        return value

    def value(self, value):
        return value


class TagColumn(tables.TemplateColumn):
    """
    Display a list of tags assigned to the object.
    """
    template_code = """
    {% load helpers %}
    {% for tag in value.all %}
        {% tag tag url_name=url_name %}
    {% empty %}
        <span class="text-muted">&mdash;</span>
    {% endfor %}
    """

    def __init__(self, url_name=None):
        super().__init__(
            orderable=False,
            template_code=self.template_code,
            extra_context={'url_name': url_name}
        )

    def value(self, value):
        return ",".join([tag.name for tag in value.all()])


class CustomFieldColumn(tables.Column):
    """
    Display custom fields in the appropriate format.
    """
    def __init__(self, customfield, *args, **kwargs):
        self.customfield = customfield
        kwargs['accessor'] = Accessor(f'custom_field_data__{customfield.name}')
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = customfield.label or customfield.name

        super().__init__(*args, **kwargs)

    def render(self, value):
        if isinstance(value, list):
            return ', '.join(v for v in value)
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value is True:
            return mark_safe('<i class="mdi mdi-check-bold text-success"></i>')
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value is False:
            return mark_safe('<i class="mdi mdi-close-thick text-danger"></i>')
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_URL:
            return mark_safe(f'<a href="{value}">{value}</a>')
        if value is not None:
            return value
        return self.default

    def value(self, value):
        if isinstance(value, list):
            return ','.join(v for v in value)
        if value is not None:
            return value
        return self.default


class CustomLinkColumn(tables.Column):
    """
    Render a custom links as a table column.
    """
    def __init__(self, customlink, *args, **kwargs):
        self.customlink = customlink
        kwargs['accessor'] = Accessor('pk')
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = customlink.name

        super().__init__(*args, **kwargs)

    def render(self, record):
        try:
            rendered = self.customlink.render({'obj': record})
            if rendered:
                return mark_safe(f'<a href="{rendered["link"]}"{rendered["link_target"]}>{rendered["text"]}</a>')
        except Exception as e:
            return mark_safe(f'<span class="text-danger" title="{e}"><i class="mdi mdi-alert"></i> Error</span>')
        return ''

    def value(self, record):
        try:
            rendered = self.customlink.render({'obj': record})
            if rendered:
                return rendered['link']
        except Exception:
            pass
        return None


class MPTTColumn(tables.TemplateColumn):
    """
    Display a nested hierarchy for MPTT-enabled models.
    """
    template_code = """
        {% load helpers %}
        {% for i in record.level|as_range %}<i class="mdi mdi-circle-small"></i>{% endfor %}
        <a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            template_code=self.template_code,
            orderable=False,
            attrs={'td': {'class': 'text-nowrap'}},
            *args,
            **kwargs
        )

    def value(self, value):
        return value


class UtilizationColumn(tables.TemplateColumn):
    """
    Display a colored utilization bar graph.
    """
    template_code = """{% load helpers %}{% if record.pk %}{% utilization_graph value %}{% endif %}"""

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return f'{value}%'


class MarkdownColumn(tables.TemplateColumn):
    """
    Render a Markdown string.
    """
    template_code = """
    {% load helpers %}
    {% if value %}
      {{ value|render_markdown }}
    {% else %}
      &mdash;
    {% endif %}
    """

    def __init__(self):
        super().__init__(
            template_code=self.template_code
        )

    def value(self, value):
        return value


#
# Pagination
#

def paginate_table(table, request):
    """
    Paginate a table given a request context.
    """
    paginate = {
        'paginator_class': EnhancedPaginator,
        'per_page': get_paginate_count(request)
    }
    RequestConfig(request, paginate).configure(table)


#
# Callables
#

def linkify_email(value):
    if value is None:
        return None
    return f"mailto:{value}"


def linkify_phone(value):
    if value is None:
        return None
    return f"tel:{value}"
