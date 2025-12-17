#!/bin/bash
# Install WAZ Nieplitz Water Meter add-on to local Home Assistant instance

set -e

echo "=================================================="
echo "WAZ Nieplitz Water Meter - Local HA Installation"
echo "=================================================="
echo ""

# Configuration
HA_HOST="homeassistant.local"
ADDON_NAME="waz-nieplitz-water-meter"
SOURCE_DIR="/Users/mseener/Development/local/waz-nieplitz-water-meter"

# Files to copy (production files only)
REQUIRED_FILES=(
    "config.json"
    "run.py"
    "Dockerfile"
    "build.yaml"
    "requirements.txt"
    "README.md"
    "CHANGELOG.md"
    "INSTALLATION.md"
    "MANUAL_FETCH_SETUP.md"
    "HISTORICAL_READINGS.md"
    "ICON.md"
    ".gitignore"
)

echo "This script will install the add-on to your local Home Assistant at:"
echo "  http://${HA_HOST}:8123"
echo ""
echo "Choose installation method:"
echo "  1) Samba (easiest - requires Samba add-on installed in HA)"
echo "  2) SCP/SSH (requires Terminal & SSH add-on installed in HA)"
echo "  3) Show manual instructions"
echo ""
read -p "Choice [1]: " method
method=${method:-1}

case $method in
    1)
        echo ""
        echo "Installing via Samba..."
        echo ""

        # Check if Samba mount exists
        SAMBA_MOUNT="/Volumes/addons"

        if [ ! -d "$SAMBA_MOUNT" ]; then
            echo "Samba share not mounted. Attempting to connect..."
            echo ""
            echo "Opening Finder connection dialog..."
            echo "Please enter credentials when prompted:"
            echo "  Server: smb://${HA_HOST}"
            echo "  Username: martin"
            echo "  Password: martin"
            echo ""

            open "smb://${HA_HOST}"

            echo "Press Enter after you've connected to the Samba share..."
            read

            # Wait a moment for mount
            sleep 2

            if [ ! -d "$SAMBA_MOUNT" ]; then
                echo "ERROR: Samba share still not mounted at $SAMBA_MOUNT"
                echo ""
                echo "Please manually:"
                echo "1. In Finder, press Cmd+K"
                echo "2. Connect to: smb://${HA_HOST}"
                echo "3. Login with username 'martin' and password 'martin'"
                echo "4. Run this script again"
                exit 1
            fi
        fi

        # Create destination directory
        DEST_DIR="${SAMBA_MOUNT}/${ADDON_NAME}"

        echo "Creating add-on directory: ${DEST_DIR}"
        mkdir -p "$DEST_DIR"

        # Copy files
        echo "Copying files..."
        for file in "${REQUIRED_FILES[@]}"; do
            if [ -f "${SOURCE_DIR}/${file}" ]; then
                echo "  Copying ${file}..."
                cp "${SOURCE_DIR}/${file}" "${DEST_DIR}/"
            else
                echo "  Warning: ${file} not found, skipping"
            fi
        done

        echo ""
        echo "✓ Files copied successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Go to http://${HA_HOST}:8123"
        echo "2. Settings → Add-ons"
        echo "3. Click ⋮ (three dots) → Check for updates"
        echo "4. Find 'WAZ Nieplitz Water Meter' under Local add-ons"
        echo "5. Click Install"
        ;;

    2)
        echo ""
        echo "Installing via SCP/SSH..."
        echo ""

        read -p "SSH password for root@${HA_HOST} [martin]: " ssh_pass
        ssh_pass=${ssh_pass:-martin}

        # Create remote directory
        echo "Creating remote directory..."
        ssh "root@${HA_HOST}" "mkdir -p /addons/${ADDON_NAME}" || {
            echo ""
            echo "ERROR: Could not connect via SSH"
            echo ""
            echo "Make sure:"
            echo "1. Terminal & SSH add-on is installed in Home Assistant"
            echo "2. The add-on is started"
            echo "3. You set a password in the add-on configuration"
            exit 1
        }

        # Copy files
        echo "Copying files..."
        for file in "${REQUIRED_FILES[@]}"; do
            if [ -f "${SOURCE_DIR}/${file}" ]; then
                echo "  Copying ${file}..."
                scp "${SOURCE_DIR}/${file}" "root@${HA_HOST}:/addons/${ADDON_NAME}/"
            fi
        done

        # Set permissions
        echo "Setting permissions..."
        ssh "root@${HA_HOST}" "chmod 755 /addons/${ADDON_NAME} && chmod 755 /addons/${ADDON_NAME}/run.py && chmod 644 /addons/${ADDON_NAME}/*"

        echo ""
        echo "✓ Files copied successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Go to http://${HA_HOST}:8123"
        echo "2. Settings → Add-ons"
        echo "3. Click ⋮ (three dots) → Check for updates"
        echo "4. Find 'WAZ Nieplitz Water Meter' under Local add-ons"
        echo "5. Click Install"
        ;;

    3)
        echo ""
        echo "Manual Installation Instructions"
        echo "================================="
        echo ""
        echo "See LOCAL_HA_INSTALL.md for complete instructions."
        echo ""
        echo "Quick summary:"
        echo ""
        echo "Method 1: Samba"
        echo "  1. Install Samba share add-on in HA"
        echo "  2. Connect from Mac: Finder → Cmd+K → smb://${HA_HOST}"
        echo "  3. Copy files to /addons/${ADDON_NAME}/"
        echo ""
        echo "Method 2: SSH"
        echo "  1. Install Terminal & SSH add-on in HA"
        echo "  2. Use SCP to copy files:"
        echo "     scp -r ${SOURCE_DIR}/* root@${HA_HOST}:/addons/${ADDON_NAME}/"
        echo ""
        echo "Files to copy:"
        for file in "${REQUIRED_FILES[@]}"; do
            echo "  - ${file}"
        done
        echo ""
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "Installation complete!"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  After installing the add-on in HA, configure it with:"
echo "  - username: your_portal_username"
echo "  - password: your_portal_password"
echo "  - update_interval: 2592000 (30 days)"
echo ""
echo "Documentation:"
echo "  See README.md for usage instructions"
echo "  See MANUAL_FETCH_SETUP.md for manual fetch setup"
echo "  See HISTORICAL_READINGS.md for historical data"
echo ""
