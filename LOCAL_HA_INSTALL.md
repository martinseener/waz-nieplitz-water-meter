# Installing to Local Home Assistant (VirtualBox)

Guide for installing the WAZ Nieplitz Water Meter add-on to your local Home Assistant instance.

## Prerequisites

- Home Assistant running at http://homeassistant.local:8123
- User: martin / Password: martin
- VirtualBox VM running Home Assistant OS

## Installation Methods

### Method 1: Using Samba Share (Easiest)

#### Step 1: Install Samba Add-on

1. Open Home Assistant: http://homeassistant.local:8123
2. Login as martin
3. Go to **Settings** → **Add-ons** → **Add-on Store**
4. Search for "Samba share"
5. Click **Install**
6. Once installed:
   - Go to **Configuration** tab
   - Set username: `martin`
   - Set password: `martin`
   - Click **Save**
7. Go to **Info** tab
8. Click **Start**
9. Enable **Start on boot**

#### Step 2: Connect to Samba Share

On macOS (your machine):

1. Open Finder
2. Press `Cmd+K` or Go → Connect to Server
3. Enter: `smb://homeassistant.local`
4. Click **Connect**
5. Username: `martin`
6. Password: `martin`

You should now see the Home Assistant folders.

#### Step 3: Create Add-on Directory

In the Samba share:

