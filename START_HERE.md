# 🚀 START HERE

Welcome! This guide will get your WAZ Nieplitz water meters into Home Assistant.

## Step 1: Choose Your Installation Method

### ✅ Recommended: GitHub Installation

**Advantages:**
- ✓ Easy updates (automatic notifications in HA)
- ✓ Share with others
- ✓ Professional distribution
- ✓ Automatic backups

**Steps:**
1. Push to GitHub: `./push_to_github.sh`
2. Add repository to Home Assistant
3. Install from add-on store

👉 **[See GITHUB_INSTALL.md](GITHUB_INSTALL.md)** for complete instructions

### 🔧 Alternative: Local Installation

**Best for:**
- Testing before GitHub
- Private use only
- No GitHub account

**Steps:**
1. Install Samba in HA
2. Run: `./install_to_local_ha.sh`
3. Install from local add-ons

👉 **[See LOCAL_HA_INSTALL.md](LOCAL_HA_INSTALL.md)** for complete instructions

## Step 2: Test First (Recommended)

Before installing, verify everything works:

```bash
./run_tests.sh
# Select option 1 for offline tests
# Or option 2 for full tests with your credentials
```

👉 **[See TESTING.md](TESTING.md)** for testing guide

## Quick Start (5 Minutes)

**Absolute fastest path to a working installation:**

```bash
# 1. Push to GitHub
./push_to_github.sh

# 2. In Home Assistant (http://homeassistant.local:8123):
#    - Settings → Add-ons → ⋮ → Repositories
#    - Add: https://github.com/martinseener/waz-nieplitz-water-meter
#    - Install "WAZ Nieplitz Water Meter"
#    - Configure with your credentials
#    - Start the add-on

# 3. Verify sensors:
#    - Developer Tools → States
#    - Search: waz_nieplitz
```

## File Overview

### 📝 Documentation

| File | Purpose |
|------|---------|
| **START_HERE.md** | ⭐ This file - your starting point |
| **QUICKSTART.md** | 5-minute installation guide |
| **GITHUB_INSTALL.md** | GitHub repository setup |
| **README.md** | Complete add-on documentation |
| **INSTALLATION.md** | All installation methods |
| **TESTING.md** | How to test before installing |

### 🔧 Setup Guides

| File | Purpose |
|------|---------|
| **MANUAL_FETCH_SETUP.md** | Set up manual data refresh |
| **HISTORICAL_READINGS.md** | Add readings older than 2 years |
| **LOCAL_HA_INSTALL.md** | Install to local VirtualBox HA |
| **INSTALL_QUICKSTART.md** | Quick local install guide |

### 🛠️ Scripts

| Script | Purpose |
|--------|---------|
| `push_to_github.sh` | Push add-on to GitHub |
| `install_to_local_ha.sh` | Install to local HA |
| `run_tests.sh` | Test the add-on |
| `test_addon.py` | Full test suite |

### ⚙️ Core Files

| File | Purpose |
|------|---------|
| `config.json` | Add-on configuration |
| `run.py` | Main add-on code |
| `Dockerfile` | Container definition |
| `repository.json` | GitHub repository metadata |
| `LICENSE` | MIT License |

## What You Need

- ✓ WAZ Nieplitz portal account (username/password)
- ✓ Home Assistant instance (your local VirtualBox instance at homeassistant.local)
- ✓ GitHub account (martinseener/waz-nieplitz-water-meter)
- ✓ Your meter numbers (will be detected automatically)

## What This Add-on Does

1. **Connects** to kundenportal.waz-nieplitz.de monthly
2. **Fetches** your water meter readings
3. **Creates** Home Assistant sensors:
   - `sensor.waz_nieplitz_water_main`
   - `sensor.waz_nieplitz_water_garden`
4. **Updates** Energy Dashboard with water consumption
5. **Stores** historical readings (optional)

## Decision Tree

```
Do you want to test first?
├─ Yes → Run ./run_tests.sh → See TESTING.md
└─ No → Continue below

Where will you use this?
├─ Production HA → Use GitHub installation
│  └─ Run ./push_to_github.sh → See GITHUB_INSTALL.md
│
└─ Local test HA → Use local installation
   └─ Run ./install_to_local_ha.sh → See LOCAL_HA_INSTALL.md

After installation:
├─ Add to Energy Dashboard
├─ (Optional) Set up manual fetch → MANUAL_FETCH_SETUP.md
└─ (Optional) Add historical data → HISTORICAL_READINGS.md
```

## Next Steps

Pick one:

### Path A: GitHub Installation (Recommended)
1. ✅ Read [QUICKSTART.md](QUICKSTART.md)
2. ✅ Run `./push_to_github.sh`
3. ✅ Follow [GITHUB_INSTALL.md](GITHUB_INSTALL.md)
4. ✅ Install in Home Assistant
5. ✅ Configure and start

### Path B: Local Testing First
1. ✅ Read [QUICKSTART_TESTING.md](QUICKSTART_TESTING.md)
2. ✅ Run `./run_tests.sh`
3. ✅ Verify tests pass
4. ✅ Then choose Path A or C

### Path C: Local Installation Only
1. ✅ Read [INSTALL_QUICKSTART.md](INSTALL_QUICKSTART.md)
2. ✅ Run `./install_to_local_ha.sh`
3. ✅ Install in Home Assistant
4. ✅ Configure and start

## Common Questions

**Q: Should I use GitHub or local installation?**
A: GitHub for production, local for testing. GitHub gives you automatic updates.

**Q: Do I need to test first?**
A: Recommended but not required. Tests verify everything works without touching HA.

**Q: How do I update the add-on later?**
A: If installed from GitHub, you'll get update notifications in HA automatically.

**Q: Can I add old meter readings?**
A: Yes! See [HISTORICAL_READINGS.md](HISTORICAL_READINGS.md) for instructions.

**Q: How often does it update?**
A: Every 30 days by default. You can trigger manual updates anytime.

## Support

- 📖 **Documentation**: All .md files in this repository
- 🧪 **Testing**: `./run_tests.sh` before installing
- 🐛 **Issues**: GitHub issues (after pushing to GitHub)
- 📝 **Logs**: Check add-on logs in Home Assistant

## Repository Structure

```
waz-nieplitz-water-meter/
├── START_HERE.md ⭐ You are here
├── QUICKSTART.md
├── GITHUB_INSTALL.md
├── README.md
│
├── config.json (Add-on metadata)
├── run.py (Main code - 630 lines)
├── Dockerfile
├── repository.json
│
├── Documentation/
│   ├── INSTALLATION.md
│   ├── TESTING.md
│   ├── MANUAL_FETCH_SETUP.md
│   └── HISTORICAL_READINGS.md
│
└── Scripts/
    ├── push_to_github.sh
    ├── install_to_local_ha.sh
    ├── run_tests.sh
    └── test_addon.py
```

## Your Next Action

**Choose ONE:**

```bash
# A) Test first (recommended)
./run_tests.sh

# B) Push to GitHub and install
./push_to_github.sh

# C) Install to local HA directly
./install_to_local_ha.sh
```

Then follow the on-screen instructions!

---

**Ready?** Pick a path above and let's get started! 🚀

For detailed instructions, see:
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute guide
- **[GITHUB_INSTALL.md](GITHUB_INSTALL.md)** - GitHub setup
- **[README.md](README.md)** - Full documentation
