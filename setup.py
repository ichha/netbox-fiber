from setuptools import find_packages, setup

setup(
    name='netbox-fiber',
    version='0.1.0',
    description='A NetBox plugin for managing optical fiber routes, vendors, drop points, core allocations, and topologies.',
    install_requires=[],
    author='Nepal Telecom',
    author_email='info@ntc.net.np',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'netbox_fiber': ['templates/*/*', 'templates/*', 'static/*/*', 'static/*'],
    },
    zip_safe=False,
)