1. Navigate to the `addons` folder (create it if it doesn't exist at root level)
2. Create a new folder: `waz-nieplitz-water-meter`

#### Step 4: Copy Add-on Files

Copy these files from your local `waz-nieplitz-water-meter` folder to the Samba share:

**Required files:**
- `config.json`
- `run.py`
- `Dockerfile`
- `build.yaml`
- `requirements.txt`
- `README.md`
- `CHANGELOG.md`

**Optional but recommended:**
- `INSTALLATION.md`
- `MANUAL_FETCH_SETUP.md`
- `HISTORICAL_READINGS.md`
- `ICON.md`

**Do NOT copy:**
- `test_addon.py`
- `test_config.json`
- `docker-compose.test.yml`
- `run_tests.sh`
- `TESTING.md`
- `Ablesungen.html`

You can do this via Finder drag-and-drop or terminal:

```bash
# From your local machine
cd /Users/mseener/Development/local

# Copy only production files (excluding test files)
rsync -av \
  --exclude 'test_*.py' \
  --exclude 'test_*.json' \
  --exclude 'docker-compose.test.yml' \
  --exclude 'run_tests.sh' \
  --exclude 'TESTING.md' \
  --exclude 'QUICKSTART_TESTING.md' \
  --exclude '*.html' \
  --exclude 'test_data' \
  --exclude '.git*' \
  waz-nieplitz-water-meter/ \
  /Volumes/addons/waz-nieplitz-water-meter/
```

Or manually in Finder:
1. Open two Finder windows
2. Left: `/Users/mseener/Development/local/waz-nieplitz-water-meter`
3. Right: Samba share → `addons` → `waz-nieplitz-water-meter`
4. Copy the required files listed above

#### Step 5: Install the Add-on in Home Assistant

1. Go to **Settings** → **Add-ons**
2. Click the **⋮** (three dots) in top right
3. Click **Check for updates** (this reloads the add-on store)
4. You should see **WAZ Nieplitz Water Meter** under "Local add-ons"
5. Click on it
6. Click **Install**
7. Wait for installation to complete (this builds the Docker container)

#### Step 6: Configure the Add-on

1. After installation, go to the **Configuration** tab
2. Enter your settings:
   ```yaml
   username: your_portal_username
   password: your_portal_password
   update_interval: 2592000
   main_meter_name: Water Meter Main
   garden_meter_name: Water Meter Garden
   ```
3. Click **Save**

#### Step 7: Start the Add-on

1. Go to the **Info** tab
2. Enable **Start on boot** (recommended)
3. Enable **Watchdog** (auto-restart on crash)
4. Click **Start**

#### Step 8: Check Logs

1. Go to the **Log** tab
2. You should see:
   ```
   Starting WAZ Nieplitz Water Meter Add-on
   Update interval: 2592000 seconds (30.0 days)
   Performing initial meter reading fetch...
   Attempting to login to WAZ Nieplitz portal...
   Login successful
   Fetching meter readings...
   Found 2 meter(s)
   Updated sensor sensor.waz_nieplitz_water_main: 484
   Updated sensor sensor.waz_nieplitz_water_garden: 51
   ```

### Method 2: Using Terminal & SSH Add-on

If Samba doesn't work, use SSH:

#### Step 1: Install Terminal & SSH

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Search for "Terminal & SSH"
3. Install it
4. Go to **Configuration** tab
5. Set a password (e.g., `martin`)
6. Click **Save**
7. Start the add-on

#### Step 2: Access Terminal

1. Click **Open Web UI** in the Terminal & SSH add-on
2. You should see a terminal prompt

#### Step 3: Create Add-on Directory

In the terminal:

```bash
# Create addons directory
mkdir -p /addons/waz-nieplitz-water-meter

# Navigate to it
cd /addons/waz-nieplitz-water-meter
```

#### Step 4: Create Files

You have two options:

**Option A: Use SCP from your Mac**

On your Mac terminal:

```bash
# Copy all files via SCP
scp -r /Users/mseener/Development/local/waz-nieplitz-water-meter/* \
  root@homeassistant.local:/addons/waz-nieplitz-water-meter/
```

When prompted for password, enter the SSH add-on password you set.

**Option B: Create files manually in HA terminal**

In the HA Terminal & SSH web UI:

```bash
cd /addons/waz-nieplitz-water-meter

# Create each file using vi or nano
# For example:
nano config.json
# Paste the content from your local config.json
# Save with Ctrl+X, Y, Enter

nano run.py
# Paste the content from your local run.py
# Save

# Repeat for other required files
```

#### Step 5: Set Permissions

```bash
chmod 755 /addons/waz-nieplitz-water-meter
chmod 644 /addons/waz-nieplitz-water-meter/*
chmod 755 /addons/waz-nieplitz-water-meter/run.py
```

#### Step 6: Reload and Install

1. Go to **Settings** → **Add-ons**
2. Click **⋮** → **Check for updates**
3. Install and configure as described in Method 1, Steps 5-8

### Method 3: Using File Editor Add-on

#### Step 1: Install File Editor

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Search for "File editor"
3. Install and start it

#### Step 2: Enable Advanced Mode

1. Click on your profile (bottom left)
2. Enable **Advanced Mode**

#### Step 3: Configure File Editor

1. Go back to File Editor add-on
2. Click **Configuration**
3. Enable access to `/addons`
4. Save and restart the add-on

#### Step 4: Create Add-on Files

1. Open File Editor Web UI
2. Create `/addons/waz-nieplitz-water-meter/` folder
3. Create each file by copying content from your local files
4. Save each file

Then follow Method 1, Steps 5-8.

## Verification

### Check if Add-on Appears

After copying files:

1. Go to **Settings** → **Add-ons**
2. Click **⋮** → **Check for updates**
3. Look for "WAZ Nieplitz Water Meter" under "Local add-ons"

If it doesn't appear:
- Check files are in `/addons/waz-nieplitz-water-meter/`
- Ensure `config.json` is valid JSON
- Check logs in **Settings** → **System** → **Logs**

### Check Sensors After Start

1. Go to **Developer Tools** → **States**
2. Search for `waz_nieplitz`
3. You should see:
   - `sensor.waz_nieplitz_water_main`
   - `sensor.waz_nieplitz_water_garden`

Click on a sensor to see all attributes.

## Testing the Add-on

### Test Manual Fetch

While logged into Terminal & SSH:

```bash
# Trigger manual fetch
touch /addons/waz-nieplitz-water-meter/data/manual_fetch

# Watch the logs
ha addons logs local_waz-nieplitz-water-meter
```

Or use Home Assistant:
1. Create shell command in `configuration.yaml`:
   ```yaml
   shell_command:
     fetch_water_meters: 'touch /addons/waz-nieplitz-water-meter/data/manual_fetch'
   ```
2. Restart Home Assistant
3. Call the service in Developer Tools → Services

### Test Historical Readings

Create a script in `scripts.yaml`:

```yaml
test_add_historical_reading:
  alias: Test Add Historical Reading
  sequence:
    - service: shell_command.add_water_reading
      data:
        meter_number: "15093668"
        date: "2020-12-31"
        reading: 100
        consumption: 150
```

(After setting up the shell command as described in HISTORICAL_READINGS.md)

## Troubleshooting

### Add-on doesn't appear in store

**Check:**
1. Files are in correct location: `/addons/waz-nieplitz-water-meter/`
2. `config.json` exists and is valid JSON
3. Reload add-on store (⋮ → Check for updates)

**Verify via SSH:**
```bash
ls -la /addons/waz-nieplitz-water-meter/
cat /addons/waz-nieplitz-water-meter/config.json
```

### Add-on won't start

**Check logs:**
1. Go to Add-on → Log tab
2. Look for error messages

**Common issues:**
- Invalid credentials
- Python dependencies failed to install
- Network connectivity to portal

### Sensors not appearing

**Check:**
1. Add-on is running (green "STARTED")
2. Logs show "Updated sensor..." messages
3. Wait for first update cycle (check logs)
4. Go to Developer Tools → States and search for `waz_nieplitz`

### Can't connect to Samba

**Try:**
1. Check Samba add-on is running
2. Try IP address instead: `smb://192.168.x.x` (find IP in HA under Settings → System → Network)
3. Check firewall settings on your Mac
4. Use SSH method instead

## File Structure on Home Assistant

After installation:

```
/addons/waz-nieplitz-water-meter/
├── config.json                  - Add-on configuration
├── run.py                       - Main script
├── Dockerfile                   - Container definition
├── build.yaml                   - Build config
├── requirements.txt             - Python dependencies
├── README.md                    - Documentation
├── CHANGELOG.md                 - Version history
├── INSTALLATION.md              - Install guide
├── MANUAL_FETCH_SETUP.md        - Manual fetch guide
├── HISTORICAL_READINGS.md       - Historical data guide
└── data/                        - Created at runtime
    ├── historical_readings.json - Your historical data
    └── manual_fetch            - Trigger file (temporary)
```

## Next Steps

Once the add-on is running:

1. **Add to Energy Dashboard**
   - Settings → Dashboards → Energy
   - Add Water Source
   - Select your sensors

2. **Set up manual fetch** (optional)
   - Follow MANUAL_FETCH_SETUP.md
   - Create shell commands and scripts

3. **Add historical readings** (optional)
   - Follow HISTORICAL_READINGS.md
   - Add readings from previous years

4. **Monitor and verify**
   - Check logs regularly
   - Verify readings match portal
   - Test manual fetch works

## Quick Commands Reference

```bash
# View add-on logs
ha addons logs local_waz-nieplitz-water-meter

# Restart add-on
ha addons restart local_waz-nieplitz-water-meter

# View historical readings
cat /addons/waz-nieplitz-water-meter/data/historical_readings.json

# Trigger manual fetch
touch /addons/waz-nieplitz-water-meter/data/manual_fetch

# Check if add-on is running
ha addons info local_waz-nieplitz-water-meter
```

## Support

If you encounter issues:
1. Check the add-on logs first
2. Verify credentials work on the portal website
3. Review TESTING.md for testing procedures
4. Check TROUBLESHOOTING sections in other docs
