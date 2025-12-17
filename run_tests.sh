#!/bin/bash
# Quick test runner script for WAZ Nieplitz Water Meter Add-on

set -e

echo "=================================================="
echo "WAZ Nieplitz Water Meter Add-on - Test Runner"
echo "=================================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✓ Dependencies installed"
fi

echo ""
echo "Select test mode:"
echo "  1) Offline mode (test local features only)"
echo "  2) Full test (requires portal credentials)"
echo "  3) Docker test"
echo "  4) Quick HTML parsing test"
echo ""
read -p "Choice [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo ""
        echo "Running offline tests..."
        python3 test_addon.py --offline
        ;;
    2)
        echo ""
        read -p "Portal username: " username
        read -sp "Portal password: " password
        echo ""
        echo "Running full tests..."
        python3 test_addon.py --test-portal --username "$username" --password "$password"
        ;;
    3)
        echo ""
        if ! command -v docker &> /dev/null; then
            echo "ERROR: Docker is required but not found"
            exit 1
        fi

        echo "Building Docker test environment..."
        docker-compose -f docker-compose.test.yml build

        echo "Running Docker tests..."
        docker-compose -f docker-compose.test.yml up -d

        echo "Executing tests in container..."
        docker exec -it waz-nieplitz-test python3 /test_addon.py --offline

        echo ""
        read -p "Keep container running? [y/N]: " keep
        if [[ ! $keep =~ ^[Yy]$ ]]; then
            echo "Stopping container..."
            docker-compose -f docker-compose.test.yml down
        fi
        ;;
    4)
        echo ""
        if [ ! -f "Ablesungen.html" ]; then
            echo "ERROR: Ablesungen.html not found"
            echo "Please save a copy of the portal page as Ablesungen.html"
            exit 1
        fi

        echo "Parsing Ablesungen.html..."
        python3 << 'EOF'
from bs4 import BeautifulSoup

with open('Ablesungen.html', 'r') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

table = soup.find('table', class_='listview ablesungen')
if not table:
    print("ERROR: Could not find readings table in HTML")
    exit(1)

rows = table.find_all('tr', class_='item')
print(f"\n✓ Found {len(rows)} readings in saved HTML file\n")

meters = {}
for row in rows:
    meter_cell = row.find('td', class_='zaehler')
    if meter_cell:
        meter_number = meter_cell.get_text(strip=True).replace('Zähler', '')
        stand_cell = row.find('td', class_='stand')
        stand = stand_cell.get_text(strip=True).replace('Stand', '') if stand_cell else '0'
        stichtag_cell = row.find('td', class_='stichtag')
        stichtag = stichtag_cell.get_text(strip=True).replace('Stichtag', '') if stichtag_cell else ''

        if meter_number not in meters:
            meters[meter_number] = []
        meters[meter_number].append((stichtag, stand))

for meter_number, readings in meters.items():
    print(f"Meter {meter_number}:")
    # Show only the most recent reading
    if readings:
        latest = readings[0]
        print(f"  Latest: {latest[0]} -> {latest[1]} m³")
    print(f"  Total readings in file: {len(readings)}")
    print()

print("✓ HTML parsing working correctly!")
EOF
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "Tests completed!"
echo "=================================================="
