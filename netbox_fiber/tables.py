import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import FiberVendor, FiberRoute, FiberDropPoint


class FiberVendorTable(NetBoxTable):
    name = tables.Column(linkify=True)
    contact_name = tables.Column(verbose_name='Contact Person')
    contact_phone = tables.Column(verbose_name='Phone')
    contact_email = tables.Column(verbose_name='Email')
    total_routes_count = tables.Column(verbose_name='Total Routes')
    total_distance_km = tables.Column(verbose_name='Total KM')
    tags = columns.TagColumn(url_name='plugins:netbox_fiber:fibervendor_list')
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = FiberVendor
        fields = (
            'pk', 'id', 'name', 'contact_name', 'contact_phone', 'contact_email',
            'total_routes_count', 'total_distance_km', 'description', 'tags', 'actions'
        )
        default_columns = (
            'pk', 'name', 'contact_name', 'contact_phone',
            'total_routes_count', 'total_distance_km', 'actions'
        )


class FiberRouteTable(NetBoxTable):
    name = tables.Column(linkify=True)
    vendor = tables.Column(linkify=True)
    start_point = tables.Column(accessor='start_point_display', verbose_name='Starting Point')
    end_point = tables.Column(accessor='end_point_display', verbose_name='End Point')
    total_length_km = tables.Column(verbose_name='Length (KM)')
    total_cores = tables.Column(verbose_name='Cores')
    cable_type = columns.ChoiceFieldColumn(verbose_name='Type')
    status = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name='plugins:netbox_fiber:fiberroute_list')
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = FiberRoute
        fields = (
            'pk', 'id', 'name', 'vendor', 'cable_type', 'status',
            'start_point', 'end_point', 'total_length_km', 'total_cores',
            'description', 'tags', 'actions'
        )
        default_columns = (
            'pk', 'name', 'vendor', 'start_point', 'end_point',
            'total_length_km', 'total_cores', 'status', 'actions'
        )


class FiberDropPointTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name='Point / Station Name')
    fiber_route = tables.Column(linkify=True, verbose_name='Fiber Route')
    site = tables.Column(linkify=True, verbose_name='NetBox Site')
    point_type = columns.ChoiceFieldColumn(verbose_name='Point Type')
    distance_km = tables.Column(verbose_name='Distance (KM)')
    tags = columns.TagColumn(url_name='plugins:netbox_fiber:fiberdroppoint_list')
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = FiberDropPoint
        fields = (
            'pk', 'id', 'name', 'fiber_route', 'site', 'point_type',
            'distance_km', 'description', 'tags', 'actions'
        )
        default_columns = (
            'pk', 'name', 'fiber_route', 'site', 'point_type',
            'distance_km', 'actions'
        )
