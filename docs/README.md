# Documentation

This directory contains detailed step-by-step guides for the Delivery Bot project.

## Available Guides

### [MAPPING_AND_LOCATION_TAGGING.md](MAPPING_AND_LOCATION_TAGGING.md)
**Unified guide for creating SLAM maps and tagging locations**

Complete guide for:
- Starting unified mapping and tagging system (single launch command!)
- Using the unified GUI to tag locations during mapping
- Auto-updating JSON filename when map name is entered
- Saving maps directly from the GUI
- Exiting cleanly

**Key Features:**
- **Single Launch Command** - Everything starts with one command: `ros2 launch launch/mapping_with_tagging.launch.py`
- **Unified GUI** - One interface handles mapping, location tagging, and map saving
- **Auto JSON Filename** - When you enter map name, JSON filename automatically matches (e.g., `office_map.yaml` → `office_map.json`)
- **Map Saving from GUI** - Save maps directly from the interface
- **Tag During SLAM** - No initial pose needed! Tag locations while mapping

**When to use:** First time setup, creating a new map and tagging delivery locations.

---

### [DELIVERY_BOT_GUIDE.md](DELIVERY_BOT_GUIDE.md)
**Guide for using the unified delivery bot GUI for navigation**

Complete guide for:
- Starting unified delivery bot GUI (single launch command!)
- Selecting map from dropdown
- Loading map and starting localization automatically
- Setting initial pose using tagged locations or manual entry
- Navigating to destinations
- Exiting cleanly (all nodes stopped automatically)

**Key Features:**
- **Single Launch Command** - Everything starts with one command: `ros2 launch launch/delivery_bot.launch.py`
- **Unified GUI** - One interface handles map selection, localization, initial pose, and navigation
- **Automatic Node Management** - All nodes (localization, Nav2, navigator) started/stopped automatically
- **Map-Aware Location Loading** - Shows only locations associated with selected map
- **Clean Exit** - All nodes stopped cleanly with one button

**When to use:** Daily operation for autonomous navigation.

---

### [TIME_SYNCHRONIZATION.md](TIME_SYNCHRONIZATION.md)
**Setting up clock synchronization (CRITICAL)**

Essential guide for:
- Why clock synchronization is critical
- Setting up NTP synchronization
- Verifying synchronization
- Troubleshooting sync issues

**When to use:** Initial setup, before running any delivery bot operations.

**⚠️ IMPORTANT:** Clock synchronization is critical - without it, navigation will fail.

---

## Quick Reference

| Guide | Purpose |
|-------|---------|
| MAPPING_AND_LOCATION_TAGGING | Create maps and tag locations (unified GUI - one command!) |
| DELIVERY_BOT_GUIDE | Use delivery bot for navigation (unified GUI - one command!) |
| TIME_SYNCHRONIZATION | Set up clock sync (critical) |

---

## Getting Started

1. **Install dependencies:** See `../INSTALLATION.md`
2. **Set up clock synchronization:** Follow `TIME_SYNCHRONIZATION.md` (CRITICAL!)
3. **Create map and tag locations:** Follow `MAPPING_AND_LOCATION_TAGGING.md` (single launch command!)
4. **Use delivery bot:** Follow `DELIVERY_BOT_GUIDE.md`

---

## Related Documentation

- **[../README.md](../README.md)** - Project overview
- **[../ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick reference
- **[../INSTALLATION.md](../INSTALLATION.md)** - Installation instructions

---

## Workflow Overview

### Workflow 1: Map Creation with Location Tagging (First Time)

**Single unified launch:**

1. Start robot hardware (TurtleBot 4 Pi)
2. Start unified system: `ros2 launch launch/mapping_with_tagging.launch.py` (Host NUC)
3. Configure JSON filename in GUI (optional)
4. Drive robot and tag locations as you map
5. Save map from GUI when complete
6. Exit when done

**Result:**
- Map saved to: `~/delivery_bot_pkg/data/maps/{map_name}.yaml`
- Locations saved to: `~/delivery_bot_pkg/data/locations/{map_name}.json` (auto-matched filename)

**See:** `MAPPING_AND_LOCATION_TAGGING.md` for complete guide

### Workflow 2: Delivery Bot Application (Daily Use)

**Single unified launch - one GUI handles everything!**

1. Start robot hardware (TurtleBot 4 Pi)
2. Launch unified delivery bot GUI: `ros2 launch launch/delivery_bot.launch.py` (Host NUC)
3. Select map from dropdown
4. Click "Load Map and Start Localization" - GUI automatically:
   - Loads the selected map
   - Starts localization (AMCL)
   - Shows initial pose interface
5. Set initial pose (use tagged location or manual entry)
6. Select location and navigate - GUI automatically:
   - Starts Nav2 navigation stack
   - Starts delivery navigator
   - Shows only locations for selected map
7. Click "Exit" when done - All nodes stopped automatically

**See:** `DELIVERY_BOT_GUIDE.md` for complete guide
