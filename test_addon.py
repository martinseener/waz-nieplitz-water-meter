#!/usr/bin/env python3
"""
Test script for WAZ Nieplitz Water Meter Add-on
Run this standalone to test the add-on without Home Assistant
"""

import json
import logging
import os
import sys
import tempfile
from datetime import datetime
from typing import Dict, List

# Add the current directory to path to import run.py modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import from run.py
from run import WAZNieplitzClient, HistoricalReadingsManager


class MockHomeAssistantAPI:
    """Mock Home Assistant API for testing."""

    def __init__(self):
        """Initialize mock API."""
        self.sensors = {}

    def update_sensor(self, entity_id: str, state: float, attributes: Dict) -> bool:
        """Mock sensor update - stores in memory."""
        self.sensors[entity_id] = {
            'state': state,
            'attributes': attributes
        }
        logger.info(f"[MOCK] Updated sensor {entity_id}: {state}")
        logger.info(f"[MOCK] Attributes: {json.dumps(attributes, indent=2, default=str)}")
        return True

    def get_sensor(self, entity_id: str):
        """Get sensor data."""
        return self.sensors.get(entity_id)

    def print_all_sensors(self):
        """Print all sensor data."""
        print("\n" + "="*80)
        print("SENSOR DATA")
        print("="*80)
        for entity_id, data in self.sensors.items():
            print(f"\nEntity ID: {entity_id}")
            print(f"State: {data['state']} m³")
            print(f"Attributes:")
            for key, value in data['attributes'].items():
                if key == 'historical_readings':
                    print(f"  {key}: ({len(value)} readings)")
                    for reading in value:
                        print(f"    - {reading['date']}: {reading['reading']} m³")
                else:
                    print(f"  {key}: {value}")
        print("="*80 + "\n")


def test_portal_login(username: str, password: str):
    """Test logging into the portal."""
    print("\n" + "="*80)
    print("TEST 1: Portal Login")
    print("="*80)

    client = WAZNieplitzClient(username, password)

    try:
        success = client.login()
        if success:
            print("✓ Login successful!")
            return client
        else:
            print("✗ Login failed - check your credentials")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None


def test_fetch_readings(client: WAZNieplitzClient):
    """Test fetching meter readings."""
    print("\n" + "="*80)
    print("TEST 2: Fetch Meter Readings")
    print("="*80)

    try:
        meters = client.get_meter_readings()

        if meters:
            print(f"✓ Found {len(meters)} meter(s):\n")
            for meter in meters:
                print(f"  Meter Number: {meter['meter_number']}")
                print(f"  Current Reading: {meter['reading']} m³")
                print(f"  Recent Consumption: {meter['consumption']} m³")
                print(f"  Reading Type: {meter['reading_type']}")
                if meter['reading_date']:
                    print(f"  Reading Date: {meter['reading_date']}")
                if meter['reference_date']:
                    print(f"  Reference Date: {meter['reference_date']}")
                print()
            return meters
        else:
            print("✗ No meters found")
            return []
    except Exception as e:
        print(f"✗ Error fetching readings: {e}")
        return []


def test_historical_readings():
    """Test historical readings management."""
    print("\n" + "="*80)
    print("TEST 3: Historical Readings Management")
    print("="*80)

    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name

    try:
        manager = HistoricalReadingsManager(filepath=temp_file)

        # Test adding readings
        print("\n1. Adding historical readings...")
        test_data = [
            ("15093668", "2019-12-31", 50, 140),
            ("15093668", "2020-12-31", 100, 150),
            ("15093668", "2021-12-31", 150, 160),
            ("2181453194", "2020-12-31", 10, 15),
        ]

        for meter, date, reading, consumption in test_data:
            success = manager.add_reading(meter, date, reading, consumption, "Test Entry")
            if success:
                print(f"  ✓ Added: Meter {meter}, {date}, {reading} m³")
            else:
                print(f"  ✗ Failed to add: Meter {meter}, {date}")

        # Test retrieving readings
        print("\n2. Retrieving historical readings...")
        all_readings = manager.get_all_readings()
        for meter_number, readings in all_readings.items():
            print(f"\n  Meter {meter_number}: {len(readings)} reading(s)")
            for r in readings:
                print(f"    - {r['date']}: {r['reading']} m³ (consumption: {r['consumption']} m³)")

        # Test updating existing reading
        print("\n3. Updating existing reading...")
        success = manager.add_reading("15093668", "2020-12-31", 105, 155, "Updated Test Entry")
        if success:
            print("  ✓ Updated reading for 2020-12-31")
            updated = manager.get_readings("15093668")
            for r in updated:
                if "2020-12-31" in r['date']:
                    print(f"    New value: {r['reading']} m³")

        # Test deleting reading
        print("\n4. Deleting a reading...")
        success = manager.delete_reading("15093668", "2019-12-31")
        if success:
            print("  ✓ Deleted reading for 2019-12-31")
            remaining = manager.get_readings("15093668")
            print(f"    Remaining readings: {len(remaining)}")

        print("\n✓ Historical readings tests completed!")
        return manager

    except Exception as e:
        print(f"✗ Error in historical readings test: {e}")
        return None
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_sensor_updates(meters: List[Dict], historical_manager: HistoricalReadingsManager):
    """Test sensor updates with mock HA API."""
    print("\n" + "="*80)
    print("TEST 4: Sensor Updates")
    print("="*80)

    mock_api = MockHomeAssistantAPI()

    try:
        for i, meter in enumerate(meters):
            # Determine meter type (simple logic)
            meter_type = 'main' if i == 0 else 'garden' if i == 1 else 'unknown'

            if meter_type == 'main':
                entity_id = 'sensor.waz_nieplitz_water_main'
                friendly_name = 'Water Meter Main'
            elif meter_type == 'garden':
                entity_id = 'sensor.waz_nieplitz_water_garden'
                friendly_name = 'Water Meter Garden'
            else:
                entity_id = f"sensor.waz_nieplitz_water_{meter['meter_number']}"
                friendly_name = f"Water Meter {meter['meter_number']}"

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

            # Add historical readings
            if historical_manager:
                historical_readings = historical_manager.get_readings(meter['meter_number'])
                if historical_readings:
                    attributes['historical_readings'] = historical_readings
                    attributes['historical_count'] = len(historical_readings)

            # Update sensor
            mock_api.update_sensor(entity_id, meter['reading'], attributes)

        # Print all sensor data
        mock_api.print_all_sensors()

        print("✓ Sensor update tests completed!")
        return mock_api

    except Exception as e:
        print(f"✗ Error in sensor update test: {e}")
        return None


