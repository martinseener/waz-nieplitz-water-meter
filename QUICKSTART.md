# Quick Start Guide

Complete guide to get your WAZ Nieplitz water meters into Home Assistant in 5 minutes.

## What This Does

Automatically fetches your water meter readings from the WAZ Nieplitz portal and adds them to Home Assistant's Energy Dashboard.

## Installation (Choose One)

### Option A: From GitHub (Recommended - Easiest Updates)

**Step 1:** Push to GitHub (one time)
```bash
cd /Users/mseener/Development/local/waz-nieplitz-water-meter
./push_to_github.sh
```

**Step 2:** Add to Home Assistant
1. Open http://homeassistant.local:8123
2. **Settings** → **Add-ons** → **⋮** → **Repositories**
3. Add: `https://github.com/martinseener/waz-nieplitz-water-meter`
4. Find "WAZ Nieplitz Water Meter" → **Install**

**Step 3:** Configure and Start
```yaml
username: your_waz_portal_username
password: your_waz_portal_password
```
Save → Start

### Option B: Direct Installation to Local HA

**Step 1:** Install Samba in HA
- **Settings** → **Add-ons** → Install "Samba share"
- Configure with username/password
- Start it

**Step 2:** Copy Files
```bash
cd /Users/mseener/Development/local/waz-nieplitz-water-meter
./install_to_local_ha.sh  # Option 1 (Samba)
```

**Step 3:** Install in HA
- **Settings** → **Add-ons** → **⋮** → **Check for updates**
- Find "WAZ Nieplitz Water Meter" → Install
- Configure → Start

## Verification

**Check the logs:**
```
Login successful
Found 2 meter(s)
Updated sensor sensor.waz_nieplitz_water_main: 484
Updated sensor sensor.waz_nieplitz_water_garden: 51
```

**Check sensors:**
- Developer Tools → States
- Search: `waz_nieplitz`
- You should see 2 sensors!

## Add to Energy Dashboard

1. **Settings** → **Dashboards** → **Energy**
2. Click "Add Water Source"
3. Select `sensor.waz_nieplitz_water_main`
4. Add another for `sensor.waz_nieplitz_water_garden`
5. Save

Done! Your water consumption is now tracked in the Energy Dashboard.

## Optional Features

### Manual Fetch (Get latest data immediately)

See [MANUAL_FETCH_SETUP.md](MANUAL_FETCH_SETUP.md) for setup.

Quick version:
```yaml
# In configuration.yaml
shell_command:
  fetch_water_meters: 'touch /addons/waz-nieplitz-water-meter/data/manual_fetch'
```

### Historical Readings (Data older than 2 years)

See [HISTORICAL_READINGS.md](HISTORICAL_READINGS.md) for setup.

Quick version:
```yaml
# In configuration.yaml
shell_command:
  add_water_reading: >
    echo '{"action":"add","meter_number":"{{ meter_number }}","date":"{{ date }}","reading":{{ reading }}}'
    > /addons/waz-nieplitz-water-meter/data/historical_command.json
```

## Documentation Overview

| File | What It Covers |
|------|----------------|
| **QUICKSTART.md** | This file - fastest path to installation |
| **GITHUB_INSTALL.md** | GitHub setup and installation |
| **README.md** | Complete add-on documentation |
| **INSTALLATION.md** | All installation methods |
| **TESTING.md** | Test before installing |
| **MANUAL_FETCH_SETUP.md** | Manual update trigger |
| **HISTORICAL_READINGS.md** | Add old meter readings |

## Quick Commands

```bash
# Test the add-on (no HA needed)
./run_tests.sh

# Push to GitHub
./push_to_github.sh

# Install to local HA
./install_to_local_ha.sh

# Check add-on logs (in HA via SSH)
ha addons logs local_waz-nieplitz-water-meter
```

## Troubleshooting

### "Add-on not appearing"
- Wait 30 seconds, refresh
- Check for updates: **⋮** → **Check for updates**

### "Login failed"
- Verify credentials on portal website
- Check username/password in config

### "Sensors not showing"
- Wait for first update cycle
- Check logs for errors
- Go to Developer Tools → States

## Support

- **Documentation**: See .md files in repository
- **Testing**: Run `./run_tests.sh` first
- **Issues**: GitHub issues (after pushing to GitHub)

## Comparison: GitHub vs Local Install

| Feature | GitHub | Local |
|---------|--------|-------|
| **Updates** | Automatic notifications | Manual file copy |
| **Sharing** | Anyone can install | Only you |
| **Backup** | On GitHub | Your responsibility |
| **Installation** | Add URL once | Copy files each time |
| **Best for** | Production use | Testing/Development |

**Recommendation:** Use GitHub for your production Home Assistant, use local install only for testing.

## What Next?

✅ Add-on installed and running
✅ Sensors in Energy Dashboard

Optional enhancements:
- Set up manual fetch trigger
- Add historical readings from previous years
- Create automations based on water usage
- Monitor for unusual consumption patterns

Enjoy tracking your water consumption! 💧📊
