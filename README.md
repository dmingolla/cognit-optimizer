# Cognit Optimizer

A decoupled daemon that optimizes device-to-cluster assignments using Mixed-Integer Linear Programming (MILP) to minimize energy consumption and carbon footprint.

## Overview

The optimizer:
1. Reads device assignments from the shared SQLite database
2. Fetches the devices application requirements from OpenNebula
3. Filters feasible clusters based on device constraints (flavour, confidentiality, providers, geolocation)
4. Runs MILP optimization to find optimal cluster assignments
5. Updates the database with new assignments

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure OpenNebula credentials:**
   - Requires `~/.one/one_auth` file with OpenNebula credentials
   - Or `/var/lib/one/.one/one_auth` for system-wide access