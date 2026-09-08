# NetBox Fiber Plugin (`netbox-fiber`)

[![NetBox Version](https://img.shields.io/badge/NetBox-v4.0%2B%20%7C%20v4.5.9%2B-blue.svg)](https://netbox.dev)
[![Author](https://img.shields.io/badge/Author-Nepal%20Telecom-red.svg)](https://ntc.net.np)

A comprehensive NetBox plugin developed for **Nepal Telecom** to model, track, and visualize optical fiber infrastructure, vendors, route segments, core allocations, and intermediate drop points.

---

## Key Features

- **Vendor Management**:
  - Track optical fiber contractors and vendors (e.g. *Konnect Solutions*, *Nepal Telecom*).
  - Track vendor contact persons, phone numbers, emails, and notes.
  - View vendor-aggregated infrastructure statistics (total route count, total distance in KM, and installed cores).

- **Route Management**:
  - Model fiber routes with Starting Point Site, End Point Site, Total Length in KM, and Total Fiber Cores (e.g. 6, 12, 24, 48, 96).
  - Support for cable installation types (ADSS, Underground/Duct, Direct Buried/Armored, Aerial, Submarine, etc.).
  - Direct integration with NetBox `dcim.Site` objects with fallback custom site/joint naming.
  - Dedicated core termination tracking at the **Starting Point** and **End Point** (e.g. Cores `1-6`, Cores `1-2`).
  - Quick multi-line drop point entry to easily create multiple drop points in one submission.

- **Intermediate Drop Points**:
  - Add multiple drop points along a route in ordered sequence.
  - Track drop locations (NetBox Site, Joint Closure, ODF, Manhole/Chamber).
  - Assign specific cores dropped at each site (e.g. Cores `3, 4` dropped at *Thameldanda*).
  - Track distance markers in KM from the starting point.

- **Dedicated Vendor Explorer (`/plugins/fiber/vendor-view/`)**:
  - Separate interactive page to browse fiber cables by vendor selection dropdown.
  - Real-time KPI statistics per vendor (Total Routes, Total Distance KM, Total Cores, Total Drop Points).
  - Visual route path flow (`Start Site [Cores]` ➔ `Drop Points [Cores]` ➔ `End Site [Cores]`).

- **NetBox-Style Topology View (`/plugins/fiber/topology/`)**:
  - Interactive network graph of sites, joints, and fiber cables.
  - Filterable by Vendor, Route, and Site search.
  - Interactive controls: Fit to screen, Zoom in/out, and Physics toggle.
  - Click any site node or fiber link to inspect dropped cores, distance, and cable details in real time.

- **Linear Schematic Core Diagram**:
  - Visual core allocation diagram for every route matching field engineering schematics.
  - Displays each individual fiber core (Core 1, Core 2, ..., Core N) running from start to end with visual breakouts tapping off at intermediate drop points.

- **REST API Support**:
  - Full REST API endpoints for automated integrations:
    - `/api/plugins/fiber/vendors/`
    - `/api/plugins/fiber/routes/`
    - `/api/plugins/fiber/drop-points/`

---

## Compatibility

- **NetBox Versions**: NetBox **v4.0+**, **v4.5.9+**, and newer.
- **Python**: Python 3.10+

---

## Installation

### 1. Install Package
In your NetBox environment:

```bash
pip install -e /path/to/netbox-fiber
```
Or add to your Docker `plugin_requirements.txt`:
```text
/opt/netbox/plugins/netbox-fiber
```

### 2. Enable in NetBox Configuration
In your `configuration.py` (or `plugins.py`):

```python
PLUGINS = [
    'netbox_fiber',
]

PLUGINS_CONFIG = {
    'netbox_fiber': {},
}
```

### 3. Run Migrations & Collect Static Files
```bash
python manage.py migrate netbox_fiber
python manage.py collectstatic --no-input
```

### 4. Restart NetBox Service
```bash
sudo systemctl restart netbox netbox-rq
# Or for Docker:
# docker compose restart netbox
```

---

## Example Usage: ADSS Fiber Route

Following Nepal Telecom route configurations:
- **Vendor**: `Konnect Solutions`
- **Route Name**: `Galchhi - Gajuri`
- **Total Length**: `14.855 KM`
- **Total Cores**: `6 Cores`
- **Starting Point**: `Galchhi` (Cores dropped: `1-6`)
- **Intermediate Drop Point**: `Thameldanda` (Cores dropped: `3, 4`)
- **Intermediate Drop Point**: `Adamghat` (Cores dropped: `5, 6`)
- **End Point**: `Gajuri` (Cores dropped: `1, 2`)

---

## Author & Maintainer

- **Organization**: Nepal Telecom
- **Email**: info@ntc.net.np
- **Website**: [https://www.ntc.net.np](https://www.ntc.net.np)
