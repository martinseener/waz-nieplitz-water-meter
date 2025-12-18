# Changelog

All notable changes to this project will be documented in this file.

## [1.5.1] - 2025-12-18

### Fixed
- **Statistics import "Invalid source" error**
  - Changed source from 'recorder' to 'waz_nieplitz' (custom integration name)
  - External statistics require a custom source identifier, not 'recorder'

- **Web interface routes returning 404 through ingress**
  - Changed all fetch() calls from absolute paths (`/config`) to relative paths (`config`)
  - Fixes meter dropdown not loading when accessed through HA ingress proxy
  - Fixes status and historical readings not loading

### Technical
- For external statistics, source must be a custom integration/add-on name
- Ingress proxy requires relative URLs for proper routing
- All JavaScript fetch calls now use relative paths

## [1.5.0] - 2025-12-18

### Changed
- **Statistics import now uses WebSocket API instead of REST API**
  - No longer requires Spook or other custom integrations
  - Native Home Assistant WebSocket API for recorder/import_statistics
  - More reliable and follows HA's recommended approach
  - Uses `recorder/import_statistics` WebSocket command directly

### Fixed
- **Flask web interface JSON response issues**
  - Completely disabled werkzeug logging that was interfering with HTTP responses
  - Added threaded mode to Flask for better concurrency
  - Fixed "unexpected character" JSON parse errors in browser
  - Meter dropdown should now populate correctly

### Added
- websocket-client library for WebSocket communication with HA Core

### Technical
- WebSocket connects to `ws://supervisor/core/websocket`
- Authenticates using Supervisor API token
- Sends `recorder/import_statistics` command with metadata and stats
- External statistics use `:` delimiter in statistic_id (e.g., `sensor:waz_nieplitz_water_main`)

## [1.4.4] - 2025-12-18

### Fixed
- **Statistics import 400 Bad Request error**
  - Replaced deprecated `has_mean` boolean with new `mean_type` integer parameter (0 = no mean)
  - Changed `statistic_id` format from `sensor.xxx` to `sensor:xxx` for external statistics
  - External statistics use `:` delimiter instead of `.` per HA API specification
  - Fixes compatibility with latest Home Assistant recorder API changes

### Technical
- Based on HA Developer Blog (Oct 2025) API changes
- `mean_type` replaces deprecated `has_mean` flag (0=no mean, 1=arithmetic, 2=circular)
- External statistics require different ID format than entity-based statistics
- See: https://developers.home-assistant.io/blog/2025/10/16/recorder-statistics-api-changes/
- See: https://data.home-assistant.io/docs/statistics/

## [1.4.3] - 2025-12-18

### Fixed
- **HA 2025.11 API compatibility**
  - Added required `unit_class` field (set to None for water meters)
  - Fixes 400 Bad Request errors introduced in Home Assistant Core 2025.11
  - Updated to comply with October 2025 recorder statistics API changes

### Technical
- Implemented breaking changes from HA Developer Blog (Oct 2025)
- See: https://developers.home-assistant.io/blog/2025/10/16/recorder-statistics-api-changes/
- Required fields: unit_class (None), has_mean (False), has_sum (True)
- Stat entries: only 'start' and 'sum' fields (removed 'state')

## [1.4.2] - 2025-12-18

### Fixed
- **Statistics format for has_sum sensors**
  - Removed 'state' field from stat entries (only use 'sum' for cumulative sensors)
  - 'state' field is for mean statistics, not sum statistics
  - Stat entries now only contain 'start' and 'sum' fields

### Improved
- **Verbose logging for debugging**
  - Logs complete service_data being sent to HA API
  - Shows first and last stat entries
  - Helps diagnose API format issues

## [1.4.1] - 2025-12-18

### Fixed
- **Statistics import 400 error**
  - Added required "source": "recorder" field to service call
  - Added timezone information to all timestamps (UTC)
  - Fixed timestamp formatting for HA's statistics API
  - Enhanced error logging with JSON error details
  - Added debug logging for sample stat entries

