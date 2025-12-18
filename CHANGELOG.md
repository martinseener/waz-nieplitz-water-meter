# Changelog

All notable changes to this project will be documented in this file.

## [1.2.1] - 2025-12-17

### Fixed
- **Critical:** Fixed s6-overlay compatibility issue
  - Removed CMD override from Dockerfile that caused "can only run as pid 1" error
  - Added proper s6 service structure with rootfs/etc/services.d/
  - Add-on now starts correctly in Home Assistant

### Changed
- Moved run.py to /app/ directory
- Added s6 run and finish scripts for proper service management

## [1.2.0] - 2025-12-17

### Added
- **Historical readings support** - Manually add water meter readings from previous years beyond the 2-year portal window
- `HistoricalReadingsManager` class for managing historical data
- File-based command interface for adding/deleting historical readings via `/data/historical_command.json`
- Historical readings stored persistently in `/data/historical_readings.json`
- Sensor attributes now include `historical_readings` and `historical_count`
- Support for both date formats: YYYY-MM-DD and DD.MM.YYYY
- Shell command examples for easy integration
- Complete documentation in HISTORICAL_READINGS.md

### Features
- Add unlimited historical readings per meter
- Delete specific historical readings
- Historical data persisted across restarts
- Never overwritten by portal data
- Automatic processing of commands every 60 seconds
- Validation of date formats and required fields

## [1.1.0] - 2025-12-17

### Changed
- **Default update interval changed to 30 days** (2592000 seconds) - more appropriate for annual water meter readings
- **Minimum update interval increased to 1 day** (86400 seconds) - prevents overwhelming the portal servers
- Updated configuration schema to reflect new limits

### Added
- **Manual fetch feature** - trigger immediate readings fetch without waiting for scheduled update
- File-based trigger mechanism (`/data/manual_fetch`) for on-demand updates
- Manual fetch resets the scheduled update timer
- Improved logging with update interval displayed in days
- Documentation for manual fetch setup (MANUAL_FETCH_SETUP.md)
- Dashboard button examples for manual fetch
- Shell command and script examples for easy integration
- Multiple setup options (button, automation, toggle, Node-RED)

### Improved
- Better server-friendly defaults to avoid unnecessary polling
- Clear warnings about respecting server resources
- More detailed configuration documentation

## [1.0.0] - 2025-12-17

### Added
- Initial release
- Login functionality for WAZ Nieplitz customer portal
- Automatic fetching of water meter readings
- Support for multiple water meters (main and garden)
- Home Assistant sensor integration
- Energy Dashboard compatibility with `state_class: total_increasing`
- Configurable update interval
- Automatic retry on connection failures
- Comprehensive error logging
- Multi-architecture support (armhf, armv7, aarch64, amd64, i386)
