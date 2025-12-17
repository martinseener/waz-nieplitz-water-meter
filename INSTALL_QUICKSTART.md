# Quick Install to Local Home Assistant

Installing the add-on to your local HA instance at http://homeassistant.local:8123

## Fastest Method (2 minutes)

### Step 1: Install Samba Add-on in Home Assistant

1. Open http://homeassistant.local:8123
2. Login as **martin** / **martin**
3. Go to **Settings** → **Add-ons** → **Add-on Store**
4. Search for "**Samba share**"
5. Click **Install**
6. After installation:
   - Go to **Configuration** tab
   - Username: `martin`
   - Password: `martin`
   - Click **Save**
7. Go to **Info** tab → Click **Start**
8. Enable **Start on boot**

### Step 2: Run Installation Script

On your Mac terminal:

```bash
cd /Users/mseener/Development/local/waz-nieplitz-water-meter
./install_to_local_ha.sh
```

Choose **Option 1** (Samba)

The script will:
- Connect to your HA Samba share
- Copy all necessary files
- Give you next steps

### Step 3: Install in Home Assistant

1. Go back to http://homeassistant.local:8123
2. Go to **Settings** → **Add-ons**
3. Click **⋮** (three dots) in top right
4. Click **Check for updates**
5. You should see **WAZ Nieplitz Water Meter** under "Local add-ons"
6. Click on it
7. Click **Install** (wait 1-2 minutes for build)

### Step 4: Configure

1. Go to **Configuration** tab
2. Enter:
   ```yaml
   username: your_waz_portal_username
   password: your_waz_portal_password
   update_interval: 2592000
   main_meter_name: Water Meter Main
   garden_meter_name: Water Meter Garden
   ```
3. Click **Save**

### Step 5: Start

1. Go to **Info** tab
2. Enable **Start on boot**
3. Enable **Watchdog**
4. Click **Start**

### Step 6: Verify

1. Go to **Log** tab
2. Look for:
   ```
   Starting WAZ Nieplitz Water Meter Add-on
   Login successful
   Found 2 meter(s)
   Updated sensor sensor.waz_nieplitz_water_main: XXX
   Updated sensor sensor.waz_nieplitz_water_garden: XXX
   ```

3. Go to **Developer Tools** → **States**
4. Search for `waz_nieplitz`
5. You should see your two sensors!

## Alternative: Manual Copy via Samba

If the script doesn't work:

1. In Finder, press **Cmd+K**
2. Enter: `smb://homeassistant.local`
3. Connect with username `martin` and password `martin`
4. Navigate to `addons` folder
5. Create folder: `waz-nieplitz-water-meter`
6. Copy these files from your local folder:
   - `config.json`
   - `run.py`
   - `Dockerfile`
   - `build.yaml`
   - `requirements.txt`
   - `README.md`
   - `CHANGELOG.md`
   - All `*.md` files (except `TESTING.md` and test files)

Then follow Steps 3-6 above.

## Alternative: SSH Method

If Samba doesn't work:

### Install Terminal & SSH in HA

1. **Settings** → **Add-ons** → **Add-on Store**
2. Search "Terminal & SSH"
3. Install and configure with password
4. Start the add-on

### Copy Files via Script

```bash
cd /Users/mseener/Development/local/waz-nieplitz-water-meter
./install_to_local_ha.sh
```

Choose **Option 2** (SCP/SSH)

Then follow Steps 3-6 from the main method.

## What Next?

Once installed and running:

✅ **Add to Energy Dashboard**
   - Settings → Dashboards → Energy
   - Add Water Source → Select sensors

✅ **Set up Manual Fetch** (optional)
   - See [MANUAL_FETCH_SETUP.md](MANUAL_FETCH_SETUP.md)

✅ **Add Historical Readings** (optional)
   - See [HISTORICAL_READINGS.md](HISTORICAL_READINGS.md)

## Troubleshooting

### Add-on doesn't appear after "Check for updates"

**Solution:**
1. Check files are in `/addons/waz-nieplitz-water-meter/` on HA
2. Verify via Terminal & SSH: `ls -la /addons/waz-nieplitz-water-meter/`
3. Check `config.json` is valid: `cat /addons/waz-nieplitz-water-meter/config.json`

### Can't connect to Samba

**Solutions:**
- Try IP address instead: `smb://192.168.x.x` (find IP in HA Settings → System → Network)
- Check Samba add-on is running
- Use SSH method instead

### Add-on won't start

**Check:**
1. Look at logs in the add-on
2. Verify credentials work on the portal website
3. Check network connectivity from HA to portal

### Sensors don't appear

**Wait and check:**
1. Give it 1-2 minutes after start
2. Check logs show "Updated sensor..." messages
3. Refresh Developer Tools → States page
4. Search for `sensor.waz_nieplitz_water_main`

## Complete Documentation

See [LOCAL_HA_INSTALL.md](LOCAL_HA_INSTALL.md) for detailed instructions and all methods.
