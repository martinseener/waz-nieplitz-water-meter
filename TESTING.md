# Testing Guide

This guide explains how to test the WAZ Nieplitz Water Meter add-on **without installing it in your production Home Assistant instance**.

## Testing Options

There are three ways to test the add-on:

1. **Standalone Python Script** (Recommended) - Test locally without any containers
2. **Docker Container** - Test in an isolated container environment
3. **Development Home Assistant Instance** - Test in a separate HA installation

## Option 1: Standalone Python Script (Recommended)

This is the fastest and easiest way to test the add-on's core functionality.

### Prerequisites

- Python 3.11 or higher
- The dependencies from `requirements.txt`

### Setup

1. Navigate to the add-on directory:
   ```bash
   cd waz-nieplitz-water-meter
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Make the test script executable:
   ```bash
   chmod +x test_addon.py
   ```

### Running Tests

#### Test Without Portal (Offline Mode)

Test only local features (historical readings, command processing) without connecting to the portal:

```bash
python3 test_addon.py --offline
```

This runs:
- ✓ Historical readings management (add, update, delete)
- ✓ Command file processing
- ✓ Sensor attribute generation
- ✗ Portal login (skipped)
- ✗ Data fetching (skipped)

**Output Example:**
```
================================================================================
TEST 3: Historical Readings Management
================================================================================

1. Adding historical readings...
  ✓ Added: Meter 15093668, 2019-12-31, 50 m³
  ✓ Added: Meter 15093668, 2020-12-31, 100 m³
  ✓ Added: Meter 15093668, 2021-12-31, 150 m³
  ✓ Added: Meter 2181453194, 2020-12-31, 10 m³

2. Retrieving historical readings...

  Meter 15093668: 3 reading(s)
    - 2019-12-31T00:00:00: 50 m³ (consumption: 140 m³)
    - 2020-12-31T00:00:00: 100 m³ (consumption: 150 m³)
    - 2021-12-31T00:00:00: 150 m³ (consumption: 160 m³)

✓ Historical readings tests completed!
```

#### Test With Portal (Full Test)

Test everything including portal login and data fetching:

```bash
python3 test_addon.py --test-portal --username YOUR_USERNAME --password YOUR_PASSWORD
```

**Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with your actual portal credentials.**

This runs:
- ✓ Portal login
- ✓ Fetching current meter readings
- ✓ HTML parsing
- ✓ Historical readings management
- ✓ Command file processing
- ✓ Complete sensor updates with all attributes

**Output Example:**
```
================================================================================
TEST 1: Portal Login
================================================================================
✓ Login successful!

================================================================================
TEST 2: Fetch Meter Readings
================================================================================
✓ Found 2 meter(s):

  Meter Number: 15093668
  Current Reading: 484 m³
  Recent Consumption: 162 m³
  Reading Type: Kundenangabe, Jahresabrechnung
  Reading Date: 2025-12-17 00:00:00
  Reference Date: 2025-12-31 00:00:00

  Meter Number: 2181453194
  Current Reading: 51 m³
  Recent Consumption: 10 m³
  Reading Type: Kundenangabe, Jahresabrechnung
  Reading Date: 2025-12-17 00:00:00
  Reference Date: 2025-12-31 00:00:00
