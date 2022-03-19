import django_tables2 as tables

from tenancy.tables import TenantColumn
from utilities.tables import BaseTable, ButtonsColumn, MarkdownColumn, TagColumn, ToggleColumn
from ipam.models import *

__all__ = (
    'FHRPGroupTable',
    'FHRPGroupAssignmentTable',
)


IPADDRESSES = """
{% for ip in record.ip_addresses.all %}
  <a href="{{ ip.get_absolute_url }}">{{ ip }}</a><br />
{% endfor %}
"""


class FHRPGroupTable(BaseTable):
    pk = ToggleColumn()
    group_id = tables.Column(
        linkify=True
    )
    comments = MarkdownColumn()
    tenant = TenantColumn()
    site = tables.Column(
        linkify=True
    )
    vlan_group = tables.Column(
        linkify=True,
        verbose_name='VLAN Group'
    )
    vlan = tables.Column(
        linkify=True,
        verbose_name='VLAN'
    )
    ip_addresses = tables.TemplateColumn(
        template_code=IPADDRESSES,
        orderable=False,
        verbose_name='IP Addresses'
    )
    member_count = tables.Column(
        verbose_name='Members'
    )
    tags = TagColumn(
        url_name='ipam:fhrpgroup_list'
    )

    class Meta(BaseTable.Meta):
        model = FHRPGroup
        fields = (
            'pk', 'group_id', 'tenant', 'site', 'vlan_group', 'vlan', 'protocol',
            'auth_type', 'auth_key', 'description', 'ip_addresses', 'member_count',
            'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'group_id', 'protocol', 'auth_type', 'description', 'ip_addresses', 'member_count')


class FHRPGroupAssignmentTable(BaseTable):
    pk = ToggleColumn()
    interface_parent = tables.Column(
        accessor=tables.A('interface__parent_object'),
        linkify=True,
        orderable=False,
        verbose_name='Parent'
    )
    interface = tables.Column(
        linkify=True,
        orderable=False
    )
    group = tables.Column(
        linkify=True
    )
    actions = ButtonsColumn(
        model=FHRPGroupAssignment,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = FHRPGroupAssignment
        fields = ('pk', 'group', 'interface_parent', 'interface', 'priority')
        exclude = ('id',)
