# WAZ Nieplitz Water Meter Add-on

This Home Assistant add-on fetches water meter readings from the WAZ Nieplitz customer portal (kundenportal.waz-nieplitz.de) and makes them available as sensors in Home Assistant. The sensors can be integrated into the Home Assistant Energy Dashboard for water consumption monitoring.

## Features

- Automatic login to WAZ Nieplitz customer portal
- Fetches meter readings for multiple water meters
- Supports at least 2 meters (e.g., main and garden meters)
- Creates Home Assistant sensors with water consumption data
- Compatible with Home Assistant Energy Dashboard
- Configurable update interval (default: monthly)
- Manual fetch trigger for immediate updates
- Historical readings support (beyond 2-year portal window)
- Automatic retry on connection failures
- Comprehensive test suite for safe evaluation

## Testing Before Installation

**Want to test before installing in production?** See [TESTING.md](TESTING.md) for complete testing instructions.

Quick test (no Home Assistant required):
```bash
cd waz-nieplitz-water-meter
./run_tests.sh
# Select option 1 for offline tests
```

## Installation

### Via GitHub Repository (Recommended)

1. In Home Assistant: **Settings** → **Add-ons** → **Add-on Store**
2. Click **⋮** (three dots) → **Repositories**
3. Add: `https://github.com/martinseener/waz-nieplitz-water-meter`
4. Find "WAZ Nieplitz Water Meter" in the store
5. Click **Install**

See [GITHUB_INSTALL.md](GITHUB_INSTALL.md) for detailed GitHub installation.

### Manual Installation

1. Copy the add-on folder to your Home Assistant `/addons` directory
2. Reload the add-on store
3. Install "WAZ Nieplitz Water Meter"

See [INSTALLATION.md](INSTALLATION.md) for manual installation methods.

## Configuration

Configure the add-on through the Home Assistant UI:

```yaml
username: "your_username"
password: "your_password"
update_interval: 2592000
main_meter_name: "Water Meter Main"
garden_meter_name: "Water Meter Garden"
```

### Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `username` | Yes | - | Your WAZ Nieplitz portal username |
| `password` | Yes | - | Your WAZ Nieplitz portal password |
| `update_interval` | No | 2592000 | Update interval in seconds (default: 30 days, minimum: 1 day / 86400 seconds) |
| `main_meter_name` | No | "Water Meter Main" | Friendly name for the main water meter |
| `garden_meter_name` | No | "Water Meter Garden" | Friendly name for the garden water meter |

### Important Notes About Update Interval

- **Default is 30 days** (2592000 seconds): Since water meter readings are typically only updated annually, frequent polling is unnecessary
- **Minimum is 1 day** (86400 seconds): Please do not reduce the interval below this to avoid overwhelming the portal servers
- **Respect the server**: The portal is not designed for frequent automated access
- **Use manual fetch instead**: If you need immediate updates after entering new readings, use the manual fetch feature (see below)

## Sensors

The add-on creates the following sensors:

- `sensor.waz_nieplitz_water_main` - Main water meter reading
- `sensor.waz_nieplitz_water_garden` - Garden water meter reading

### Sensor Attributes

Each sensor includes the following attributes:

- `unit_of_measurement`: m³
- `device_class`: water
- `state_class`: total_increasing (for Energy Dashboard integration)
- `meter_number`: Physical meter number
- `reading_type`: Type of reading (e.g., "Kundenangabe, Jahresabrechnung")
- `consumption`: Recent consumption in m³
- `reading_date`: Date when the reading was taken
- `reference_date`: Reference date for the reading (Stichtag)

## Manual Fetch Feature

While the add-on automatically fetches readings on a monthly schedule, you can trigger an immediate fetch at any time. This is useful when you've just entered new readings in the portal and want to see them in Home Assistant immediately.

### Quick Setup

1. Add to your `configuration.yaml`:
   ```yaml
   shell_command:
     fetch_water_meters: 'touch /addons/waz-nieplitz-water-meter/data/manual_fetch'
   ```