```

### Understanding Test Results

The test script will show:

✓ **Green checkmarks** - Test passed
✗ **Red X marks** - Test failed
[INFO] **Info messages** - Informational
[MOCK] **Mock messages** - Simulated Home Assistant API calls

### What Gets Tested

| Test | Description | Offline Mode | Portal Mode |
|------|-------------|--------------|-------------|
| **Portal Login** | Authenticates with kundenportal.waz-nieplitz.de | ✗ Skipped | ✓ Runs |
| **Fetch Readings** | Retrieves and parses meter data from portal | ✗ Skipped | ✓ Runs |
| **Historical Mgmt** | Add/update/delete historical readings | ✓ Runs | ✓ Runs |
| **Command Processing** | File-based command interface | ✓ Runs | ✓ Runs |
| **Sensor Updates** | Creates sensor data with attributes | ✓ Runs | ✓ Runs |

## Option 2: Docker Container Testing

Test the add-on in an isolated Docker container that mimics the Home Assistant environment.

### Prerequisites

- Docker and Docker Compose installed

### Setup

1. Create a test data directory:
   ```bash
   mkdir -p test_data
   ```

2. Set your credentials (optional for full test):
   ```bash
   export TEST_USERNAME="your_username"
   export TEST_PASSWORD="your_password"
   ```

### Build and Run

1. Build the Docker image:
   ```bash
   docker-compose -f docker-compose.test.yml build
   ```

2. Start the test container:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

3. Run tests inside the container:
   ```bash
   # Offline test
   docker exec -it waz-nieplitz-test python3 /test_addon.py --offline

   # Full test (with portal)
   docker exec -it waz-nieplitz-test python3 /test_addon.py \
     --test-portal \
     --username YOUR_USERNAME \
     --password YOUR_PASSWORD
   ```

4. Check logs:
   ```bash
   docker-compose -f docker-compose.test.yml logs -f
   ```

5. Inspect test data:
   ```bash
   # View historical readings file
   cat test_data/historical_readings.json

   # Check if manual fetch trigger exists
   ls -la test_data/
   ```

6. Stop and cleanup:
   ```bash
   docker-compose -f docker-compose.test.yml down
   rm -rf test_data
   ```

### Testing Manual Fetch Trigger

While the container is running:

```bash
# Trigger a manual fetch
docker exec -it waz-nieplitz-test touch /data/manual_fetch

# Watch the logs to see it get processed
docker-compose -f docker-compose.test.yml logs -f
```

### Testing Historical Readings

```bash
# Add a historical reading
docker exec -it waz-nieplitz-test sh -c 'echo "{\"action\":\"add\",\"meter_number\":\"15093668\",\"date\":\"2020-12-31\",\"reading\":100,\"consumption\":150}" > /data/historical_command.json'

