# Manual Fetch Setup Guide

The add-on supports manual fetching of water meter readings on-demand. This is useful when you've just entered new readings in the portal and want to see them in Home Assistant immediately, without waiting for the monthly scheduled update.

## How It Works

The add-on monitors for a trigger file at `/data/manual_fetch`. When this file is created, the add-on:
1. Immediately fetches the latest readings from the portal
2. Updates the Home Assistant sensors
3. Deletes the trigger file
4. Resumes the normal monthly update schedule

## Setup Option 1: Button in Dashboard (Recommended)

This creates a button in your Home Assistant UI that triggers an immediate fetch.

### Step 1: Create a Shell Command

Add this to your `configuration.yaml`:

```yaml
shell_command:
  fetch_water_meters: 'touch /addons/waz-nieplitz-water-meter/data/manual_fetch'
```

**Note:** The exact path may vary depending on your installation:
- Home Assistant OS: `/addons/waz-nieplitz-water-meter/data/manual_fetch`
- Docker: May need to use the container name or volume path
- If unsure, check the add-on logs for the exact path shown at startup

### Step 2: Create a Script

Add this to your `scripts.yaml` (or create via UI: Settings → Automations & Scenes → Scripts):

```yaml
fetch_water_meters:
  alias: Fetch Water Meter Readings
  sequence:
    - service: shell_command.fetch_water_meters
    - delay:
        seconds: 2
    - service: persistent_notification.create
      data:
        title: Water Meters
        message: "Water meter fetch triggered. Check add-on logs for results."
```

### Step 3: Add Button to Dashboard

1. Edit your dashboard
2. Add a new card (Button card)
3. Configure:
   - **Entity:** script.fetch_water_meters
   - **Name:** Fetch Water Meters
   - **Icon:** mdi:water-sync
   - **Tap Action:** Execute

Or add this YAML to your dashboard:

```yaml
type: button
tap_action:
  action: call-service
  service: script.fetch_water_meters
name: Fetch Water Meters
icon: mdi:water-sync
show_state: false
```

## Setup Option 2: Automation After Portal Update

Create an automation that you can manually trigger after entering readings in the portal.

```yaml
automation:
  - alias: Manually Fetch Water Meters
    description: Trigger water meter fetch from portal
    mode: single
    trigger: []
    condition: []
    action:
      - service: shell_command.fetch_water_meters
      - service: notify.persistent_notification
        data:
          title: Water Meters
          message: Fetching latest readings from portal...
```

Then create a button card that triggers this automation.

## Setup Option 3: Direct File Creation (Advanced)

If you have SSH access or use the File Editor add-on:

1. Install Terminal & SSH or Studio Code Server add-on
2. When you want to fetch readings, run:
   ```bash
   touch /addons/waz-nieplitz-water-meter/data/manual_fetch
   ```
3. Check add-on logs to see the fetch in action

## Setup Option 4: Node-RED Flow (If Using Node-RED)

Create a flow with:
1. **Inject node** → triggers manually or on schedule
2. **Exec node** → command: `touch /addons/waz-nieplitz-water-meter/data/manual_fetch`
3. **Notification node** → confirms the action

## Verifying It Works

After triggering a manual fetch:

1. Go to **Settings** → **Add-ons** → **WAZ Nieplitz Water Meter** → **Log**
2. You should see messages like:
   ```
   Manual fetch triggered! Fetching readings immediately...
   Attempting to login to WAZ Nieplitz portal...
   Login successful
   Fetching meter readings...
   Found 2 meter(s)
   Updated sensor sensor.waz_nieplitz_water_main: 484
   Updated sensor sensor.waz_nieplitz_water_garden: 51
   Manual fetch completed successfully
   Manual fetch trigger cleared
   ```

## Troubleshooting

### Shell command not working

If the shell command fails, try these alternative paths:
```yaml
shell_command:
  # Option 1: Direct data path
  fetch_water_meters: 'touch /data/manual_fetch'

  # Option 2: Via addon_configs
  fetch_water_meters: 'touch /config/addons_config/waz-nieplitz-water-meter/manual_fetch'

  # Option 3: Using docker exec (if running in Docker)
  fetch_water_meters: 'docker exec addon_local_waz-nieplitz-water-meter touch /data/manual_fetch'
```

Check the add-on logs at startup - it will show the exact path it's monitoring.

### Button does nothing

1. Check the shell command works by testing in **Developer Tools** → **Services**
2. Call `shell_command.fetch_water_meters` manually
3. Check Home Assistant logs for any errors
4. Verify the path to the data directory is correct

### No notification appears

The notification is optional - check the add-on logs directly to see if the fetch occurred.

## Best Practices

1. **Don't overuse manual fetch**: The portal should not be overwhelmed with requests. Use manual fetch only when needed.
2. **After entering new readings**: This is the perfect time to use manual fetch
3. **Monthly is usually sufficient**: Since readings are typically annual, the monthly automatic update should be adequate for most uses
4. **Check logs**: Always verify successful fetches in the add-on logs

## Alternative: Using a Helper Toggle

You can also create an Input Boolean helper and use an automation to watch for changes:

1. Create helper: **Settings** → **Devices & Services** → **Helpers** → **Toggle**
   - Name: "Fetch Water Meters Trigger"
   - ID: `input_boolean.fetch_water_meters_trigger`

2. Create automation:
```yaml
automation:
  - alias: Water Meter Fetch on Toggle
    trigger:
      - platform: state
        entity_id: input_boolean.fetch_water_meters_trigger
        to: 'on'
    action:
      - service: shell_command.fetch_water_meters
      - delay:
          seconds: 10
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.fetch_water_meters_trigger
      - service: notify.persistent_notification
        data:
          message: Water meter readings fetched!
```

3. Add the toggle to your dashboard - toggling it will trigger a fetch and automatically turn off.
