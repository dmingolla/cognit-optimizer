# Cognit Optimizer

A decoupled daemon that optimizes device-to-cluster assignments using Mixed-Integer Linear Programming (MILP) to minimize energy consumption and carbon footprint.

## Debian Package

### Build

```bash
cd /path/to/cognit-optimizer
ln -sf packaging/debian debian
dpkg-buildpackage -us -uc -b
```

Output: `../opennebula-cognit-optimizer_1.0.0-1_all.deb`

### Install

**Requires:** `opennebula-cognit-frontend` must be installed first.

```bash
dpkg -i opennebula-cognit-optimizer_1.0.0-1_all.deb
```

Service starts automatically as daemon (runs every 300s).

### Verify

```bash
systemctl status opennebula-cognit-optimizer
journalctl -u opennebula-cognit-optimizer -f
```

### Remove

```bash
dpkg --purge opennebula-cognit-optimizer
```

## Overview

The optimizer periodically:
1. Reads device assignments from the local SQLite database (device_id, cluster_id, app_req_id, estimated_load)
2. Fetches each device's application requirements from OpenNebula using the app_req_id
3. Filters feasible clusters based on device constraints (flavour, confidentiality, providers, geolocation)
4. Runs MILP optimization to find optimal cluster assignments that minimize energy/carbon
5. Scales clusters in parallel based on optimizer output via cluster scaling endpoints
6. Updates the cluster_id in the database for devices assigned to successfully scaled clusters

## Database Integration

**Local Database (`device_cluster_assignment.db`):**
- Stores device-to-cluster assignments with application requirements
- Shared between `cognit-frontend` and `cognit-optimizer`
- Schema: `device_id`, `cluster_id`, `flavour`, `app_req_id`, `app_req_json`, `estimated_load`, `last_seen`

**cognit-frontend interaction:**
- When a device requests a cluster, cognit-frontend queries OpenNebula for feasible clusters
- Selects the closest cluster and stores the assignment in the database
- The optimizer later re-evaluates these assignments globally to optimize across all devices

**cognit-optimizer interaction:**
- Reads all device assignments from the database
- Uses `app_req_id` to fetch fresh requirements from OpenNebula
- Optimizes assignments considering all devices simultaneously
- Scales clusters in parallel via cluster scaling endpoints
- Updates `cluster_id` in the database incrementally as clusters finish scaling

## Dependencies

**Required:**
- `cognit-frontend` repository at `/home/ubuntu/cognit-frontend/` (imports `db_manager.py` and `opennebula.py`)
- Database file at `/home/ubuntu/cognit-frontend/database/device_cluster_assignment.db`
- OpenNebula API accessible at `http://localhost:2633/RPC2`
- OpenNebula credentials in `~/.one/one_auth` or `/var/lib/one/.one/one_auth`

## Setup

1. **Ensure cognit-frontend repository exists:**
   ```bash
   ls /home/ubuntu/cognit-frontend/src/db_manager.py
   ls /home/ubuntu/cognit-frontend/src/opennebula.py
   ```

2. **Create virtual environment:**
   ```bash
   cd cognit-optimizer
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

**Run single optimization cycle:**
```bash
python main.py
```

**Run as daemon (continuous mode):**
```bash
# Use default interval (300 seconds)
python main.py --daemon

# Use custom interval
python main.py --daemon --interval 60
```