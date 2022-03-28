import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import (
    ConsolePort, ConsoleServerPort, Device, DeviceBay, DeviceRole, FrontPort, Interface, InventoryItem, Platform,
    PowerOutlet, PowerPort, RearPort, VirtualChassis,
)
from tenancy.tables import TenantColumn
from utilities.tables import (
    BaseTable, BooleanColumn, ButtonsColumn, ChoiceFieldColumn, ColorColumn, ColoredLabelColumn, LinkedCountColumn,
    MarkdownColumn, TagColumn, TemplateColumn, ToggleColumn,
)
from .template_code import *

__all__ = (
    'BaseInterfaceTable',
    'CableTerminationTable',
    'ConsolePortTable',
    'ConsoleServerPortTable',
    'DeviceBayTable',
    'DeviceConsolePortTable',
    'DeviceConsoleServerPortTable',
    'DeviceDeviceBayTable',
    'DeviceFrontPortTable',
    'DeviceImportTable',
    'DeviceInterfaceTable',
    'DeviceInventoryItemTable',
    'DevicePowerPortTable',
    'DevicePowerOutletTable',
    'DeviceRearPortTable',
    'DeviceRoleTable',
    'DeviceTable',
    'FrontPortTable',
    'InterfaceTable',
    'InventoryItemTable',
    'PlatformTable',
    'PowerOutletTable',
    'PowerPortTable',
    'RearPortTable',
    'VirtualChassisTable',
)


def get_cabletermination_row_class(record):
    if record.mark_connected:
        return 'success'
    elif record.cable:
        return record.cable.get_status_class()
    return ''


def get_interface_row_class(record):
    if not record.enabled:
        return 'danger'
    elif record.is_virtual:
        return 'primary'
    return get_cabletermination_row_class(record)


def get_interface_state_attribute(record):
    """
    Get interface enabled state as string to attach to <tr/> DOM element.
    """
    if record.enabled:
        return "enabled"
    else:
        return "disabled"

#
# Device roles
#


class DeviceRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'role_id': 'pk'},
        verbose_name='Devices'
    )
    vm_count = LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'role_id': 'pk'},
        verbose_name='VMs'
    )
    color = ColorColumn()
    vm_role = BooleanColumn()
    tags = TagColumn(
        url_name='dcim:devicerole_list'
    )
    actions = ButtonsColumn(DeviceRole)

    class Meta(BaseTable.Meta):
        model = DeviceRole
        fields = (
            'pk', 'id', 'name', 'device_count', 'vm_count', 'color', 'vm_role', 'description', 'slug', 'tags',
            'actions', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device_count', 'vm_count', 'color', 'vm_role', 'description', 'actions')


#
# Platforms
#

class PlatformTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'platform_id': 'pk'},
        verbose_name='Devices'
    )
    vm_count = LinkedCountColumn(
        viewname='virtualization:virtualmachine_list',
        url_params={'platform_id': 'pk'},
        verbose_name='VMs'
    )
    tags = TagColumn(
        url_name='dcim:platform_list'
    )
    actions = ButtonsColumn(Platform)

    class Meta(BaseTable.Meta):
        model = Platform
        fields = (
            'pk', 'id', 'name', 'manufacturer', 'device_count', 'vm_count', 'slug', 'napalm_driver', 'napalm_args',
            'description', 'tags', 'actions', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'manufacturer', 'device_count', 'vm_count', 'napalm_driver', 'description', 'actions',
        )


#
# Devices
#

class DeviceTable(BaseTable):
    pk = ToggleColumn()
    name = tables.TemplateColumn(
        order_by=('_name',),
        template_code=DEVICE_LINK
    )
    status = ChoiceFieldColumn()
    tenant = TenantColumn()
    site = tables.Column(
        linkify=True
    )
    location = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    device_role = ColoredLabelColumn(
        verbose_name='Role'
    )
    manufacturer = tables.Column(
        accessor=Accessor('device_type__manufacturer'),
        linkify=True
    )
    device_type = tables.Column(
        linkify=True,
        verbose_name='Type'
    )
    primary_ip = tables.Column(
        linkify=True,
        order_by=('primary_ip4', 'primary_ip6'),
        verbose_name='IP Address'
    )
    primary_ip4 = tables.Column(
        linkify=True,
        verbose_name='IPv4 Address'
    )
    primary_ip6 = tables.Column(
        linkify=True,
        verbose_name='IPv6 Address'
    )
    cluster = tables.Column(
        linkify=True
    )
    virtual_chassis = tables.Column(
        linkify=True
    )
    vc_position = tables.Column(
        verbose_name='VC Position'
    )
    vc_priority = tables.Column(
        verbose_name='VC Priority'
    )
    contacts = tables.ManyToManyColumn(
        linkify_item=True
    )
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='dcim:device_list'
    )

    class Meta(BaseTable.Meta):
        model = Device
        fields = (
            'pk', 'id', 'name', 'status', 'tenant', 'device_role', 'manufacturer', 'device_type', 'platform', 'serial',
            'asset_tag', 'site', 'location', 'rack', 'position', 'face', 'primary_ip', 'airflow', 'primary_ip4',
            'primary_ip6', 'cluster', 'virtual_chassis', 'vc_position', 'vc_priority', 'comments', 'contacts', 'tags',
            'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'status', 'tenant', 'site', 'location', 'rack', 'device_role', 'manufacturer', 'device_type',
            'primary_ip',
        )


