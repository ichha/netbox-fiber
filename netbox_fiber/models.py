from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


def parse_core_string(core_str):
    """
    Parses a string representing core numbers or ranges (e.g. '1, 2, 3-5, 8')
    into a sorted list of integer core numbers.
    """
    if not core_str:
        return []
    cores = set()
    parts = [p.strip() for p in str(core_str).replace(';', ',').split(',') if p.strip()]
    for part in parts:
        if '-' in part:
            sub = part.split('-')
            if len(sub) == 2:
                try:
                    start = int(sub[0].strip())
                    end = int(sub[1].strip())
                    if start <= end:
                        cores.update(range(start, end + 1))
                    else:
                        cores.update(range(end, start + 1))
                except ValueError:
                    pass
        else:
            try:
                cores.add(int(part))
            except ValueError:
                pass
    return sorted(list(cores))


class FiberVendor(NetBoxModel):
    """
    Represents an optical fiber vendor, contractor, or provider (e.g., Konnect Solutions, Nepal Telecom).
    """
    name = models.CharField(max_length=100, unique=True, help_text="Vendor / Provider Name")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly slug")
    contact_name = models.CharField(max_length=100, blank=True, help_text="Primary Contact Person")
    contact_phone = models.CharField(max_length=50, blank=True, help_text="Contact Phone Number")
    contact_email = models.EmailField(blank=True, help_text="Contact Email Address")
    description = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Fiber Vendor'
        verbose_name_plural = 'Fiber Vendors'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_fiber:fibervendor', args=[self.pk])

    @property
    def total_routes_count(self):
        return self.fiber_routes.count()

    @property
    def total_distance_km(self):
        total = sum((r.total_length_km or 0) for r in self.fiber_routes.all())
        return round(float(total), 3)


class FiberRoute(NetBoxModel):
    """
    Represents an optical fiber route / cable bundle running between a Starting Point Site
    and an End Point Site with multiple intermediate Drop Points.
    """
    CABLE_TYPE_CHOICES = [
        ('adss', 'ADSS (All-Dielectric Self-Supporting)'),
        ('underground', 'Underground / Duct'),
        ('armored', 'Direct Buried / Armored'),
        ('aerial', 'Aerial / Figure-8'),
        ('submarine', 'Submarine / Underwater'),
        ('indoor', 'Indoor / Riser'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('planned', 'Planned'),
        ('maintenance', 'Under Maintenance'),
        ('decommissioned', 'Decommissioned'),
        ('damaged', 'Damaged / Cut'),
    ]

    name = models.CharField(
        max_length=150, 
        unique=True, 
        help_text="Route Name (e.g. 'Galchhi - Gajuri', 'Galchhi - Tarukaghat - Trishuli')"
    )
    vendor = models.ForeignKey(
        to='netbox_fiber.FiberVendor',
        on_delete=models.PROTECT,
        related_name='fiber_routes',
        help_text="Fiber Vendor or Provider"
    )
    cable_type = models.CharField(
        max_length=50,
        choices=CABLE_TYPE_CHOICES,
        default='adss',
        help_text="Cable installation type"
    )
    total_length_km = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Total Length (KM)",
        help_text="Total length of route in kilometers (e.g. 14.855)"
    )
    total_cores = models.PositiveIntegerField(
        default=6,
        verbose_name="Total Cores",
        help_text="Total fiber cores in the cable (e.g. 6, 12, 24, 48, 96)"
    )

    # Starting Point
    start_site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fiber_routes_starting',
        help_text="Starting NetBox Site (optional if using custom name)"
    )
    start_site_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Starting Point Site / Location Name (e.g. 'Galchhi')"
    )
    start_cores_dropped = models.CharField(
        max_length=255,
        blank=True,
        help_text="Cores terminated / dropped at Starting Point (e.g. '1-6' or '1, 2, 3, 4, 5, 6')"
    )

    # End Point
    end_site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fiber_routes_ending',
        help_text="End NetBox Site (optional if using custom name)"
    )
    end_site_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="End Point Site / Location Name (e.g. 'Gajuri')"
    )
    end_cores_dropped = models.CharField(
        max_length=255,
        blank=True,
        help_text="Cores terminated / dropped at End Point (e.g. '1, 2' or '1-2')"
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Operational status of the route"
    )
    description = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

    clone_fields = [
        'vendor', 'cable_type', 'total_cores', 'status'
    ]

    class Meta:
        ordering = ('name',)
        verbose_name = 'Fiber Route'
        verbose_name_plural = 'Fiber Routes'

    def __str__(self):
        return f"{self.name} ({self.total_cores} Cores, {self.total_length_km} KM)"

    def get_absolute_url(self):
        return reverse('plugins:netbox_fiber:fiberroute', args=[self.pk])

    @property
    def start_point_obj(self):
        return self.drop_points.filter(point_type='start').first()

    @property
    def end_point_obj(self):
        return self.drop_points.filter(point_type='end').first()

    @property
    def start_point_display(self):
        sp = self.start_point_obj
        if sp:
            return sp.site_display
        if self.start_site:
            return self.start_site.name
        return self.start_site_name or 'Starting Point'

    @property
    def end_point_display(self):
        ep = self.end_point_obj
        if ep:
            return ep.site_display
        if self.end_site:
            return self.end_site.name
        return self.end_site_name or 'End Point'

    @property
    def parsed_start_cores(self):
        sp = self.start_point_obj
        if sp:
            return sp.parsed_dropped_cores
        return parse_core_string(self.start_cores_dropped)

    @property
    def parsed_end_cores(self):
        ep = self.end_point_obj
        if ep:
            return ep.parsed_dropped_cores
        return parse_core_string(self.end_cores_dropped)

    def get_ordered_drop_points(self):
        # Return intermediate drop points (excluding start and end points if specified)
        intermediate = self.drop_points.exclude(point_type__in=['start', 'end']).order_by('sequence', 'id')
        if intermediate.exists():
            return intermediate
        return self.drop_points.all().order_by('sequence', 'id')

    def get_all_points(self):
        return self.drop_points.all().order_by('sequence', 'id')

    def get_core_map(self):
        """
        Builds a comprehensive core-by-core mapping across Start, Intermediate Drop Points, and End Point.
        Returns a list of dicts for each core from 1 to total_cores.
        """
        drop_points = list(self.get_ordered_drop_points())
        start_cores = set(self.parsed_start_cores)
        end_cores = set(self.parsed_end_cores)

        # Pre-parse drop point cores
        dp_parsed = []
        for dp in drop_points:
            dp_parsed.append({
                'point': dp,
                'name': dp.site_display,
                'cores': set(dp.parsed_dropped_cores)
            })

        core_map = []
        for c in range(1, self.total_cores + 1):
            dropped_at = []
            if c in start_cores:
                dropped_at.append({'type': 'start', 'name': self.start_point_display, 'role': 'Start Site Termination'})
            for item in dp_parsed:
                if c in item['cores']:
                    dropped_at.append({'type': 'drop', 'name': item['name'], 'role': f"Dropped at {item['name']}"})
            if c in end_cores:
                dropped_at.append({'type': 'end', 'name': self.end_point_display, 'role': 'End Site Termination'})

            if not dropped_at:
                status_label = 'Pass-through / Dark'
                color = '#6c757d'
            elif len(dropped_at) == 1 and dropped_at[0]['type'] == 'start':
                status_label = f"Originated at {self.start_point_display} (In Transit)"
                color = '#0d6efd'
            elif any(d['type'] == 'drop' for d in dropped_at):
                drop_names = [d['name'] for d in dropped_at if d['type'] == 'drop']
                status_label = f"Dropped at {', '.join(drop_names)}"
                color = '#198754'
            elif any(d['type'] == 'end' for d in dropped_at):
                status_label = f"Thru to {self.end_point_display}"
                color = '#0dcaf0'
            else:
                status_label = 'Active'
                color = '#20c997'

            core_map.append({
                'core_number': c,
                'dropped_at': dropped_at,
                'status_label': status_label,
                'color': color,
                'is_start_dropped': c in start_cores,
                'is_end_dropped': c in end_cores,
            })

        return core_map


