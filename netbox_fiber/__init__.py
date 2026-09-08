from netbox.plugins import PluginConfig


class NetBoxFiberConfig(PluginConfig):
    name = 'netbox_fiber'
    verbose_name = 'Fiber Management'
    description = 'A NetBox plugin for managing optical fiber routes, vendors, drop points, core allocations, and topologies.'
    version = '0.1.0'
    author = 'Nepal Telecom'
    author_email = 'info@ntc.net.np'
    base_url = 'fiber'
    min_version = '4.0.0'
    default_settings = {}


config = NetBoxFiberConfig
