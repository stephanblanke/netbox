from django import forms

from dcim.models import Region, Site, SiteGroup
from tenancy.forms import TenancyForm
from extras.forms import AddRemoveTagsForm, CustomFieldModelBulkEditForm
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BulkEditNullBooleanSelect, DatePicker, DynamicModelChoiceField, NumericArrayField, StaticSelect,
    DynamicModelMultipleChoiceField,
)

__all__ = (
    'AggregateBulkEditForm',
    'ASNBulkEditForm',
    'FHRPGroupBulkEditForm',
    'IPAddressBulkEditForm',
    'IPRangeBulkEditForm',
    'PrefixBulkEditForm',
    'RIRBulkEditForm',
    'RoleBulkEditForm',
    'RouteTargetBulkEditForm',
    'ServiceBulkEditForm',
    'VLANBulkEditForm',
    'VLANGroupBulkEditForm',
    'VRFBulkEditForm',
)


class VRFBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    enforce_unique = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Enforce unique space'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


class RouteTargetBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = [
            'tenant', 'description',
        ]


class RIRBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    is_private = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['is_private', 'description']


class ASNBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label='RIR'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'date_added', 'description',
        ]
        widgets = {
            'date_added': DatePicker(),
        }


class AggregateBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label='RIR'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    date_added = forms.DateField(
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'date_added', 'description',
        ]
        widgets = {
            'date_added': DatePicker(),
        }


class RoleBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    weight = forms.IntegerField(
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['description']


class PrefixBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    prefix_length = forms.IntegerField(
        min_value=PREFIX_LENGTH_MIN,
        max_value=PREFIX_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PrefixStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    is_pool = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Is a pool'
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Treat as 100% utilized'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'site', 'vrf', 'tenant', 'role', 'description',
        ]


class IPRangeBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(IPRangeStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'vrf', 'tenant', 'role', 'description',
        ]


class IPAddressBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    mask_length = forms.IntegerField(
        min_value=IPADDRESS_MASK_LENGTH_MIN,
        max_value=IPADDRESS_MASK_LENGTH_MAX,
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(IPAddressStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = forms.ChoiceField(
        choices=add_blank_choice(IPAddressRoleChoices),
        required=False,
        widget=StaticSelect()
    )
    dns_name = forms.CharField(
        max_length=255,
        required=False,
        label='DNS name'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'vrf', 'role', 'tenant', 'dns_name', 'description',
        ]


class FHRPGroupBulkEditForm(AddRemoveTagsForm, TenancyForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=FHRPGroup.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label='Group ID'
    )
    auth_type = forms.ChoiceField(
        choices=add_blank_choice(FHRPGroupAuthTypeChoices),
        required=False,
        widget=StaticSelect(),
        label='Authentication type'
    )
    auth_key = forms.CharField(
        max_length=255,
        required=False,
        label='Authentication key'
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN Group',
        query_params={
            'site_id': '$site',
        }
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='VLAN',
        query_params={
            'group_id': '$vlan_group'
        }
    )

    class Meta:
        nullable_fields = ['tenant', 'site', 'vlan_group', 'vlan', 'auth_type', 'auth_key', 'description']


class VLANGroupBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['site', 'description']


class VLANBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(VLANStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'site', 'group', 'tenant', 'role', 'description',
        ]


class ServiceBulkEditForm(AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect()
    )
    ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'description',
        ]
