# Installation Guide

## Method 1: Local Add-on Installation

This is the recommended method for a custom add-on.

### Step 1: Copy Add-on to Home Assistant

Copy the entire `waz-nieplitz-water-meter` folder to your Home Assistant addons directory:

```
/addons/waz-nieplitz-water-meter/
```

If you're using Home Assistant OS:
1. Access your Home Assistant via SSH or File Editor add-on
2. Create the `/addons` directory if it doesn't exist
3. Copy all files from `waz-nieplitz-water-meter` into `/addons/waz-nieplitz-water-meter/`

If you're using a Samba share:
1. Connect to your Home Assistant Samba share
2. Navigate to the `addons` folder (create it if needed)
3. Copy the `waz-nieplitz-water-meter` folder there

### Step 2: Reload Add-on Store

1. Go to **Settings** → **Add-ons**
2. Click the three dots menu (⋮) in the top right
3. Click **Check for updates** or reload the page
4. You should now see "WAZ Nieplitz Water Meter" in the add-on store under "Local add-ons"

### Step 3: Install the Add-on

1. Click on "WAZ Nieplitz Water Meter"
2. Click **Install**
3. Wait for the installation to complete

### Step 4: Configure the Add-on

1. Go to the **Configuration** tab
2. Enter your credentials:
   ```yaml
   username: your_portal_username
   password: your_portal_password
   update_interval: 3600
   main_meter_name: Water Meter Main
   garden_meter_name: Water Meter Garden
   ```
3. Click **Save**

### Step 5: Start the Add-on

1. Go to the **Info** tab
2. Enable **Start on boot** (optional but recommended)
3. Enable **Watchdog** (optional, auto-restarts on crash)
4. Click **Start**

### Step 6: Check the Logs

1. Go to the **Log** tab
2. Verify the add-on is running correctly
3. You should see messages like:
   ```
   Starting WAZ Nieplitz Water Meter Add-on
   Attempting to login to WAZ Nieplitz portal...
   Login successful
   Fetching meter readings...
   Found 2 meter(s)
   Updated sensor sensor.waz_nieplitz_water_main: 484
   Updated sensor sensor.waz_nieplitz_water_garden: 51
   ```

## Method 2: Git Repository Installation

If you want to manage the add-on via Git:

### Step 1: Create a Git Repository

1. Create a new repository (e.g., on GitHub, GitLab)
2. Push the `waz-nieplitz-water-meter` folder contents to the repository

### Step 2: Add Repository to Home Assistant

1. Go to **Settings** → **Add-ons**
2. Click the three dots menu (⋮) in the top right
3. Click **Repositories**
4. Add your repository URL
5. Click **Add**

### Step 3: Install the Add-on

Follow steps 3-6 from Method 1 above.

## Verifying Installation

### Check Sensors

1. Go to **Developer Tools** → **States**
2. Search for `sensor.waz_nieplitz_water`
3. You should see:
   - `sensor.waz_nieplitz_water_main`
   - `sensor.waz_nieplitz_water_garden`

### Check Attributes

Click on a sensor to see its attributes:
- `meter_number`: Your meter's number
- `reading_date`: When the reading was taken
- `consumption`: Recent consumption
- `state_class`: Should be "total_increasing"

### Add to Energy Dashboard

1. Go to **Settings** → **Dashboards** → **Energy**
2. Under "Water consumption", click **Add Water Source**
3. Select your water meter sensors
4. Save and wait for data to accumulate

## Troubleshooting

### Add-on Not Appearing

- Ensure all files are in `/addons/waz-nieplitz-water-meter/`
- Check that `config.json` is valid JSON
- Reload the add-on store
- Restart Home Assistant if needed

### Login Failures

- Verify credentials on the portal website first
- Check the portal isn't under maintenance
- Review add-on logs for specific error messages

### Sensors Not Creating

- Wait for first update cycle to complete
- Check add-on is running (not in error state)
- Verify logs show "Updated sensor..." messages
- Check Home Assistant has API access enabled

## File Structure

Your final directory should look like:

```
/addons/waz-nieplitz-water-meter/
├── config.json
├── Dockerfile
├── build.yaml
├── run.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── INSTALLATION.md
├── ICON.md
└── .gitignore
```

## Next Steps

Once installed and running:
1. Monitor the add-on for a few update cycles
2. Verify sensors are updating correctly
3. Add sensors to your Energy Dashboard
4. Create automations or dashboards with the water data
5. Optionally adjust `update_interval` based on your needs