### Technical
- Timestamps now include timezone info (required by HA)
- Service data now includes all required fields per HA API spec
- Better error messages showing exact API response

## [1.4.0] - 2025-12-18

### Added
- **🎉 Energy Dashboard Historical Graphs Support**
  - Implemented `recorder.import_statistics` service integration
  - Historical data now appears correctly in Energy Dashboard graphs
  - All portal readings (2+ years) imported as statistics with correct timestamps
  - Manual historical readings also imported as statistics
  - Graphs now show actual historical consumption patterns

### Fixed
- **Energy Dashboard showing 0 m³**
  - Statistics are now properly imported to HA's long-term database
  - Energy Dashboard can correctly read and display historical data
  - Consumption tracking works properly with statistical data

### Improved
- **Enhanced dropdown debugging**
  - Added comprehensive JavaScript console logging
  - Shows config loading status and meter detection
  - Warns when no meters are configured
  - Helps diagnose configuration issues

- **Better statistics logging**
  - Shows date range being imported
  - Logs number of statistics per sensor
  - Better error messages for statistics import failures

### Technical
- Added `import_statistics()` method to HomeAssistantAPI
- Statistics include both 'state' and 'sum' for total_increasing sensors
- Automatic combination of portal_readings + historical_readings
- Statistics sorted by date before import
- Proper timestamp formatting for HA's statistics database

### How It Works
1. Sensor state shows current reading (timestamp = now)
2. All readings (portal + historical) stored in attributes
3. **NEW:** All readings also imported as statistics with correct dates
4. Energy Dashboard reads from statistics database
5. Historical graphs now display correctly!

### Migration
After upgrading:
1. The add-on will automatically import all historical statistics
2. Energy Dashboard will show historical data immediately
3. Check logs for "Importing X statistics" messages
4. For dropdown issues, check browser console (F12) for debugging info

## [1.3.2] - 2025-12-18

### Fixed
- **Empty meter dropdown in web interface**
  - Added fallback to load config directly if not in app_state
  - Improved error handling in /config route
  - Config now strips whitespace from meter numbers
  - Better logging to debug configuration issues

### Improved
- **Enhanced logging for debugging**
  - Added detailed logging of portal table scraping
  - Shows number of rows found in readings table
  - Logs each reading being processed with date, value, consumption
  - Logs when readings are added to existing meters
  - Better visibility into what data is being captured
- Better error messages in web interface config route

### Technical
- Improved /config endpoint with fallback loading
- Added INFO-level logging for portal scraping process
- Helps diagnose issues with missing readings or incorrect meter data

### Known Limitations
- **Sensor timestamps**: Home Assistant's State API doesn't support backdating states
  - Sensor state timestamp is always "now" when updated via API
  - All readings (portal and historical) are stored in sensor **attributes**:
    - `portal_readings` - All readings from the 2-year portal window
    - `historical_readings` - Manually added readings beyond 2-year window
  - Current sensor state shows the most recent reading value
  - For historical graphs, you would need to use HA's Recorder API (more complex)

## [1.3.1] - 2025-12-18

### Added
- **Historical Readings Web Interface**
  - Added form to add historical readings directly from web interface
  - Table view showing all historical readings per configured meter
  - Delete button for each historical reading
  - Meter dropdown automatically populated from configuration
  - Date picker for easy date selection
  - Real-time updates after adding/deleting readings

### Changed
- **Consumption is now optional and auto-calculated**
  - No need to manually enter consumption values
  - System calculates consumption based on previous readings
  - Simplified historical readings form (removed consumption field)

### Improved
- More user-friendly historical readings management
- No more manual JSON file editing required
- Better visual presentation of historical data
- Separate tables for each configured meter
- Confirmation dialog before deleting readings

