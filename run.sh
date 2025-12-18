#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start the WAZ Nieplitz Water Meter add-on
# ==============================================================================

bashio::log.info "Starting WAZ Nieplitz Water Meter..."

# Run the Python application
exec python3 -u /run.py