class DeviceImportTable(BaseTable):
    name = tables.TemplateColumn(
        template_code=DEVICE_LINK
    )
    status = ChoiceFieldColumn()
    tenant = TenantColumn()
    site = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    device_role = tables.Column(
        verbose_name='Role'
    )
    device_type = tables.Column(
        verbose_name='Type'
    )

    class Meta(BaseTable.Meta):
        model = Device
        fields = ('id', 'name', 'status', 'tenant', 'site', 'rack', 'position', 'device_role', 'device_type')
        empty_text = False


#
# Device components
#

class DeviceComponentTable(BaseTable):
    pk = ToggleColumn()
    device = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True,
        order_by=('_name',)
    )

    class Meta(BaseTable.Meta):
        order_by = ('device', 'name')


class CableTerminationTable(BaseTable):
    cable = tables.Column(
        linkify=True
    )
    cable_color = ColorColumn(
        accessor='cable__color',
        orderable=False,
        verbose_name='Cable Color'
    )
    link_peer = TemplateColumn(
        accessor='_link_peer',
        template_code=LINKTERMINATION,
        orderable=False,
        verbose_name='Link Peer'
    )
    mark_connected = BooleanColumn()


class PathEndpointTable(CableTerminationTable):
    connection = TemplateColumn(
        accessor='_path__last_node',
        template_code=LINKTERMINATION,
        verbose_name='Connection',
        orderable=False
    )


class ConsolePortTable(DeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_consoleports',
            'args': [Accessor('device_id')],
        }
    )
    tags = TagColumn(
        url_name='dcim:consoleport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = ConsolePort
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'type', 'speed', 'description', 'mark_connected', 'cable', 'cable_color',
            'link_peer', 'connection', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'speed', 'description')


class DeviceConsolePortTable(ConsolePortTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-console"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=ConsolePort,
        buttons=('edit', 'delete'),
        prepend_template=CONSOLEPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = ConsolePort
        fields = (
            'pk', 'id', 'name', 'label', 'type', 'speed', 'description', 'mark_connected', 'cable', 'cable_color',
            'link_peer', 'connection', 'tags', 'actions'
        )
        default_columns = ('pk', 'name', 'label', 'type', 'speed', 'description', 'cable', 'connection', 'actions')
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class ConsoleServerPortTable(DeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_consoleserverports',
            'args': [Accessor('device_id')],
        }
    )
    tags = TagColumn(
        url_name='dcim:consoleserverport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = ConsoleServerPort
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'type', 'speed', 'description', 'mark_connected', 'cable',
            'cable_color', 'link_peer', 'connection', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'speed', 'description')


class DeviceConsoleServerPortTable(ConsoleServerPortTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-console-network-outline"></i> '
                      '<a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=ConsoleServerPort,
        buttons=('edit', 'delete'),
        prepend_template=CONSOLESERVERPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = ConsoleServerPort
        fields = (
            'pk', 'id', 'name', 'label', 'type', 'speed', 'description', 'mark_connected', 'cable', 'cable_color',
            'link_peer', 'connection', 'tags', 'actions',
        )
        default_columns = ('pk', 'name', 'label', 'type', 'speed', 'description', 'cable', 'connection', 'actions')
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class PowerPortTable(DeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_powerports',
            'args': [Accessor('device_id')],
        }
    )
    tags = TagColumn(
        url_name='dcim:powerport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = PowerPort
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'type', 'description', 'mark_connected', 'maximum_draw',
            'allocated_draw', 'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description')