# Wait a moment, then check if it was processed
docker exec -it waz-nieplitz-test cat /data/historical_readings.json
```

## Option 3: Development Home Assistant Instance

For the most realistic testing environment, set up a separate development Home Assistant instance.

### Using Home Assistant Container

1. Create a development directory:
   ```bash
   mkdir -p ~/ha-dev/config
   mkdir -p ~/ha-dev/addons/waz-nieplitz-water-meter
   ```

2. Copy the add-on files:
   ```bash
   cp -r waz-nieplitz-water-meter/* ~/ha-dev/addons/waz-nieplitz-water-meter/
   ```

3. Start Home Assistant in development mode:
   ```bash
   docker run -d \
     --name ha-dev \
     --privileged \
     --restart=unless-stopped \
     -e TZ=Europe/Berlin \
     -v ~/ha-dev/config:/config \
     -v ~/ha-dev/addons:/addons \
     --network=host \
     ghcr.io/home-assistant/home-assistant:stable
   ```

4. Access at `http://localhost:8123`

5. Install the add-on:
   - Go to Settings → Add-ons
   - Reload add-ons store
   - Find "WAZ Nieplitz Water Meter" under Local add-ons
   - Install and configure

### Using Home Assistant OS in VirtualBox

1. Download Home Assistant OS image for VirtualBox
2. Create a new VM with the image
3. Access via web interface
4. Upload add-on via SSH or Samba share

## Test Scenarios

### Scenario 1: Test Historical Readings Feature

**Goal:** Verify you can add and manage historical readings

**Steps:**
1. Run offline test:
   ```bash
   python3 test_addon.py --offline
   ```

2. Verify output shows:
   - ✓ Historical readings added
   - ✓ Readings retrieved correctly
   - ✓ Updates work
   - ✓ Deletions work

**Expected:** All tests pass with green checkmarks

### Scenario 2: Test Portal Connection

**Goal:** Verify the add-on can connect to the portal and fetch real data

**Steps:**
1. Run portal test with your credentials:
   ```bash
   python3 test_addon.py --test-portal -u YOUR_USER -p YOUR_PASS
   ```

2. Verify output shows:
   - ✓ Login successful
   - ✓ Meters found (should match your actual meters)
   - ✓ Current readings displayed
   - ✓ Reference dates shown

**Expected:** Your actual meter numbers and readings appear

### Scenario 3: Test Data Persistence

**Goal:** Verify historical readings survive restarts

**Steps:**
1. Using Docker:
   ```bash
   # Start container
   docker-compose -f docker-compose.test.yml up -d

   # Add historical reading
   docker exec -it waz-nieplitz-test sh -c 'echo "{\"action\":\"add\",\"meter_number\":\"15093668\",\"date\":\"2020-12-31\",\"reading\":100}" > /data/historical_command.json'

   # Wait and verify
   sleep 5
   docker exec -it waz-nieplitz-test cat /data/historical_readings.json

   # Restart container
   docker-compose -f docker-compose.test.yml restart

   # Verify data still exists
   docker exec -it waz-nieplitz-test cat /data/historical_readings.json
   ```

**Expected:** Historical readings persist after restart

### Scenario 4: Test With Your Saved HTML

**Goal:** Test HTML parsing with your actual portal page

**Steps:**
1. You already have `Ablesungen.html` - let's test parsing it directly:
   ```python
   python3 -c "
   from bs4 import BeautifulSoup

   with open('Ablesungen.html', 'r') as f:
       soup = BeautifulSoup(f.read(), 'html.parser')

   table = soup.find('table', class_='listview ablesungen')
   rows = table.find_all('tr', class_='item')
   print(f'Found {len(rows)} readings in HTML')

   for row in rows[:2]:  # Show first 2
       meter = row.find('td', class_='zaehler').get_text(strip=True)
       stand = row.find('td', class_='stand').get_text(strip=True)
       print(f'  Meter: {meter}, Reading: {stand}')
   "
   ```

**Expected:** Shows your 2 meters and their readings

## Troubleshooting Tests

### Test script can't import modules

**Problem:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Portal login fails in test

**Problem:** `✗ Login failed - check your credentials`

**Possible causes:**
1. Wrong username/password
2. Portal is down/under maintenance
3. Network connectivity issues
4. Portal changed login mechanism

**Solution:**
- Verify credentials work on the website directly
- Check portal is accessible: `curl https://kundenportal.waz-nieplitz.de`
- Run with verbose logging (edit test script to set level=DEBUG)

### Docker container won't start

**Problem:** Container exits immediately

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.test.yml logs

# Try building fresh
docker-compose -f docker-compose.test.yml build --no-cache
docker-compose -f docker-compose.test.yml up
```

### Historical readings not persisting

**Problem:** Data disappears after restart

**Solution:**
- Check file permissions on test_data directory
- Verify JSON file is valid: `cat test_data/historical_readings.json | python3 -m json.tool`
- Check container volume mounts: `docker inspect waz-nieplitz-test`

## Continuous Testing During Development

If you're modifying the code:

1. **Watch mode with Python:**
   ```bash
   # Install watchdog
   pip3 install watchdog

   # Auto-run tests on file changes
   watchmedo shell-command \
     --patterns="*.py" \
     --command='python3 test_addon.py --offline' \
     .
   ```

2. **Quick iteration loop:**
   ```bash
   # Edit run.py
   # Then immediately test
   python3 test_addon.py --offline && echo "✓ Tests passed"
   ```

## Test Coverage

Current test coverage:

| Feature | Tested | Notes |
|---------|--------|-------|
| Portal login | ✓ | Requires credentials |
| HTML parsing | ✓ | Uses real portal data |
| Meter identification | ✓ | Tests main/garden logic |
| Historical add | ✓ | Full CRUD operations |
| Historical update | ✓ | Overwrites existing dates |
| Historical delete | ✓ | Removes specific entries |
| Command file add | ✓ | JSON file processing |
| Command file delete | ✓ | JSON file processing |
| Sensor creation | ✓ | Mock HA API |
| Sensor attributes | ✓ | All attributes verified |
| Data persistence | ✓ | File-based storage |
| Manual fetch trigger | ✓ | File creation detection |
| Date format parsing | ✓ | ISO and German formats |

## Safety Notes

⚠️ **Important:**
- Test credentials are never stored in files (passed as arguments)
- Test data is created in temporary directories
- Docker tests are isolated from production
- No changes are made to the actual portal
- Test script only reads from the portal (when enabled)

## Next Steps After Testing

Once all tests pass:

1. **Install in development HA** - Test in a real (but non-production) Home Assistant
2. **Verify integrations** - Check Energy Dashboard integration
3. **Test automations** - Create test automations with the sensors
4. **Monitor logs** - Watch add-on logs for any issues
5. **Gradual rollout** - Start with one meter, then add more
6. **Backup first** - Backup your HA config before production install

## Getting Help

If tests fail:

1. Check the test output carefully - it shows exactly what failed
2. Review the add-on logs (if using Docker/HA)
3. Verify your portal credentials work on the website
4. Check the GitHub issues for similar problems
5. Include test output when reporting issues
