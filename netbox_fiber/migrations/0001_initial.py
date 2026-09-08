from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0001_initial'),
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FiberVendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(help_text='Vendor / Provider Name', max_length=100, unique=True)),
                ('slug', models.SlugField(help_text='URL-friendly slug', max_length=100, unique=True)),
                ('contact_name', models.CharField(blank=True, help_text='Primary Contact Person', max_length=100)),
                ('contact_phone', models.CharField(blank=True, help_text='Contact Phone Number', max_length=50)),
                ('contact_email', models.EmailField(blank=True, help_text='Contact Email Address', max_length=254)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('comments', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Fiber Vendor',
                'verbose_name_plural': 'Fiber Vendors',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='FiberRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(help_text="Route Name (e.g. 'Galchhi - Gajuri')", max_length=150, unique=True)),
                ('cable_type', models.CharField(default='adss', help_text='Cable installation type', max_length=50)),
                ('total_length_km', models.DecimalField(decimal_places=3, help_text='Total length of route in kilometers (e.g. 14.855)', max_digits=10, verbose_name='Total Length (KM)')),
                ('total_cores', models.PositiveIntegerField(default=6, help_text='Total fiber cores in the cable (e.g. 6, 12, 24, 48, 96)', verbose_name='Total Cores')),
                ('start_site_name', models.CharField(blank=True, help_text="Starting Point Site / Location Name (e.g. 'Galchhi')", max_length=100)),
                ('start_cores_dropped', models.CharField(blank=True, help_text="Cores terminated / dropped at Starting Point (e.g. '1-6' or '1, 2, 3, 4, 5, 6')", max_length=255)),
                ('end_site_name', models.CharField(blank=True, help_text="End Point Site / Location Name (e.g. 'Gajuri')", max_length=100)),
                ('end_cores_dropped', models.CharField(blank=True, help_text="Cores terminated / dropped at End Point (e.g. '1, 2' or '1-2')", max_length=255)),
                ('status', models.CharField(default='active', help_text='Operational status of the route', max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('comments', models.TextField(blank=True)),
                ('end_site', models.ForeignKey(blank=True, help_text='End NetBox Site (optional if using custom name)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fiber_routes_ending', to='dcim.site')),
                ('start_site', models.ForeignKey(blank=True, help_text='Starting NetBox Site (optional if using custom name)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fiber_routes_starting', to='dcim.site')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('vendor', models.ForeignKey(help_text='Fiber Vendor or Provider', on_delete=django.db.models.deletion.PROTECT, related_name='fiber_routes', to='netbox_fiber.fibervendor')),
            ],
            options={
                'verbose_name': 'Fiber Route',
                'verbose_name_plural': 'Fiber Routes',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='FiberDropPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(help_text="Drop Point / Site / Joint Name (e.g. 'Thameldanda', 'Taruka_Joint', 'Adamghat')", max_length=100)),
                ('point_type', models.CharField(default='site', help_text='Type of drop point', max_length=50)),
                ('sequence', models.PositiveIntegerField(default=1, help_text='Sequence order along the route (e.g. 1, 2, 3...)')),
                ('distance_km', models.DecimalField(blank=True, decimal_places=3, help_text='Distance marker in KM from route starting point (optional)', max_digits=10, null=True)),
                ('dropped_cores', models.CharField(help_text="Cores dropped / spliced at this point (e.g. '3, 4' or '3-4')", max_length=255)),
                ('passed_cores', models.CharField(blank=True, help_text='Cores passing through without termination (optional, e.g. \'1, 2, 5, 6\')', max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('comments', models.TextField(blank=True)),
                ('fiber_route', models.ForeignKey(help_text='Associated Fiber Route', on_delete=django.db.models.deletion.CASCADE, related_name='drop_points', to='netbox_fiber.fiberroute')),
                ('site', models.ForeignKey(blank=True, help_text='NetBox Site (optional if using joint or custom name)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fiber_drop_points', to='dcim.site')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Fiber Drop Point',
                'verbose_name_plural': 'Fiber Drop Points',
                'ordering': ('fiber_route', 'sequence', 'name'),
            },
        ),
    ]
