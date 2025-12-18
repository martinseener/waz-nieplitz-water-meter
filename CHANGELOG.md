# Changelog

All notable changes to this project will be documented in this file.

## [1.2.4] - 2025-12-17

### Fixed
- **Critical:** Corrected login URL
  - Changed LOGIN_URL from `{BASE_URL}/login` to just `{BASE_URL}`
  - Login form is at https://kundenportal.waz-nieplitz.de/ (root), not /login
  - Previous URL was returning 404

## [1.2.3] - 2025-12-17

### Fixed
- **Critical:** Added required s6-overlay v3 compatibility fixes
  - Added `CMD [ "/run.sh" ]` to Dockerfile (required for s6-overlay v3)
  - Added `"init": false` to config.json (disables Docker's init, allows s6-overlay as PID 1)
  - These changes are required for Home Assistant base images updated in May 2022

### Technical Details
This resolves the "s6-overlay-suexec: fatal: can only run as pid 1" error that occurs
with s6-overlay v3. The error happened because:
1. Missing CMD prevented Docker from knowing what to execute
2. Missing "init": false allowed Docker's default init to claim PID 1, blocking s6-overlay

Based on official Home Assistant add-on documentation and working examples from
the home-assistant/addons repository.

## [1.2.2] - 2025-12-17

### Fixed
- **Critical:** Simplified add-on structure to fix persistent s6-overlay error
  - Removed complex rootfs/services.d structure
  - Added simple run.sh wrapper script
  - Reverted to copying files to root (/)
  - Removed unnecessary apk packages from Dockerfile

### Changed
- Simplified Dockerfile significantly
- Using run.sh as entry wrapper instead of direct CMD
- Cleaner, more maintainable structure

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
