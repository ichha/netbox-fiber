from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_fiber', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fiberdroppoint',
            options={
                'ordering': ('fiber_route', 'sequence', 'distance_km', 'name'),
                'verbose_name': 'Fiber Drop Point',
                'verbose_name_plural': 'Fiber Drop Points',
            },
        ),
        migrations.AlterField(
            model_name='fiberdroppoint',
            name='dropped_cores',
            field=models.CharField(blank=True, help_text="Cores dropped / spliced at this point (e.g. '3, 4' or '3-4')", max_length=255),
        ),
        migrations.AlterField(
            model_name='fiberdroppoint',
            name='point_type',
            field=models.CharField(default='drop', help_text='Type of point along the route', max_length=50),
        ),
    ]
