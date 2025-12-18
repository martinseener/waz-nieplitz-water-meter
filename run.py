#!/usr/bin/env python3
"""
WAZ Nieplitz Water Meter Add-on
Fetches water meter readings from kundenportal.waz-nieplitz.de
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from flask import Flask, jsonify, send_file, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://kundenportal.waz-nieplitz.de"
LOGIN_URL = BASE_URL  # Login form is at the root
READINGS_URL = f"{BASE_URL}/ablesungen"
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HA_URL = "http://supervisor/core/api"
MANUAL_FETCH_TRIGGER = "/data/manual_fetch"
CHECK_INTERVAL = 60  # Check for manual trigger every 60 seconds
HISTORICAL_READINGS_FILE = "/data/historical_readings.json"
INGRESS_PORT = int(os.environ.get('INGRESS_PORT', '8099'))

# Flask app
app = Flask(__name__)
app.logger.setLevel(logging.ERROR)  # Suppress Flask logging

# Global state for web interface
app_state = {
    'last_fetch': None,
    'fetch_callback': None,  # Will be set to trigger manual fetch
    'historical_manager': None,  # Will be set to historical readings manager
    'config': None  # Will be set to configuration
}


class HistoricalReadingsManager:
    """Manager for manual historical water meter readings."""

    def __init__(self, filepath: str = HISTORICAL_READINGS_FILE):
        """Initialize the manager."""
        self.filepath = filepath
        self.readings = self._load_readings()

    def _load_readings(self) -> Dict[str, List[Dict]]:
        """Load historical readings from file."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {sum(len(r) for r in data.values())} historical reading(s)")
                    return data
            else:
                logger.info("No historical readings file found, starting fresh")
                return {}
        except Exception as e:
            logger.error(f"Error loading historical readings: {e}")
            return {}

    def _save_readings(self):
        """Save historical readings to file."""
        try:
            # Ensure /data directory exists
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            with open(self.filepath, 'w') as f:
                json.dump(self.readings, f, indent=2)
            logger.info("Historical readings saved successfully")
        except Exception as e:
            logger.error(f"Error saving historical readings: {e}")

    def add_reading(self, meter_number: str, date: str, reading: float,
                   consumption: Optional[float] = None, reading_type: str = "Manual Entry") -> bool:
        """
        Add a manual historical reading.

        Args:
            meter_number: The meter number (e.g., "15093668")
            date: Date string in format "YYYY-MM-DD" or "DD.MM.YYYY"
            reading: The meter reading in m³
            consumption: Optional consumption for this period in m³
            reading_type: Description of the reading type

        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse date
            try:
                # Try ISO format first
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                # Try German format
                parsed_date = datetime.strptime(date, "%d.%m.%Y")

            # Initialize meter if not exists
            if meter_number not in self.readings:
                self.readings[meter_number] = []

            # Create reading entry
            entry = {
                "date": parsed_date.isoformat(),
                "reading": float(reading),
                "consumption": float(consumption) if consumption is not None else None,
                "reading_type": reading_type,
                "manual": True
            }

            # Check if reading already exists for this date
            existing_idx = None
            for idx, r in enumerate(self.readings[meter_number]):
                if r["date"] == entry["date"]:
                    existing_idx = idx
                    break

            if existing_idx is not None:
                # Update existing entry
                self.readings[meter_number][existing_idx] = entry
                logger.info(f"Updated historical reading for meter {meter_number} on {date}")
            else:
                # Add new entry
                self.readings[meter_number].append(entry)
                logger.info(f"Added historical reading for meter {meter_number} on {date}: {reading} m³")

            # Sort readings by date
            self.readings[meter_number].sort(key=lambda x: x["date"])

            # Save to file
            self._save_readings()
            return True

        except Exception as e:
            logger.error(f"Error adding historical reading: {e}")
            return False

    def get_readings(self, meter_number: str) -> List[Dict]:
        """Get all historical readings for a meter."""
        return self.readings.get(meter_number, [])

    def get_all_readings(self) -> Dict[str, List[Dict]]:
        """Get all historical readings for all meters."""
        return self.readings

    def delete_reading(self, meter_number: str, date: str) -> bool:
        """Delete a specific historical reading."""
        try:
            if meter_number not in self.readings:
                return False

            # Parse date
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                parsed_date = datetime.strptime(date, "%d.%m.%Y")

            iso_date = parsed_date.isoformat()

            # Find and remove reading
            self.readings[meter_number] = [
                r for r in self.readings[meter_number]
                if r["date"] != iso_date
            ]

            # Remove meter entry if no readings left
            if not self.readings[meter_number]:
                del self.readings[meter_number]

            self._save_readings()
            logger.info(f"Deleted historical reading for meter {meter_number} on {date}")
            return True

        except Exception as e:
            logger.error(f"Error deleting historical reading: {e}")
            return False


class WAZNieplitzClient:
    """Client for WAZ Nieplitz customer portal."""

    def __init__(self, username: str, password: str):
        """Initialize the client."""
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def login(self) -> bool:
        """Login to the portal."""
        try:
            logger.info("Attempting to login to WAZ Nieplitz portal...")

            # First, get the login page to retrieve any CSRF tokens or form data
            response = self.session.get(LOGIN_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the login form
            form = soup.find('form')
            if not form:
                logger.error("Could not find login form")
                return False

            # Prepare login data with correct field names
            login_data = {
                'fieldLoginBenutzername': self.username,
                'fieldLoginPasswort': self.password,
                'fieldFormSent': 'formLogin',
                'fieldSFileReferer': ''
            }

            # Add any other hidden fields from the form (if they exist)
            for hidden_input in soup.find_all('input', type='hidden'):
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name and name not in login_data:
                    login_data[name] = value

            # Submit login form
            action = form.get('action', LOGIN_URL)
            if not action.startswith('http'):
                action = BASE_URL + action

            logger.debug(f"Posting login to: {action}")
            response = self.session.post(action, data=login_data, timeout=30)
            response.raise_for_status()

            # Check if login was successful by trying to access the readings page
            test_response = self.session.get(READINGS_URL, timeout=30)
            if test_response.status_code == 200 and 'Ablesungen' in test_response.text:
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - could not access readings page")
                logger.debug(f"Response status: {test_response.status_code}")
                logger.debug(f"Response contains 'Ablesungen': {'Ablesungen' in test_response.text}")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def get_meter_readings(self) -> List[Dict]:
        """Fetch meter readings from the portal."""
        try:
            logger.info("Fetching meter readings...")

            response = self.session.get(READINGS_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table with readings
            table = soup.find('table', class_='listview ablesungen')
            if not table:
                logger.error("Could not find readings table")
                return []

            meters = {}

            # Parse table rows - collect ALL readings per meter
            rows = table.find_all('tr', class_='item')
            logger.info(f"Found {len(rows)} row(s) in readings table")

            for idx, row in enumerate(rows):
                # Extract meter number
                meter_cell = row.find('td', class_='zaehler')
                if meter_cell:
                    meter_number = meter_cell.get_text(strip=True).replace('Zähler', '').strip()
                    logger.info(f"Row {idx+1}: Processing meter {meter_number}")

                    # Extract reading date (Ablesetag)
                    ablesetag_cell = row.find('td', class_='ablesetag')
                    ablesetag = ablesetag_cell.get_text(strip=True).replace('Ablesetag', '').strip() if ablesetag_cell else ''

                    # Extract reference date (Stichtag)
                    stichtag_cell = row.find('td', class_='stichtag')
                    stichtag = stichtag_cell.get_text(strip=True).replace('Stichtag', '').strip() if stichtag_cell else ''

                    # Extract meter reading (Stand)
                    stand_cell = row.find('td', class_='stand')
                    stand = stand_cell.get_text(strip=True).replace('Stand', '').replace('m³', '').strip() if stand_cell else '0'

                    # Extract consumption (Verbrauch)
                    verbrauch_cell = row.find('td', class_='verbrauch')
                    verbrauch = verbrauch_cell.get_text(strip=True).replace('Verbrauch (m³)', '').replace('m³', '').strip() if verbrauch_cell else '0'

                    # Extract reading type
                    ablesart_cell = row.find('td', class_='ablesart')
                    ablesart = ablesart_cell.get_text(strip=True).replace('Ableseart', '').strip() if ablesart_cell else ''

                    # Parse reading date (Ablesetag)
                    reading_date = None
                    if ablesetag:
                        try:
                            reading_date = date_parser.parse(ablesetag, dayfirst=True)
                        except:
                            pass

                    # Parse reference date (Stichtag)
                    reference_date = None
                    if stichtag:
                        try:
                            reference_date = date_parser.parse(stichtag, dayfirst=True)
                        except:
                            pass

                    # Determine primary date: prioritize Ablesetag over Stichtag
                    primary_date = reading_date if reading_date else reference_date

                    # Parse reading value - remove commas and handle decimal points
                    try:
                        # Remove spaces and replace comma with dot for European format
                        cleaned_stand = stand.replace(' ', '').replace(',', '.')
                        reading_value = int(float(cleaned_stand))
                    except (ValueError, AttributeError):
                        reading_value = 0
                        logger.warning(f"Could not parse reading value: '{stand}'")

                    # Parse consumption value
                    try:
                        cleaned_verbrauch = verbrauch.replace(' ', '').replace(',', '.')
                        consumption_value = int(float(cleaned_verbrauch))
                    except (ValueError, AttributeError):
                        consumption_value = 0
                        logger.warning(f"Could not parse consumption value: '{verbrauch}'")

                    # Create reading entry
                    reading_entry = {
                        'date': primary_date.isoformat() if primary_date else None,
                        'reading': reading_value,
                        'consumption': consumption_value,
                        'reading_type': ablesart,
                        'reading_date': reading_date.isoformat() if reading_date else None,
                        'reference_date': reference_date.isoformat() if reference_date else None
                    }

                    logger.info(f"  → Date={primary_date}, Reading={reading_value} m³, Consumption={consumption_value} m³, Type={ablesart}")

                    # Initialize meter if not exists
                    if meter_number not in meters:
                        meters[meter_number] = {
                            'meter_number': meter_number,
                            'reading_date': reading_date,
                            'reference_date': reference_date,
                            'primary_date': primary_date,
                            'reading': reading_value,
                            'consumption': consumption_value,
                            'reading_type': ablesart,
                            'portal_readings': [reading_entry]
                        }
                    else:
                        # Add this reading to the portal readings list
                        meters[meter_number]['portal_readings'].append(reading_entry)
                        logger.debug(f"  Added to existing meter {meter_number} (now {len(meters[meter_number]['portal_readings'])} reading(s))")

                        # Update current reading if this one is more recent
                        existing = meters[meter_number]
                        if primary_date and existing.get('primary_date'):
                            if primary_date > existing['primary_date']:
                                logger.debug(f"  Updating current reading for {meter_number} (newer date)")
                                meters[meter_number].update({
                                    'reading_date': reading_date,
                                    'reference_date': reference_date,
                                    'primary_date': primary_date,
                                    'reading': reading_value,
                                    'consumption': consumption_value,
                                    'reading_type': ablesart
                                })

            result = list(meters.values())
            logger.info(f"Found {len(result)} meter(s)")
            for meter in result:
                portal_count = len(meter.get('portal_readings', []))
                logger.info(f"Meter {meter['meter_number']}: {meter['reading']} m³ "
                          f"({portal_count} portal reading(s), Date: {meter.get('primary_date')})")

            return result

        except Exception as e:
            logger.error(f"Error fetching readings: {e}")
            return []


class HomeAssistantAPI:
    """Interface to Home Assistant API."""

    def __init__(self):
        """Initialize the API client."""
        self.token = SUPERVISOR_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def update_sensor(self, entity_id: str, state: float, attributes: Dict) -> bool:
        """Update or create a sensor in Home Assistant."""
        try:
            url = f"{HA_URL}/states/{entity_id}"
            # Convert state to string as HA expects
            state_str = str(state)
            data = {
                'state': state_str,
                'attributes': attributes
            }

            logger.debug(f"Sending to HA: entity={entity_id}, state={state_str}")
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()

            logger.info(f"Updated sensor {entity_id}: {state}")
            logger.debug(f"HA Response: {response.status_code}")
            return True

        except Exception as e:
            logger.error(f"Error updating sensor {entity_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return False

    def register_service(self, domain: str, service: str, service_data: Dict) -> bool:
        """Register a service with Home Assistant."""
        try:
            url = f"{HA_URL}/services/{domain}/{service}"
            response = requests.post(url, headers=self.headers, json=service_data, timeout=10)
            response.raise_for_status()
            logger.info(f"Registered service {domain}.{service}")
            return True
        except Exception as e:
            logger.error(f"Error registering service {domain}.{service}: {e}")
            return False

    def import_statistics(self, entity_id: str, friendly_name: str, readings: List[Dict]) -> bool:
        """
        Import historical statistics for energy/utility sensors using WebSocket API.
        This allows the Energy Dashboard to show historical data correctly.

        Args:
            entity_id: The sensor entity ID
            friendly_name: Friendly name for the statistic
            readings: List of readings with 'date' and 'reading' keys

        Returns:
            True if successful, False otherwise
        """
        try:
            if not readings:
                logger.warning(f"No readings to import for {entity_id}")
                return False

            # Sort readings by date
            sorted_readings = sorted(readings, key=lambda x: x.get('date', ''))

            # Build statistics data
            stats = []
            for reading in sorted_readings:
                if not reading.get('date') or reading.get('reading') is None:
                    continue

                # Convert date to timestamp with timezone
                try:
                    date_obj = datetime.fromisoformat(reading['date'].replace('Z', '+00:00'))
                    # Ensure timezone info is present (use UTC if not specified)
                    if date_obj.tzinfo is None:
                        from datetime import timezone
                        date_obj = date_obj.replace(tzinfo=timezone.utc)
                except Exception as e:
                    logger.warning(f"Could not parse date: {reading['date']} - {e}")
                    continue

                # For total_increasing sensors
                # Include 'sum' for cumulative value
                stat_entry = {
                    "start": date_obj.isoformat(),
                    "sum": float(reading['reading'])
                }
                stats.append(stat_entry)

            if not stats:
                logger.warning(f"No valid statistics to import for {entity_id}")
                return False

            # Use WebSocket API to import statistics
            # For external statistics, statistic_id uses ':' instead of '.' as delimiter
            # IMPORTANT: The domain (part before :) MUST match the source parameter
            # Convert sensor.waz_nieplitz_water_main -> waz_nieplitz:water_main
            if '.' in entity_id:
                _, object_id = entity_id.split('.', 1)
                # Remove waz_nieplitz_ prefix from object_id if present
                if object_id.startswith('waz_nieplitz_water_'):
                    object_id = 'water_' + object_id[len('waz_nieplitz_water_'):]
                statistic_id = f"waz_nieplitz:{object_id}"
            else:
                statistic_id = entity_id

            logger.info(f"Importing {len(stats)} statistics for {statistic_id} (entity: {entity_id})")
            logger.info(f"Date range: {stats[0]['start']} to {stats[-1]['start']}")

            # Import via WebSocket API
            import websocket
            import ssl

            # Connect to Home Assistant WebSocket
            ws_url = f"ws://supervisor/core/websocket"
            ws = websocket.create_connection(ws_url, timeout=30)

            try:
                # Receive auth_required message
                result = json.loads(ws.recv())
                if result['type'] != 'auth_required':
                    raise Exception(f"Expected auth_required, got {result['type']}")

                # Send auth message
                ws.send(json.dumps({
                    'type': 'auth',
                    'access_token': self.token
                }))

                # Receive auth response
                result = json.loads(ws.recv())
                if result['type'] != 'auth_ok':
                    raise Exception(f"Authentication failed: {result}")

                # Send import_statistics command
                # Note: As of HA 2025.11, metadata uses mean_type instead of has_mean
                # For external statistics, source should be a custom integration name
                command = {
                    'id': 1,
                    'type': 'recorder/import_statistics',
                    'metadata': {
                        'has_mean': False,  # Still include for backwards compatibility
                        'has_sum': True,
                        'mean_type': 0,  # 0=no mean, 1=arithmetic, 2=circular (new API)
                        'name': friendly_name,
                        'source': 'waz_nieplitz',
                        'statistic_id': statistic_id,
                        'unit_of_measurement': 'm³',
                        'unit_class': None  # Required as of HA 2025.11
                    },
                    'stats': stats
                }

                logger.info(f"WebSocket command: {command}")
                ws.send(json.dumps(command))

                # Receive response
                result = json.loads(ws.recv())
                logger.info(f"WebSocket response: {result}")

                if result.get('success'):
                    logger.info(f"Successfully imported statistics for {entity_id}")
                    return True
                else:
                    logger.error(f"Failed to import statistics: {result}")
                    return False

            finally:
                ws.close()

        except Exception as e:
            logger.error(f"Error importing statistics for {entity_id}: {e}")
            return False


def load_config() -> Dict:
    """Load add-on configuration."""
    try:
        with open('/data/options.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Configuration file not found, using environment variables")
        return {
            'username': os.environ.get('USERNAME', ''),
            'password': os.environ.get('PASSWORD', ''),
            'update_interval': int(os.environ.get('UPDATE_INTERVAL', '2592000')),  # 30 days
            'main_meter_number': os.environ.get('MAIN_METER_NUMBER', ''),
            'main_meter_name': os.environ.get('MAIN_METER_NAME', 'Main'),
            'garden_meter_number': os.environ.get('GARDEN_METER_NUMBER', ''),
            'garden_meter_name': os.environ.get('GARDEN_METER_NAME', 'Garden')
        }


def identify_meter_type(meter_number: str, config: Dict) -> str:
    """
    Identify if a meter is the main or garden meter based on configuration.

    Args:
        meter_number: The meter number to identify
        config: Configuration dict with main_meter_number and garden_meter_number

    Returns:
        'main', 'garden', or 'unknown'
    """
    main_meter_number = config.get('main_meter_number', '').strip()
    garden_meter_number = config.get('garden_meter_number', '').strip()

    if main_meter_number and meter_number == main_meter_number:
        return 'main'
    elif garden_meter_number and meter_number == garden_meter_number:
        return 'garden'
    else:
        return 'unknown'


def check_manual_trigger() -> bool:
    """Check if manual fetch trigger file exists."""
    return os.path.exists(MANUAL_FETCH_TRIGGER)


def clear_manual_trigger():
    """Remove the manual fetch trigger file."""
    try:
        if os.path.exists(MANUAL_FETCH_TRIGGER):
            os.remove(MANUAL_FETCH_TRIGGER)
            logger.info("Manual fetch trigger cleared")
    except Exception as e:
        logger.error(f"Error clearing manual trigger: {e}")


def fetch_and_update_meters(client: WAZNieplitzClient, ha_api: HomeAssistantAPI,
                            config: Dict,
                            historical_manager: Optional[HistoricalReadingsManager] = None) -> bool:
    """
    Fetch meter readings and update Home Assistant sensors.
    Only creates sensors for meters configured in main_meter_number or garden_meter_number.
    Returns True if successful, False otherwise.
    """
    try:
        # Login to portal
        if not client.login():
            logger.error("Failed to login to portal")
            return False

        # Fetch meter readings
        meters = client.get_meter_readings()

        if not meters:
            logger.warning("No meter readings found")
            return False

        # Get configured meter numbers
        main_meter_number = config.get('main_meter_number', '').strip()
        garden_meter_number = config.get('garden_meter_number', '').strip()
        main_meter_name = config.get('main_meter_name', 'Main')
        garden_meter_name = config.get('garden_meter_name', 'Garden')

        # Track which configured meters were found
        found_main = False
        found_garden = False

        # Update Home Assistant sensors
        for meter in meters:
            meter_type = identify_meter_type(meter['meter_number'], config)

            # Skip unconfigured meters
            if meter_type == 'unknown':
                logger.info(f"Skipping unconfigured meter: {meter['meter_number']}")
                continue

            if meter_type == 'main':
                entity_id = 'sensor.waz_nieplitz_water_main'
                friendly_name = main_meter_name
                found_main = True
            elif meter_type == 'garden':
                entity_id = 'sensor.waz_nieplitz_water_garden'
                friendly_name = garden_meter_name
                found_garden = True
            else:
                continue  # Should not reach here, but skip just in case

            # Prepare attributes
            attributes = {
                'unit_of_measurement': 'm³',
                'friendly_name': friendly_name,
                'device_class': 'water',
                'state_class': 'total_increasing',
                'meter_number': meter['meter_number'],
                'reading_type': meter['reading_type'],
                'consumption': meter['consumption'],
                'icon': 'mdi:water'
            }

            if meter['reading_date']:
                attributes['reading_date'] = meter['reading_date'].isoformat()
            if meter['reference_date']:
                attributes['reference_date'] = meter['reference_date'].isoformat()

            # Add portal readings to attributes
            if 'portal_readings' in meter and meter['portal_readings']:
                # Sort portal readings by date (newest first)
                sorted_readings = sorted(
                    meter['portal_readings'],
                    key=lambda x: x['date'] if x['date'] else '',
                    reverse=True
                )
                attributes['portal_readings'] = sorted_readings
                attributes['portal_readings_count'] = len(sorted_readings)
                logger.info(f"Meter {meter['meter_number']}: {len(sorted_readings)} portal reading(s)")

            # Add historical readings to attributes
            if historical_manager:
                historical_readings = historical_manager.get_readings(meter['meter_number'])
                if historical_readings:
                    attributes['historical_readings'] = historical_readings
                    attributes['historical_count'] = len(historical_readings)
                    logger.info(f"Meter {meter['meter_number']}: {len(historical_readings)} historical reading(s)")

            # Update sensor
            logger.info(f"Updating {entity_id} with state={meter['reading']} (type: {type(meter['reading']).__name__})")
            ha_api.update_sensor(entity_id, meter['reading'], attributes)

            # Import statistics for Energy Dashboard historical graphs
            all_readings = []

            # Add portal readings
            if 'portal_readings' in meter and meter['portal_readings']:
                all_readings.extend(meter['portal_readings'])

            # Add historical readings
            if historical_manager:
                historical_readings = historical_manager.get_readings(meter['meter_number'])
                if historical_readings:
                    all_readings.extend(historical_readings)

            # Import statistics if we have readings
            if all_readings:
                logger.info(f"Importing {len(all_readings)} statistics for {entity_id}")
                ha_api.import_statistics(entity_id, friendly_name, all_readings)

        # Warn if configured meters were not found
        if main_meter_number and not found_main:
            logger.warning(f"Configured main meter '{main_meter_number}' not found in portal readings")
        if garden_meter_number and not found_garden:
            logger.warning(f"Configured garden meter '{garden_meter_number}' not found in portal readings")

        return True

    except Exception as e:
        logger.error(f"Error during fetch and update: {e}")
        return False


def process_historical_command(historical_manager: HistoricalReadingsManager):
    """Process historical reading commands from file."""
    command_file = "/data/historical_command.json"

    try:
        if not os.path.exists(command_file):
            return

        with open(command_file, 'r') as f:
            command = json.load(f)

        action = command.get('action')

        if action == 'add':
            meter_number = command.get('meter_number')
            date = command.get('date')
            reading = command.get('reading')
            consumption = command.get('consumption')
            reading_type = command.get('reading_type', 'Manual Entry')

            if meter_number and date and reading is not None:
                success = historical_manager.add_reading(
                    meter_number, date, reading, consumption, reading_type
                )
                logger.info(f"Historical reading add {'succeeded' if success else 'failed'}")
            else:
                logger.error("Missing required fields for add command")

        elif action == 'delete':
            meter_number = command.get('meter_number')
            date = command.get('date')

            if meter_number and date:
                success = historical_manager.delete_reading(meter_number, date)
                logger.info(f"Historical reading delete {'succeeded' if success else 'failed'}")
            else:
                logger.error("Missing required fields for delete command")

        # Remove command file after processing
        os.remove(command_file)
        logger.info("Historical command processed and file removed")

    except Exception as e:
        logger.error(f"Error processing historical command: {e}")
        # Try to remove file even on error
        try:
            if os.path.exists(command_file):
                os.remove(command_file)
        except:
            pass


# Flask routes
@app.route('/')
def index():
    """Serve the main page."""
    try:
        return send_file('/index.html')
    except:
        return """
        <!DOCTYPE html>
        <html><body style="font-family: sans-serif; padding: 20px;">
        <h1>WAZ Nieplitz Water Meter</h1>
        <p>Web interface file not found. Please check installation.</p>
        </body></html>
        """, 404


@app.route('/fetch', methods=['POST'])
def fetch():
    """Trigger manual fetch."""
    try:
        if app_state['fetch_callback']:
            # Trigger manual fetch
            success = app_state['fetch_callback']()
            if success:
                app_state['last_fetch'] = datetime.now().isoformat()
                return jsonify({
                    'success': True,
                    'message': 'Readings fetched successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to fetch readings. Check add-on logs for details.'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': 'Fetch callback not initialized'
            }), 500
    except Exception as e:
        logger.error(f"Error in fetch route: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/status')
def status():
    """Get current status."""
    return jsonify({
        'last_fetch': app_state.get('last_fetch')
    })


@app.route('/config')
def get_config():
    """Get configuration for meter numbers and names."""
    try:
        config = app_state.get('config')

        if config is None:
            # Config not loaded yet, try loading directly
            logger.warning("Config not in app_state, loading directly")
            config = load_config()

        result = {
            'main_meter_number': config.get('main_meter_number', '').strip(),
            'main_meter_name': config.get('main_meter_name', 'Main'),
            'garden_meter_number': config.get('garden_meter_number', '').strip(),
            'garden_meter_name': config.get('garden_meter_name', 'Garden')
        }

        logger.info(f"Config route returning: main={result['main_meter_number']}, garden={result['garden_meter_number']}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in config route: {e}")
        return jsonify({
            'error': str(e),
            'main_meter_number': '',
            'main_meter_name': 'Main',
            'garden_meter_number': '',
            'garden_meter_name': 'Garden'
        }), 500


@app.route('/historical/add', methods=['POST'])
def add_historical():
    """Add a historical reading."""
    try:
        data = request.get_json()
        meter_number = data.get('meter_number')
        date = data.get('date')
        reading = data.get('reading')

        if not meter_number or not date or reading is None:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        historical_manager = app_state.get('historical_manager')
        if not historical_manager:
            return jsonify({
                'success': False,
                'message': 'Historical manager not initialized'
            }), 500

        # Add the reading (consumption will be calculated automatically)
        success = historical_manager.add_reading(
            meter_number=meter_number,
            date=date,
            reading=float(reading),
            consumption=None,  # Let it calculate automatically
            reading_type='Manual Entry'
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Historical reading added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to add reading'
            }), 500

    except Exception as e:
        logger.error(f"Error adding historical reading: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/historical/delete', methods=['POST'])
def delete_historical():
    """Delete a historical reading."""
    try:
        data = request.get_json()
        meter_number = data.get('meter_number')
        date = data.get('date')

        if not meter_number or not date:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        historical_manager = app_state.get('historical_manager')
        if not historical_manager:
            return jsonify({
                'success': False,
                'message': 'Historical manager not initialized'
            }), 500

        success = historical_manager.delete_reading(meter_number, date)

        if success:
            return jsonify({
                'success': True,
                'message': 'Historical reading deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete reading'
            }), 500

    except Exception as e:
        logger.error(f"Error deleting historical reading: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/historical/list')
def list_historical():
    """List all historical readings."""
    try:
        historical_manager = app_state.get('historical_manager')
        if not historical_manager:
            return jsonify({
                'readings': {}
            })

        return jsonify({
            'readings': historical_manager.readings
        })

    except Exception as e:
        logger.error(f"Error listing historical readings: {e}")
        return jsonify({
            'readings': {},
            'error': str(e)
        }), 500


def run_web_server():
    """Run the Flask web server."""
    try:
        logger.info(f"Starting web server on port {INGRESS_PORT}")
        # Disable Flask's default logging completely
        import logging as flask_logging
        import sys
        import os

        # Disable werkzeug logging
        flask_log = flask_logging.getLogger('werkzeug')
        flask_log.setLevel(flask_logging.ERROR)
        flask_log.disabled = True

        # Disable Flask's CLI output by redirecting to devnull during startup
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None

        app.run(host='0.0.0.0', port=INGRESS_PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        logger.error(f"Web server error: {e}")


def main():
    """Main loop."""
    logger.info("Starting WAZ Nieplitz Water Meter Add-on")

    # Load configuration
    config = load_config()

    username = config.get('username', '')
    password = config.get('password', '')
    update_interval = config.get('update_interval', 2592000)  # Default: 30 days

    if not username or not password:
        logger.error("Username and password must be configured")
        sys.exit(1)

    logger.info(f"Update interval: {update_interval} seconds ({update_interval / 86400:.1f} days)")
    logger.info(f"Manual fetch trigger: Create file '{MANUAL_FETCH_TRIGGER}' to trigger immediate update")
    logger.info(f"Historical readings file: {HISTORICAL_READINGS_FILE}")

    # Initialize clients
    client = WAZNieplitzClient(username, password)
    ha_api = HomeAssistantAPI()
    historical_manager = HistoricalReadingsManager()

    # Set up fetch callback for web interface
    def fetch_callback():
        """Callback for web interface manual fetch."""
        return fetch_and_update_meters(client, ha_api, config, historical_manager)

    app_state['fetch_callback'] = fetch_callback
    app_state['historical_manager'] = historical_manager
    app_state['config'] = config

    # Start web server in background thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info("Web interface started")

    # Perform initial fetch
    logger.info("Performing initial meter reading fetch...")
    fetch_and_update_meters(client, ha_api, config, historical_manager)

    # Calculate how many check intervals equal one update interval
    checks_per_update = update_interval // CHECK_INTERVAL
    check_counter = 0

    last_update_time = time.time()

    while True:
        try:
            # Check for historical reading commands
            process_historical_command(historical_manager)

            # Check for manual trigger
            if check_manual_trigger():
                logger.info("Manual fetch triggered! Fetching readings immediately...")
                clear_manual_trigger()
                if fetch_and_update_meters(client, ha_api, config, historical_manager):
                    logger.info("Manual fetch completed successfully")
                    app_state['last_fetch'] = datetime.now().isoformat()
                    last_update_time = time.time()
                    check_counter = 0  # Reset counter after manual fetch
                else:
                    logger.error("Manual fetch failed")

            # Check if it's time for scheduled update
            elif check_counter >= checks_per_update:
                logger.info("Scheduled update triggered")
                if fetch_and_update_meters(client, ha_api, config, historical_manager):
                    logger.info("Scheduled update completed successfully")
                    app_state['last_fetch'] = datetime.now().isoformat()
                    last_update_time = time.time()
                    check_counter = 0
                else:
                    logger.error("Scheduled update failed, will retry in 5 minutes")
                    time.sleep(300)
                    continue

            # Sleep and increment counter
            check_counter += 1
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.info("Retrying in 5 minutes...")
            time.sleep(300)


if __name__ == '__main__':
    main()
