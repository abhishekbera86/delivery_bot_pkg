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

## Timezone Configuration

### Problem

Even when clocks are synchronized, **different timezones on the NUC and Raspberry Pi can cause confusion**. ROS2 timestamps should be consistent across both systems. **Both systems MUST have the same timezone.**

**Important:** If timezones don't match, even synchronized clocks will display different times, causing timestamp mismatches in ROS2.

### Check Current Timezones

**First, check the timezone on both systems:**

**On NUC (Host Computer):**
```bash
# Check current timezone
timedatectl

# Or check the timezone file directly
cat /etc/timezone

# Check what timezone is displayed in date
date
```

**On Raspberry Pi (TurtleBot 4):**
```bash
# Check current timezone
timedatectl

# Or check the timezone file directly
cat /etc/timezone

# Check what timezone is displayed in date
date
```

**Example output if timezones don't match:**
- NUC: `Time zone: Europe/Luxembourg (CET, +0100)`
- Raspberry Pi: `Time zone: America/Toronto (EST, -0500)`

**This mismatch will cause problems!** You need to set both systems to the same timezone.

### Solution: Set Both Systems to the Same Timezone

You have two options:

#### Option A: Set Both to UTC (Recommended for ROS2)

**Why UTC?** ROS2 timestamps are in UTC internally. Setting both systems to UTC ensures consistent display and avoids confusion.

**On NUC (Host Computer):**
```bash
# Set timezone to UTC
sudo timedatectl set-timezone UTC

# Verify
timedatectl
cat /etc/timezone
date
```

**On Raspberry Pi (TurtleBot 4):**
```bash
# Set timezone to UTC
sudo timedatectl set-timezone UTC

# Verify
timedatectl
cat /etc/timezone
date
```

**Expected output after setting to UTC:**
- Both systems should show UTC in the `date` output
- Example: `Tue Nov  4 07:37:35 UTC 2025` (same UTC time on both)
- `/etc/timezone` should contain `UTC` on both systems

#### Option B: Match NUC's Timezone on Raspberry Pi (Local Timezone)

If you prefer to keep a local timezone, **set the Raspberry Pi to match the NUC's timezone**.

**Step 1: Check NUC's timezone**

**On NUC:**
```bash
# Check current timezone
timedatectl | grep "Time zone"
# Or
cat /etc/timezone
```

**Example:** If NUC shows `Europe/Luxembourg`

**Step 2: Set Raspberry Pi to match NUC's timezone**

**On Raspberry Pi:**
```bash
# Set timezone to match NUC (replace with your NUC's timezone)
sudo timedatectl set-timezone Europe/Luxembourg

# Verify
timedatectl
cat /etc/timezone
date
```

**Step 3: Verify both systems match**

**On both NUC and Raspberry Pi, run:**
```bash
# Should show the same timezone
timedatectl | grep "Time zone"

# Should show the same timezone in file
cat /etc/timezone

# Should show same local time (within seconds)
date
```

**Example: If NUC is set to Europe/Luxembourg:**

**On NUC:**
```bash
sudo timedatectl set-timezone Europe/Luxembourg
```

**On Raspberry Pi:**
```bash
sudo timedatectl set-timezone Europe/Luxembourg
```

**Find available timezones:**
```bash
# List all timezones
timedatectl list-timezones

# Search for specific region
timedatectl list-timezones | grep -i europe
timedatectl list-timezones | grep -i america
timedatectl list-timezones | grep -i luxembourg
```

### Verify Timezone Sync

After setting timezones, verify on both systems:

**On both NUC and Raspberry Pi, run:**
```bash
# Check timezone (should be identical)
timedatectl | grep "Time zone"

# Check timezone file (should be identical)
cat /etc/timezone

# Check date (should show same timezone and same time)
date

# Check UTC timestamp (should be identical on both)
date -u

# Check Unix timestamp (should be within seconds)
date +%s
```

**Expected:**
- Both systems show the **same timezone** in `timedatectl`
- Both `/etc/timezone` files contain the **same timezone**
- `date` shows the **same timezone** and **same time** (within seconds)
- `date -u` shows the **same UTC time** on both
- `date +%s` shows Unix timestamps within seconds of each other

### Common Timezone Mismatch Example

**Problem:** NUC is `Europe/Luxembourg`, Raspberry Pi is `America/Toronto`

**Solution:** Set Raspberry Pi to match NUC

**On Raspberry Pi:**
```bash
# Set to match NUC's timezone
sudo timedatectl set-timezone Europe/Luxembourg

# Verify
cat /etc/timezone
# Should show: Europe/Luxembourg

timedatectl | grep "Time zone"
# Should show: Time zone: Europe/Luxembourg (CET, +0100)
```

**After setting, both systems should show:**
- Same timezone: `Europe/Luxembourg`
- Same `/etc/timezone` file content: `Europe/Luxembourg`
- Same time display (within seconds)

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

## Permanence and Automatic Sync on Boot

### Are Settings Permanent?

**Yes! Both settings are permanent:**

1. **Clock Synchronization (chrony)**: 
   - `sudo systemctl enable chrony` makes chrony start automatically on every boot
   - This is **permanent** - chrony will sync on every boot

2. **Timezone Setting**:
   - `sudo timedatectl set-timezone UTC` modifies `/etc/timezone` and systemd settings
   - This is **permanent** - timezone persists across reboots

### Automatic Sync on Boot

