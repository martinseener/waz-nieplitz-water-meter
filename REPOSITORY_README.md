# WAZ Nieplitz Water Meter - Home Assistant Add-on

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

Home Assistant add-on to fetch water meter readings from the WAZ Nieplitz customer portal (kundenportal.waz-nieplitz.de) and integrate them into Home Assistant's Energy Dashboard.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## About

This add-on automatically:
- Logs into the WAZ Nieplitz customer portal
- Fetches water meter readings from multiple meters
- Creates Home Assistant sensors with consumption data
- Integrates with the Energy Dashboard
- Supports historical readings beyond the 2-year portal window
- Provides manual fetch trigger for immediate updates

Perfect for customers of WAZ Nieplitz who want to track their water consumption in Home Assistant!

## Features

- 🔄 **Automatic Updates** - Monthly scheduled fetching (configurable)
- 💧 **Multiple Meters** - Supports main and garden water meters
- 📊 **Energy Dashboard** - Direct integration with HA Energy Dashboard
- 🕒 **Historical Data** - Add readings from previous years manually
- ⚡ **Manual Fetch** - Trigger immediate updates after entering new readings
- 🔒 **Secure** - Credentials stored safely in Home Assistant
- 🏗️ **Multi-Architecture** - Supports all major platforms

## Installation

### Method 1: Add Repository to Home Assistant (Recommended)

1. In Home Assistant, navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **⋮** (three dots) in the top right corner
3. Select **Repositories**
4. Add this repository URL:
   ```
   https://github.com/martinseener/waz-nieplitz-water-meter
   ```
5. Click **Add**
6. Refresh the add-on store page
7. Find "**WAZ Nieplitz Water Meter**" in the list
8. Click on it and then click **Install**

### Method 2: Manual Installation

See [INSTALLATION.md](INSTALLATION.md) for manual installation instructions.

## Configuration

Configure the add-on in Home Assistant:

```yaml
username: your_portal_username
password: your_portal_password
update_interval: 2592000  # 30 days in seconds
main_meter_name: Water Meter Main
garden_meter_name: Water Meter Garden
```

**Important Notes:**
- Default update interval is 30 days (appropriate for annual meter readings)
- Minimum interval is 1 day to avoid overwhelming the portal servers
- Use manual fetch for immediate updates when needed

## Documentation

- **[README.md](README.md)** - Complete add-on documentation
- **[INSTALLATION.md](INSTALLATION.md)** - Installation guide
- **[MANUAL_FETCH_SETUP.md](MANUAL_FETCH_SETUP.md)** - Manual fetch trigger setup
- **[HISTORICAL_READINGS.md](HISTORICAL_READINGS.md)** - Historical data guide
- **[TESTING.md](TESTING.md)** - Testing before installation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## Quick Start

1. Install the add-on from the repository
2. Configure with your portal credentials
3. Start the add-on
4. Check logs for successful connection
5. Find sensors in Developer Tools → States
6. Add sensors to Energy Dashboard

## Support

If you encounter issues:

1. Check the [Troubleshooting](README.md#troubleshooting) section
2. Review add-on logs for error messages
3. Test your credentials on the portal website
4. Run the test suite (see [TESTING.md](TESTING.md))
5. Open an issue on GitHub with logs and details

## Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Testing

The add-on includes a comprehensive test suite. Test before installing:

```bash
cd waz-nieplitz-water-meter
./run_tests.sh
```

See [TESTING.md](TESTING.md) for detailed testing instructions.

## License

This project is provided as-is for personal use with the WAZ Nieplitz customer portal.

## Disclaimer

This is an unofficial add-on and is not affiliated with or endorsed by WAZ Nieplitz. Use at your own risk.

---

## Screenshots

### Add-on Configuration
![Configuration](docs/images/config.png)

### Energy Dashboard Integration
![Energy Dashboard](docs/images/energy-dashboard.png)

### Sensor Attributes
![Sensor Attributes](docs/images/sensor-attributes.png)

---

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[license-shield]: https://img.shields.io/github/license/martinseener/waz-nieplitz-water-meter.svg
[releases-shield]: https://img.shields.io/github/release/martinseener/waz-nieplitz-water-meter.svg
[releases]: https://github.com/martinseener/waz-nieplitz-water-meter/releases
