from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton
from netbox.choices import ButtonColorChoices

menu = PluginMenu(
    label='Fiber',
    icon_class='mdi mdi-ray-vertex',
    groups=(
        ('Fiber Inventory', (
            PluginMenuItem(
                link='plugins:netbox_fiber:fiberroute_list',
                link_text='Fiber Routes',
                permissions=['netbox_fiber.view_fiberroute'],
                buttons=(
                    PluginMenuButton(
                        link='plugins:netbox_fiber:fiberroute_add',
                        title='Add Route',
                        icon_class='mdi mdi-plus-thick',
                        color=ButtonColorChoices.GREEN,
                        permissions=['netbox_fiber.add_fiberroute'],
                    ),
                    PluginMenuButton(
                        link='plugins:netbox_fiber:fiberroute_import',
                        title='Import Routes',
                        icon_class='mdi mdi-upload',
                        color=ButtonColorChoices.BLUE,
                        permissions=['netbox_fiber.add_fiberroute'],
                    ),
                ),
            ),
            PluginMenuItem(
                link='plugins:netbox_fiber:fiberdroppoint_list',
                link_text='Drop Points',
                permissions=['netbox_fiber.view_fiberdroppoint'],
                buttons=(
                    PluginMenuButton(
                        link='plugins:netbox_fiber:fiberdroppoint_add',
                        title='Add Drop Point',
                        icon_class='mdi mdi-plus-thick',
                        color=ButtonColorChoices.GREEN,
                        permissions=['netbox_fiber.add_fiberdroppoint'],
                    ),
                    PluginMenuButton(
                        link='plugins:netbox_fiber:fiberdroppoint_import',
                        title='Import Drop Points',
                        icon_class='mdi mdi-upload',
                        color=ButtonColorChoices.BLUE,
                        permissions=['netbox_fiber.add_fiberdroppoint'],
                    ),
                ),
            ),
            PluginMenuItem(
                link='plugins:netbox_fiber:fibervendor_list',
                link_text='Vendors',
                permissions=['netbox_fiber.view_fibervendor'],
                buttons=(
                    PluginMenuButton(
                        link='plugins:netbox_fiber:fibervendor_add',
                        title='Add Vendor',
                        icon_class='mdi mdi-plus-thick',
                        color=ButtonColorChoices.GREEN,
                        permissions=['netbox_fiber.add_fibervendor'],
                    ),
                    PluginMenuButton(
                        link='plugins:netbox_fiber:fibervendor_import',
                        title='Import Vendors',
                        icon_class='mdi mdi-upload',
                        color=ButtonColorChoices.BLUE,
                        permissions=['netbox_fiber.add_fibervendor'],
                    ),
                ),
            ),
            PluginMenuItem(
                link='plugins:netbox_fiber:vendor_view',
                link_text='Vendor Explorer',
                permissions=['netbox_fiber.view_fiberroute'],
            ),
        )),
    ),
)