### Technical
- Added Flask routes: /config, /historical/add, /historical/delete, /historical/list
- Web interface now fetches configuration dynamically
- Historical manager integrated with web interface
- Enhanced error handling and user feedback

## [1.3.0] - 2025-12-18

### Added
- **Web Interface with Manual Reload Button**
  - Enabled ingress support for web-based control panel
  - Added Flask web server with clean, modern UI
  - Manual fetch button accessible from Home Assistant sidebar
  - Real-time status display showing last fetch time
  - Panel accessible at "WAZ Nieplitz Water" in sidebar

- **Meter Number Configuration**
  - New config options: `main_meter_number` and `garden_meter_number`
  - Users can now specify exact meter numbers to track
  - Only configured meters will create sensors
  - Prevents unwanted sensors from being created

### Changed
- **BREAKING: Meter Identification Logic**
  - Changed from alphabetical sorting to explicit configuration
  - Meters must now be configured with their meter numbers
  - Unknown/unconfigured meters are skipped
  - More predictable and user-controlled behavior

- **Sensor Creation**
  - Only creates sensors for explicitly configured meters
  - If main_meter_number is not set, no main sensor is created
  - If garden_meter_number is not set, no garden sensor is created
  - Users can choose to track one or both meters

### Improved
- Web interface provides easy manual fetch without file manipulation
- Better logging when meters are skipped or not found
- Warnings when configured meters aren't found in portal
- Cleaner configuration with explicit meter selection

### Migration Notes
**Important:** After upgrading to v1.3.0, you must configure meter numbers:
1. Go to Settings → Add-ons → WAZ Nieplitz Water Meter → Configuration
2. Find your meter numbers in the add-on logs (they're displayed during fetch)
3. Set `main_meter_number` to your main water meter number (e.g., "15093668")
4. Set `garden_meter_number` to your garden meter number (e.g., "2181453194")
5. Restart the add-on

Without configuration, no sensors will be created!

## [1.2.7] - 2025-12-18

### Fixed
- **Critical:** Fixed number parsing bug causing sensors to show 0 m³
  - Previous version was checking cleaned string but converting uncleaned string
  - Now properly converts cleaned strings with float() then int()
  - Handles European number formats (comma as decimal separator)
  - Handles spaces in numbers
  - Added try/except with warning logs for unparseable values
- Fixed state type sent to Home Assistant (now properly converted to string)
- Added comprehensive error logging for API responses

### Improved
- Enhanced logging with state type information
- Better error messages showing parsing failures
- Debug logging for HA API communication
- More robust number parsing with proper exception handling

## [1.2.6] - 2025-12-18

### Fixed
- **Critical:** Fixed date logic to prioritize Ablesetag (reading day) over Stichtag (reference day)
  - Now correctly uses actual reading date when available
  - Falls back to reference date only when reading date is not present
  - This ensures the correct date is displayed for each reading

### Changed
- **Default sensor names simplified** to "Main" and "Garden" (was "Water Meter Main" and "Water Meter Garden")
- **All portal readings now captured** instead of just the most recent
  - Every reading from the portal table is now stored
  - Readings sorted by date (newest first)
  - Available in sensor attributes as `portal_readings` array
  - Count available as `portal_readings_count` attribute

### Improved
- Better number parsing for readings with various formats
- More detailed logging showing portal readings count per meter
- Sensor attributes now include complete historical data from portal

### Note
Home Assistant graphs require data accumulated over time while the add-on is running. Portal readings are visible in sensor attributes but won't appear in historical graphs until new readings are collected during add-on operation.

## [1.2.5] - 2025-12-18

### Fixed
- **Critical:** Corrected login form field names
  - Changed from generic `username`/`password` fields to actual portal field names
  - Now using: `fieldLoginBenutzername`, `fieldLoginPasswort`, `fieldFormSent`, `fieldSFileReferer`
  - Previous generic field names were causing login to fail silently
  - This fixes the "can't find readings" error by enabling successful authentication

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
