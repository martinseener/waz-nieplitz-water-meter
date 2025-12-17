# Quick Start: Testing the Add-on

This is a quick guide to test the add-on **without installing it in your production Home Assistant**.

## Fastest Way to Test (2 minutes)

### Option 1: Offline Test (No Portal Connection)

Tests all local features without connecting to the portal:

```bash
# 1. Navigate to the add-on directory
cd waz-nieplitz-water-meter

# 2. Install dependencies (one time only)
pip3 install -r requirements.txt

# 3. Run the test script
./run_tests.sh
# Select option 1 (Offline mode)
```

**What this tests:**
- ✓ Historical readings (add/update/delete)
- ✓ Command file processing
- ✓ Sensor data generation
- ✓ Data persistence

**Expected result:** All tests show green ✓ checkmarks

### Option 2: Full Test (With Your Portal Credentials)

Tests everything including actual portal connection:

```bash
# Run the interactive test script
./run_tests.sh
# Select option 2 (Full test)
# Enter your portal username and password when prompted
```

**What this additionally tests:**
- ✓ Portal login with your credentials
- ✓ Fetching your actual meter readings
- ✓ HTML parsing of real data
- ✓ Complete sensor updates with real values

**Expected result:** Shows your actual meter numbers and current readings

## What You'll See

### Offline Test Output Example

```
================================================================================
WAZ NIEPLITZ WATER METER ADD-ON TEST SUITE
================================================================================
Started at: 2025-12-17 21:30:00

[SKIPPED] Portal tests (use --test-portal to enable)

================================================================================
TEST 3: Historical Readings Management
================================================================================

1. Adding historical readings...
  ✓ Added: Meter 15093668, 2019-12-31, 50 m³
  ✓ Added: Meter 15093668, 2020-12-31, 100 m³
  ✓ Added: Meter 15093668, 2021-12-31, 150 m³

2. Retrieving historical readings...

  Meter 15093668: 3 reading(s)
    - 2019-12-31T00:00:00: 50 m³ (consumption: 140 m³)
    - 2020-12-31T00:00:00: 100 m³ (consumption: 150 m³)
    - 2021-12-31T00:00:00: 150 m³ (consumption: 160 m³)

✓ Historical readings tests completed!

================================================================================
TEST 5: Command File Processing
================================================================================

1. Testing ADD command via file...
  ✓ ADD command processed successfully
    Total readings: 1

2. Testing DELETE command via file...
  ✓ DELETE command processed successfully
    Remaining readings: 0

✓ Command file processing tests completed!

================================================================================
TEST SUITE COMPLETED
================================================================================
```

### Full Test Output Example (With Portal)

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
  Reference Date: 2025-12-31 00:00:00

  Meter Number: 2181453194
  Current Reading: 51 m³
  Recent Consumption: 10 m³
  Reading Type: Kundenangabe, Jahresabrechnung
  Reference Date: 2025-12-31 00:00:00

[... plus all offline tests ...]
```

## Alternative: Manual Python Command

If the shell script doesn't work:

```bash
# Offline test
python3 test_addon.py --offline

# Full test with portal
python3 test_addon.py --test-portal --username YOUR_USER --password YOUR_PASS
```

## Testing Your Saved HTML File

You already have `Ablesungen.html` from the portal. Test the parser on it:

```bash
./run_tests.sh
# Select option 4 (HTML parsing test)
```

This will show you exactly what data the add-on extracts from your saved portal page.

## Docker Testing (Optional)

For a more realistic test in an isolated environment:

```bash
# Build and run
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up -d

# Run tests
docker exec -it waz-nieplitz-test python3 /test_addon.py --offline

# View logs
docker-compose -f docker-compose.test.yml logs -f

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"

**Fix:**
```bash
pip3 install -r requirements.txt
```

### "Permission denied" when running test script

**Fix:**
```bash
chmod +x run_tests.sh test_addon.py
```

### Portal login fails

**Check:**
1. Credentials work on https://kundenportal.waz-nieplitz.de
2. Portal is accessible (not under maintenance)
3. Try again in a few minutes

## What Next?

Once tests pass:

1. ✅ Tests successful → Safe to install in a development HA instance
2. ✅ Dev instance works → Safe to install in production
3. ✅ Production install → Configure and start the add-on

**See full documentation:**
- [TESTING.md](TESTING.md) - Complete testing guide
- [INSTALLATION.md](INSTALLATION.md) - Installation instructions
- [README.md](README.md) - Full add-on documentation

## Quick Reference

| Command | What it tests | Time | Portal needed? |
|---------|---------------|------|----------------|
| `./run_tests.sh` → 1 | Local features only | 30s | No |
| `./run_tests.sh` → 2 | Everything | 1min | Yes |
| `./run_tests.sh` → 3 | Docker environment | 2min | No |
| `./run_tests.sh` → 4 | Your saved HTML | 10s | No |

## Safety

✅ Tests are completely safe:
- No changes to your HA installation
- No changes to the portal
- Only reads data (when portal test enabled)
- Temporary files automatically cleaned up
- Credentials never saved to disk