Both methods above enable `chrony` to start on boot, so clocks will automatically synchronize when the Raspberry Pi starts.

### Verify Boot-Time Sync

After reboot, check:
```bash
# On Raspberry Pi
sudo systemctl status chrony
chronyc tracking
```

You should see synchronized status after chrony starts.

### Ensure Permanent Configuration

To ensure everything is set up correctly and persists:

#### Step 1: Verify chrony is Enabled on Boot

**On Raspberry Pi:**
```bash
# Check if chrony is enabled
sudo systemctl is-enabled chrony

# Should output: enabled
# If not, enable it:
sudo systemctl enable chrony

# Verify it will start on boot
sudo systemctl status chrony
```

#### Step 2: Verify Timezone Persists

**On both NUC and Raspberry Pi:**
```bash
# Check current timezone
timedatectl

# Verify timezone file
cat /etc/timezone

# Should show: UTC (or your chosen timezone)
```

#### Step 3: Test After Reboot

To verify everything works after reboot:

1. **Reboot Raspberry Pi:**
   ```bash
   sudo reboot
   ```

2. **After reboot, verify on Raspberry Pi:**
   ```bash
   # Check chrony is running
   sudo systemctl status chrony
   
   # Check sync status
   chronyc tracking
   
   # Check timezone
   timedatectl
   date
   ```

3. **Verify synchronization on both systems:**
   ```bash
   # On both NUC and Raspberry Pi
   date +%s
   ```
   
   Timestamps should be within seconds of each other.

#### Step 4: Handle Large Time Differences on Boot

If the Raspberry Pi clock is too far off when it boots (>1000 seconds), chrony might not sync automatically. To ensure sync happens even with large time differences:

**On Raspberry Pi, edit chrony config:**
```bash
sudo nano /etc/chrony/chrony.conf
```

Add or ensure these lines are present:
```
# Allow large time corrections on startup
makestep 1.0 -1
```

This tells chrony to make a large time step (up to unlimited) on startup if needed.

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

```bash
# Restart chrony
sudo systemctl restart chrony
```

### Making Sync More Aggressive on Boot

If you want chrony to sync more aggressively on boot (useful for Raspberry Pi without RTC):

**On Raspberry Pi, edit chrony config:**
```bash
sudo nano /etc/chrony/chrony.conf
```

Add these lines (if not present):
```
# Allow large time corrections
makestep 1.0 -1

# Sync faster on startup
initstepslew 10 <NTP_SERVER_OR_NUC_IP>
```

Replace `<NTP_SERVER_OR_NUC_IP>` with:
- For Option 1: `0.pool.ntp.org` (or another NTP server)
- For Option 2: Your NUC's IP address

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

```bash
# Restart chrony
sudo systemctl restart chrony
```

### Complete Permanent Setup Checklist

Use this checklist to ensure everything is permanent:

**On Raspberry Pi:**
- [ ] chrony is installed: `dpkg -l | grep chrony`
- [ ] chrony is enabled on boot: `sudo systemctl is-enabled chrony` (should show "enabled")
- [ ] chrony is running: `sudo systemctl status chrony`
- [ ] chrony config has NTP servers configured: `cat /etc/chrony/chrony.conf | grep -E "pool|server"`
- [ ] chrony config has `makestep` for large corrections: `cat /etc/chrony/chrony.conf | grep makestep`
- [ ] Timezone is set: `timedatectl` (should show UTC)
- [ ] Timezone file exists: `cat /etc/timezone` (should show UTC)

**On NUC:**
- [ ] Timezone is set: `timedatectl` (should show UTC)
- [ ] Timezone file exists: `cat /etc/timezone` (should show UTC)

**After Reboot Test:**
- [ ] Reboot Raspberry Pi: `sudo reboot`
- [ ] After reboot, chrony syncs: `chronyc tracking` (should show synchronized)
- [ ] After reboot, timezone persists: `timedatectl` (should show UTC)
- [ ] After reboot, clocks are synced: `date +%s` on both systems (within seconds)

---

## Summary

- **Clock Synchronization**:
  - **Option 1 (Recommended)**: Sync Raspberry Pi to internet NTP servers
  - **Option 2**: Sync Raspberry Pi to NUC's clock (local network)
  - Both methods automatically sync on boot via `chrony` (**permanent**)
  - If time difference is too large, manually set approximate time first
  - **Permanence**: `sudo systemctl enable chrony` makes sync automatic on every boot

- **Timezone Configuration**:
  - **CRITICAL**: Both systems MUST have the same timezone
  - **Recommended**: Set both systems to UTC (`sudo timedatectl set-timezone UTC`)
  - **Alternative**: Match Raspberry Pi timezone to NUC's timezone (e.g., `Europe/Luxembourg`)
  - Check timezones: `cat /etc/timezone` on both systems
  - ROS2 timestamps are in UTC internally, so UTC is recommended
  - **Permanence**: Timezone setting persists across reboots automatically

- **Ensuring Permanent Setup**:
  - Verify chrony is enabled: `sudo systemctl is-enabled chrony` (should show "enabled")
  - Add `makestep 1.0 -1` to chrony config for large time corrections on boot
  - Test after reboot to verify everything persists

- **After Setup**:
  - Restart all ROS2 nodes to clear timestamp caches
  - Verify synchronization with `date +%s` on both systems
  - Verify timezone with `timedatectl` on both systems