def test_command_file_processing():
    """Test the command file processing for historical readings."""
    print("\n" + "="*80)
    print("TEST 5: Command File Processing")
    print("="*80)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        command_file = f.name

    try:
        manager = HistoricalReadingsManager(filepath=temp_file)

        # Test add command
        print("\n1. Testing ADD command via file...")
        command = {
            "action": "add",
            "meter_number": "15093668",
            "date": "2018-12-31",
            "reading": 25,
            "consumption": 130,
            "reading_type": "Command File Test"
        }

        with open(command_file, 'w') as f:
            json.dump(command, f)

        # Simulate processing
        if os.path.exists(command_file):
            with open(command_file, 'r') as f:
                cmd = json.load(f)

            success = manager.add_reading(
                cmd['meter_number'],
                cmd['date'],
                cmd['reading'],
                cmd.get('consumption'),
                cmd.get('reading_type', 'Manual Entry')
            )
            os.remove(command_file)

            if success:
                print("  ✓ ADD command processed successfully")
                readings = manager.get_readings("15093668")
                print(f"    Total readings: {len(readings)}")
            else:
                print("  ✗ ADD command failed")

        # Test delete command
        print("\n2. Testing DELETE command via file...")
        command = {
            "action": "delete",
            "meter_number": "15093668",
            "date": "2018-12-31"
        }

        with open(command_file, 'w') as f:
            json.dump(command, f)

        # Simulate processing
        if os.path.exists(command_file):
            with open(command_file, 'r') as f:
                cmd = json.load(f)

            success = manager.delete_reading(cmd['meter_number'], cmd['date'])
            os.remove(command_file)

            if success:
                print("  ✓ DELETE command processed successfully")
                readings = manager.get_readings("15093668")
                print(f"    Remaining readings: {len(readings)}")
            else:
                print("  ✗ DELETE command failed")

        print("\n✓ Command file processing tests completed!")

    except Exception as e:
        print(f"✗ Error in command file test: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(command_file):
            os.remove(command_file)


def run_all_tests(username: str, password: str, skip_portal: bool = False):
    """Run all tests."""
    print("\n" + "="*80)
    print("WAZ NIEPLITZ WATER METER ADD-ON TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now()}")

    historical_manager = None
    meters = []

    # Test 1: Portal Login (optional)
    if not skip_portal:
        client = test_portal_login(username, password)
        if client:
            # Test 2: Fetch Readings
            meters = test_fetch_readings(client)
    else:
        print("\n[SKIPPED] Portal tests (use --test-portal to enable)")

    # Test 3: Historical Readings
    historical_manager = test_historical_readings()

    # Test 4: Sensor Updates
    if meters and historical_manager:
        test_sensor_updates(meters, historical_manager)
    elif historical_manager:
        print("\n[INFO] Skipping sensor update test (no portal data)")

    # Test 5: Command File Processing
    test_command_file_processing()

    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)
    print(f"Finished at: {datetime.now()}\n")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test WAZ Nieplitz Water Meter Add-on')
    parser.add_argument('--username', '-u', help='Portal username (for portal tests)')
    parser.add_argument('--password', '-p', help='Portal password (for portal tests)')
    parser.add_argument('--test-portal', action='store_true', help='Include portal login/fetch tests')
    parser.add_argument('--offline', action='store_true', help='Skip portal tests (test only local features)')

    args = parser.parse_args()

    # Determine if we should test portal
    skip_portal = args.offline or not (args.username and args.password)

    if args.test_portal and skip_portal:
        print("ERROR: --test-portal requires --username and --password")
        sys.exit(1)

    # Run tests
    run_all_tests(
        username=args.username or '',
        password=args.password or '',
        skip_portal=skip_portal
    )
