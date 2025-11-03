# Time Synchronization Guide

## Problem

The TurtleBot 4 Raspberry Pi doesn't have a battery-backed real-time clock (RTC). When powered off, the clock resets, causing timestamp mismatches between the Raspberry Pi and the NUC host computer. This leads to:

- Transform timeout errors in Nav2
- Old timestamp errors in collision monitor
- Navigation failures due to timestamp mismatches
- Localization issues

## Solution

Synchronize the Raspberry Pi clock using NTP (Network Time Protocol). This guide provides two options:

1. **Option 1 (Recommended)**: Sync Raspberry Pi to Internet NTP servers
2. **Option 2**: Sync Raspberry Pi to NUC's clock (local network)

---

## Option 1: Sync Raspberry Pi to Internet NTP (Recommended)

This syncs the Pi to internet time servers, which is the most accurate.

### Step 1: Install chrony on Raspberry Pi

```bash
# Update package list
sudo apt update

# Install chrony
sudo apt install -y chrony
```

### Step 2: Configure chrony

```bash
# Edit chrony configuration
sudo nano /etc/chrony/chrony.conf
```

Add or ensure these lines are present (uncomment if commented):
```
pool 0.pool.ntp.org iburst
pool 1.pool.ntp.org iburst
pool 2.pool.ntp.org iburst
pool 3.pool.ntp.org iburst
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

### Step 3: Start and Enable chrony

```bash
# Restart chrony service
sudo systemctl restart chrony

# Enable chrony to start on boot
sudo systemctl enable chrony
```

### Step 4: Verify Synchronization

```bash
# Check synchronization status
chronyc sources -v
```

You should see `^*` next to a time source, indicating it's synchronized.

```bash
# Check current time
date
```

### Step 5: Verify on Both Computers

On both NUC and Raspberry Pi, run:
```bash
date +%s
```

The Unix timestamps should be within seconds of each other (accounting for network delay).

---

## Option 2: Sync Raspberry Pi to NUC (Local Network)

This syncs the Pi to the NUC's clock, useful when internet isn't available or you want local synchronization.

### Step 1: Configure NUC as NTP Server

**On NUC (Host Computer):**

```bash
# 1. Install chrony (if not already installed)
sudo apt update
sudo apt install -y chrony

# 2. Edit chrony configuration
sudo nano /etc/chrony/chrony.conf
```

Add or uncomment this line to allow local network connections:
```
allow 192.168.0.0/16
allow 10.0.0.0/8
```

Also ensure it syncs to internet time servers:
```
pool 0.pool.ntp.org iburst
pool 1.pool.ntp.org iburst
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

```bash
# 3. Restart chrony
sudo systemctl restart chrony

# 4. Enable chrony to start on boot
sudo systemctl enable chrony

# 5. Find NUC's IP address
hostname -I | awk '{print $1}'
```

**Note the IP address** (e.g., `192.168.1.100`).

### Step 2: Configure Raspberry Pi to Sync to NUC

**On Raspberry Pi (TurtleBot4):**

```bash
# 1. Install chrony (if not installed)
sudo apt update
sudo apt install -y chrony

# 2. Edit chrony configuration
sudo nano /etc/chrony/chrony.conf
```

Comment out or remove internet pool lines, replace with:
```
server <NUC_IP_ADDRESS> iburst
```

Replace `<NUC_IP_ADDRESS>` with the NUC's IP from Step 1.

Example:
```
server 192.168.1.100 iburst
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

```bash
# 3. Restart chrony
sudo systemctl restart chrony

# 4. Enable chrony to start on boot
sudo systemctl enable chrony

# 5. Check synchronization
chronyc sources -v
```

You should see your NUC IP with `^*` indicating synchronization.

---

## Troubleshooting

### Clocks Still Not Syncing

If chrony is configured but clocks still aren't synchronized, the time difference may be too large (>1000 seconds). chrony won't sync automatically in this case.

**Fix: Manually set approximate time first**

```bash
# 1. Stop chrony temporarily
sudo systemctl stop chrony

# 2. Get current time from NUC
# On NUC, run: date +%s
# Write down the timestamp (e.g., 1762183834)

# 3. Manually set time on Raspberry Pi
sudo date -s "@TIMESTAMP"
# Replace TIMESTAMP with value from NUC
# Example: sudo date -s "@1762183834"

# 4. Start chrony again
sudo systemctl start chrony

# 5. Force chrony to sync immediately
sudo chrony makestep

# 6. Verify synchronization
chronyc tracking
date +%s
```

**Expected output:**
- `chronyc tracking` should show "Reference time" (not "System clock wrong")
- `date +%s` on Pi should be within 1-2 seconds of NUC's timestamp

### chrony Service Not Running

```bash
# Check status
sudo systemctl status chrony

# If not running, start it
sudo systemctl start chrony

# Enable on boot
sudo systemctl enable chrony
```

### No Internet Connectivity (Option 1)

If internet sync isn't working:
- Check internet connection: `ping -c 3 8.8.8.8`
- Check firewall: `sudo ufw status`
- Use Option 2 (sync to NUC) instead

### Firewall Blocking NTP

If firewall is active and blocking NTP:

```bash
# Check firewall status
sudo ufw status

# Allow NTP traffic
sudo ufw allow 123/udp

# Restart chrony
sudo systemctl restart chrony
```

---

## Verification

After setting up clock synchronization, verify on both computers:

```bash
# Check Unix timestamps (should be within seconds)
date +%s

# Check human-readable time
date

# Check chrony sync status (on Raspberry Pi)
chronyc tracking
```

**Expected:**
- Timestamps should be within 1-2 seconds of each other
- `chronyc tracking` should show synchronized status
- No "System clock wrong" warnings

---

## After Successful Sync

Once clocks are synchronized:

1. **Restart all ROS2 nodes** (to clear timestamp caches)
   - Stop all running nodes (Ctrl+C)
   - Restart robot on Raspberry Pi
   - Restart localization and Nav2 on NUC

2. **Reset initial pose** using the Initial Pose GUI

3. **Try navigation again** - timestamp errors should be resolved!

---

## Automatic Sync on Boot

Both methods above enable `chrony` to start on boot, so clocks will automatically synchronize when the Raspberry Pi starts.

### Verify Boot-Time Sync

After reboot, check:
```bash
# On Raspberry Pi
sudo systemctl status chrony
chronyc tracking
```

You should see synchronized status after chrony starts.

---

## Summary

- **Option 1 (Recommended)**: Sync Raspberry Pi to internet NTP servers
- **Option 2**: Sync Raspberry Pi to NUC's clock (local network)
- Both methods automatically sync on boot via `chrony`
- If time difference is too large, manually set approximate time first
- After sync setup, restart ROS2 nodes to clear timestamp caches