class FiberDropPoint(NetBoxModel):
    """
    Represents an intermediate drop point, splice enclosure, joint closure, or site along a fiber route
    where specific cores are dropped or spliced.
    """
    POINT_TYPE_CHOICES = [
        ('start', 'Starting Point'),
        ('drop', 'Intermediate Drop Point'),
        ('end', 'End Point'),
    ]

    fiber_route = models.ForeignKey(
        to='netbox_fiber.FiberRoute',
        on_delete=models.CASCADE,
        related_name='drop_points',
        help_text="Associated Fiber Route"
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fiber_drop_points',
        help_text="NetBox Site (optional if using joint or custom name)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Drop Point / Site / Joint Name (e.g. 'Thameldanda', 'Taruka_Joint', 'Adamghat')"
    )
    point_type = models.CharField(
        max_length=50,
        choices=POINT_TYPE_CHOICES,
        default='drop',
        help_text="Type of point along the route"
    )
    sequence = models.PositiveIntegerField(
        default=1,
        help_text="Sequence order along the route (e.g. 1, 2, 3...)"
    )
    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Distance marker in KM from route starting point (optional)"
    )
    dropped_cores = models.CharField(
        max_length=255,
        blank=True,
        help_text="Cores dropped / spliced at this point (e.g. '3, 4' or '3-4')"
    )
    passed_cores = models.CharField(
        max_length=255,
        blank=True,
        help_text="Cores passing through without termination (optional, e.g. '1, 2, 5, 6')"
    )
    description = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ('fiber_route', 'sequence', 'name')
        verbose_name = 'Fiber Drop Point'
        verbose_name_plural = 'Fiber Drop Points'

    def __str__(self):
        return f"{self.name} ({self.fiber_route.name} - Cores: {self.dropped_cores})"

    def get_absolute_url(self):
        return reverse('plugins:netbox_fiber:fiberdroppoint', args=[self.pk])

    @property
    def site_display(self):
        if self.site:
            return self.site.name
        return self.name or f"Drop Point #{self.sequence}"

    @property
    def parsed_dropped_cores(self):
        return parse_core_string(self.dropped_cores)

    @property
    def parsed_passed_cores(self):
        return parse_core_string(self.passed_cores)