class DevicePowerPortTable(PowerPortTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-power-plug-outline"></i> <a href="{{ record.get_absolute_url }}">'
                      '{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=PowerPort,
        buttons=('edit', 'delete'),
        prepend_template=POWERPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = PowerPort
        fields = (
            'pk', 'id', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'mark_connected',
            'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description', 'cable', 'connection',
            'actions',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class PowerOutletTable(DeviceComponentTable, PathEndpointTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_poweroutlets',
            'args': [Accessor('device_id')],
        }
    )
    power_port = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='dcim:poweroutlet_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = PowerOutlet
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'type', 'description', 'power_port', 'feed_leg', 'mark_connected',
            'cable', 'cable_color', 'link_peer', 'connection', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'power_port', 'feed_leg', 'description')


class DevicePowerOutletTable(PowerOutletTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-power-socket"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=PowerOutlet,
        buttons=('edit', 'delete'),
        prepend_template=POWEROUTLET_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = PowerOutlet
        fields = (
            'pk', 'id', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description', 'mark_connected', 'cable',
            'cable_color', 'link_peer', 'connection', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description', 'cable', 'connection', 'actions',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class BaseInterfaceTable(BaseTable):
    enabled = BooleanColumn()
    ip_addresses = tables.TemplateColumn(
        template_code=INTERFACE_IPADDRESSES,
        orderable=False,
        verbose_name='IP Addresses'
    )
    fhrp_groups = tables.TemplateColumn(
        accessor=Accessor('fhrp_group_assignments'),
        template_code=INTERFACE_FHRPGROUPS,
        orderable=False,
        verbose_name='FHRP Groups'
    )
    untagged_vlan = tables.Column(linkify=True)
    tagged_vlans = TemplateColumn(
        template_code=INTERFACE_TAGGED_VLANS,
        orderable=False,
        verbose_name='Tagged VLANs'
    )


class InterfaceTable(DeviceComponentTable, BaseInterfaceTable, PathEndpointTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_interfaces',
            'args': [Accessor('device_id')],
        }
    )
    mgmt_only = BooleanColumn()
    wireless_link = tables.Column(
        linkify=True
    )
    wireless_lans = TemplateColumn(
        template_code=INTERFACE_WIRELESS_LANS,
        orderable=False,
        verbose_name='Wireless LANs'
    )
    tags = TagColumn(
        url_name='dcim:interface_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = Interface
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'enabled', 'type', 'mgmt_only', 'mtu', 'mode', 'mac_address', 'wwn',
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'description',
            'mark_connected', 'cable', 'cable_color', 'wireless_link', 'wireless_lans', 'link_peer', 'connection',
            'tags', 'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'enabled', 'type', 'description')


class DeviceInterfaceTable(InterfaceTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-{% if record.mgmt_only %}wrench{% elif record.is_lag %}reorder-horizontal'
                      '{% elif record.is_virtual %}circle{% elif record.is_wireless %}wifi{% else %}ethernet'
                      '{% endif %}"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    parent = tables.Column(
        linkify=True
    )
    bridge = tables.Column(
        linkify=True
    )
    lag = tables.Column(
        linkify=True,
        verbose_name='LAG'
    )
    actions = ButtonsColumn(
        model=Interface,
        buttons=('edit', 'delete'),
        prepend_template=INTERFACE_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = Interface
        fields = (
            'pk', 'id', 'name', 'label', 'enabled', 'type', 'parent', 'bridge', 'lag', 'mgmt_only', 'mtu', 'mode',
            'mac_address', 'wwn', 'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power',
            'description', 'mark_connected', 'cable', 'cable_color', 'wireless_link', 'wireless_lans', 'link_peer',
            'connection', 'tags', 'ip_addresses', 'fhrp_groups', 'untagged_vlan', 'tagged_vlans', 'actions',
        )
        order_by = ('name',)
        default_columns = (
            'pk', 'name', 'label', 'enabled', 'type', 'parent', 'lag', 'mtu', 'mode', 'description', 'ip_addresses',
            'cable', 'connection', 'actions',
        )
        row_attrs = {
            'class': get_interface_row_class,
            'data-name': lambda record: record.name,
            'data-enabled': get_interface_state_attribute,
        }


class FrontPortTable(DeviceComponentTable, CableTerminationTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_frontports',
            'args': [Accessor('device_id')],
        }
    )
    color = ColorColumn()
    rear_port_position = tables.Column(
        verbose_name='Position'
    )
    rear_port = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='dcim:frontport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = FrontPort
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description',
            'mark_connected', 'cable', 'cable_color', 'link_peer', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'device', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'description',
        )


class DeviceFrontPortTable(FrontPortTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-square-rounded{% if not record.cable %}-outline{% endif %}"></i> '
                      '<a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=FrontPort,
        buttons=('edit', 'delete'),
        prepend_template=FRONTPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = FrontPort
        fields = (
            'pk', 'id', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description', 'mark_connected', 'cable',
            'cable_color', 'link_peer', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description', 'cable', 'link_peer',
            'actions',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class RearPortTable(DeviceComponentTable, CableTerminationTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_rearports',
            'args': [Accessor('device_id')],
        }
    )
    color = ColorColumn()
    tags = TagColumn(
        url_name='dcim:rearport_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = RearPort
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'type', 'color', 'positions', 'description', 'mark_connected', 'cable',
            'cable_color', 'link_peer', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'type', 'color', 'description')


class DeviceRearPortTable(RearPortTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-square-rounded{% if not record.cable %}-outline{% endif %}"></i> '
                      '<a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=RearPort,
        buttons=('edit', 'delete'),
        prepend_template=REARPORT_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = RearPort
        fields = (
            'pk', 'id', 'name', 'label', 'type', 'positions', 'description', 'mark_connected', 'cable', 'cable_color',
            'link_peer', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'type', 'positions', 'description', 'cable', 'link_peer', 'actions',
        )
        row_attrs = {
            'class': get_cabletermination_row_class
        }


class DeviceBayTable(DeviceComponentTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_devicebays',
            'args': [Accessor('device_id')],
        }
    )
    device_role = ColoredLabelColumn(
        accessor=Accessor('installed_device__device_role'),
        verbose_name='Role'
    )
    device_type = tables.Column(
        accessor=Accessor('installed_device__device_type'),
        linkify=True,
        verbose_name='Type'
    )
    status = tables.TemplateColumn(
        template_code=DEVICEBAY_STATUS,
        order_by=Accessor('installed_device__status')
    )
    installed_device = tables.Column(
        linkify=True
    )
    tags = TagColumn(
        url_name='dcim:devicebay_list'
    )

    class Meta(DeviceComponentTable.Meta):
        model = DeviceBay
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'status', 'device_role', 'device_type', 'installed_device', 'description', 'tags',
            'created', 'last_updated',
        )

        default_columns = ('pk', 'name', 'device', 'label', 'status', 'installed_device', 'description')


class DeviceDeviceBayTable(DeviceBayTable):
    name = tables.TemplateColumn(
        template_code='<i class="mdi mdi-circle{% if record.installed_device %}slice-8{% else %}outline{% endif %}'
                      '"></i> <a href="{{ record.get_absolute_url }}">{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=DeviceBay,
        buttons=('edit', 'delete'),
        prepend_template=DEVICEBAY_BUTTONS
    )

    class Meta(DeviceComponentTable.Meta):
        model = DeviceBay
        fields = (
            'pk', 'id', 'name', 'label', 'status', 'installed_device', 'description', 'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'status', 'installed_device', 'description', 'actions',
        )


class InventoryItemTable(DeviceComponentTable):
    device = tables.Column(
        linkify={
            'viewname': 'dcim:device_inventory',
            'args': [Accessor('device_id')],
        }
    )
    manufacturer = tables.Column(
        linkify=True
    )
    discovered = BooleanColumn()
    tags = TagColumn(
        url_name='dcim:inventoryitem_list'
    )
    cable = None  # Override DeviceComponentTable

    class Meta(BaseTable.Meta):
        model = InventoryItem
        fields = (
            'pk', 'id', 'name', 'device', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description',
            'discovered', 'tags', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag')


class DeviceInventoryItemTable(InventoryItemTable):
    name = tables.TemplateColumn(
        template_code='<a href="{{ record.get_absolute_url }}" style="padding-left: {{ record.level }}0px">'
                      '{{ value }}</a>',
        order_by=Accessor('_name'),
        attrs={'td': {'class': 'text-nowrap'}}
    )
    actions = ButtonsColumn(
        model=InventoryItem,
        buttons=('edit', 'delete')
    )

    class Meta(BaseTable.Meta):
        model = InventoryItem
        fields = (
            'pk', 'id', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description', 'discovered',
            'tags', 'actions',
        )
        default_columns = (
            'pk', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'description', 'discovered',
            'actions',
        )


#
# Virtual chassis
#

class VirtualChassisTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    master = tables.Column(
        linkify=True
    )
    member_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'virtual_chassis_id': 'pk'},
        verbose_name='Members'
    )
    tags = TagColumn(
        url_name='dcim:virtualchassis_list'
    )

    class Meta(BaseTable.Meta):
        model = VirtualChassis
        fields = ('pk', 'id', 'name', 'domain', 'master', 'member_count', 'tags', 'created', 'last_updated',)
        default_columns = ('pk', 'name', 'domain', 'master', 'member_count')