2. Restart Home Assistant to load the shell command

3. Create a script (Settings → Automations & Scenes → Scripts):
   ```yaml
   fetch_water_meters:
     alias: Fetch Water Meter Readings
     sequence:
       - service: shell_command.fetch_water_meters
       - service: persistent_notification.create
         data:
           title: Water Meters
           message: "Fetching latest readings from portal..."
   ```

4. Add a button to your dashboard:
   ```yaml
   type: button
   tap_action:
     action: call-service
     service: script.fetch_water_meters
   name: Fetch Water Meters
   icon: mdi:water-sync
   ```

When you click the button, the add-on will immediately fetch the latest readings and update the sensors, then return to the normal monthly schedule.

**For detailed setup instructions and alternative methods**, see [MANUAL_FETCH_SETUP.md](MANUAL_FETCH_SETUP.md)

## Historical Readings

The WAZ Nieplitz portal only provides readings from the last 2 years. This add-on allows you to manually add historical readings from previous years to maintain a complete water usage history.

### Quick Start

1. Add shell command to `configuration.yaml`:
   ```yaml
   shell_command:
     add_water_reading: >
       echo '{"action":"add","meter_number":"{{ meter_number }}","date":"{{ date }}","reading":{{ reading }},"consumption":{{ consumption }}}'
       > /addons/waz-nieplitz-water-meter/data/historical_command.json
   ```

2. Create a script to add readings easily:
   ```yaml
   add_main_water_reading:
     alias: Add Main Water Meter Reading
     fields:
       date:
         description: Reading date (YYYY-MM-DD)
         example: "2020-12-31"
       reading:
         description: Meter reading in m³
         example: 100
     sequence:
       - service: shell_command.add_water_reading
         data:
           meter_number: "15093668"  # Your main meter number
           date: "{{ date }}"
           reading: "{{ reading }}"
           consumption: 0
   ```

3. View historical readings in sensor attributes:
   - Go to Developer Tools → States
   - Find `sensor.waz_nieplitz_water_main`
   - Check `historical_readings` attribute

### Features

- Store unlimited historical readings beyond the 2-year portal window
- Readings persisted across restarts in `/data/historical_readings.json`
- Never overwritten by portal data
- Included in sensor attributes for reference
- Support for both date formats: YYYY-MM-DD and DD.MM.YYYY

**For complete documentation with examples**, see [HISTORICAL_READINGS.md](HISTORICAL_READINGS.md)

## Integration with Energy Dashboard

To add the water meter sensors to your Energy Dashboard:

1. Go to Settings → Dashboards → Energy
2. Click "Add Water Source"
3. Select `sensor.waz_nieplitz_water_main` for your main water meter
4. Select `sensor.waz_nieplitz_water_garden` for your garden water meter (if applicable)
5. Click "Save"

The sensors are configured with `state_class: total_increasing` which makes them compatible with the Energy Dashboard.

## Troubleshooting

### Add-on won't start

- Check your username and password in the configuration
- Ensure your credentials work on the portal website
- Check the add-on logs for error messages

### No sensors appearing

- Wait for the first update cycle to complete (check `update_interval`)
- Verify the add-on is running without errors in the logs
- Check if you can manually access https://kundenportal.waz-nieplitz.de/ablesungen with your credentials

### Incorrect meter identification

The add-on automatically identifies meters by sorting them alphabetically. The first meter becomes "main" and the second becomes "garden". If this doesn't match your setup, you can identify sensors by their meter number in the attributes.

## Privacy & Security

- Your credentials are stored securely in Home Assistant's configuration
- The add-on only communicates with kundenportal.waz-nieplitz.de
- No data is sent to third parties
- Login sessions are maintained only during data fetching

## Support

For issues and feature requests, please check the add-on logs first and report any problems with:
- Add-on version
- Home Assistant version
- Error messages from logs
- Description of the issue

## License

This add-on is provided as-is for personal use with the WAZ Nieplitz customer portal.
