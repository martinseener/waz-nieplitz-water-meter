# Historical Water Meter Readings

The WAZ Nieplitz portal only provides readings from the last 2 years. This feature allows you to manually add historical readings from previous years to maintain a complete water usage history in Home Assistant.

## How It Works

Historical readings are:
- Stored in `/data/historical_readings.json` in the add-on's data directory
- Automatically loaded when the add-on starts
- Included in the sensor attributes for reference
- Preserved across add-on restarts and updates
- Never overwritten by portal data

## Adding Historical Readings

There are multiple ways to add historical readings:

### Method 1: Using Shell Commands (Recommended)

#### Setup

Add these shell commands to your `configuration.yaml`:

```yaml
shell_command:
  add_water_reading: >
    echo '{"action":"add","meter_number":"{{ meter_number }}","date":"{{ date }}","reading":{{ reading }},"consumption":{{ consumption }},"reading_type":"{{ reading_type }}"}'
    > /addons/waz-nieplitz-water-meter/data/historical_command.json
```

#### Usage

Create scripts for easy access (in `scripts.yaml` or via UI):

```yaml
add_main_water_reading:
  alias: Add Main Water Meter Reading
  fields:
    date:
      description: Reading date (YYYY-MM-DD or DD.MM.YYYY)
      example: "2020-12-31"
    reading:
      description: Meter reading in m³
      example: 100
    consumption:
      description: Consumption for this period (optional)
      example: 150
  sequence:
    - service: shell_command.add_water_reading
      data:
        meter_number: "15093668"  # Your main meter number
        date: "{{ date }}"
        reading: "{{ reading }}"
        consumption: "{{ consumption | default(0) }}"
        reading_type: "Manual Historical Entry"
    - service: persistent_notification.create
      data:
        title: Water Meter
        message: "Historical reading added for {{ date }}"

add_garden_water_reading:
  alias: Add Garden Water Meter Reading
  fields:
    date:
      description: Reading date (YYYY-MM-DD or DD.MM.YYYY)
      example: "2020-12-31"
    reading:
      description: Meter reading in m³
      example: 20
    consumption:
      description: Consumption for this period (optional)
      example: 25
  sequence:
    - service: shell_command.add_water_reading
      data:
        meter_number: "2181453194"  # Your garden meter number
        date: "{{ date }}"
        reading: "{{ reading }}"
        consumption: "{{ consumption | default(0) }}"
        reading_type: "Manual Historical Entry"
    - service: persistent_notification.create
      data:
        title: Water Meter
        message: "Historical reading added for {{ date }}"
```

#### Dashboard Example

Add a button to your dashboard:

```yaml
type: button
tap_action:
  action: call-service
  service: script.add_main_water_reading
  data:
    date: "2020-12-31"
    reading: 100
    consumption: 150
name: Add 2020 Reading
icon: mdi:water-plus
```

Or create an input form with helpers:

```yaml
type: entities
entities:
  - entity: input_text.water_reading_date
  - entity: input_number.water_reading_value
  - entity: input_number.water_reading_consumption
  - type: button
    name: Add Reading
    tap_action:
      action: call-service
      service: script.add_main_water_reading
      data:
        date: "{{ states('input_text.water_reading_date') }}"
        reading: "{{ states('input_number.water_reading_value') | float }}"
        consumption: "{{ states('input_number.water_reading_consumption') | float }}"
```

### Method 2: Direct JSON File Creation

If you have SSH or file editor access:

1. Create a file `/addons/waz-nieplitz-water-meter/data/historical_command.json`
2. Add this content:

```json
{
  "action": "add",
  "meter_number": "15093668",
  "date": "2020-12-31",
  "reading": 100,
  "consumption": 150,
  "reading_type": "Manual Historical Entry"
}
```

3. The add-on will process this within 60 seconds and delete the file
4. Check the add-on logs for confirmation

### Method 3: Manually Edit the Historical Readings File

**Advanced users only** - directly edit `/data/historical_readings.json`:

```json
{
  "15093668": [
    {
      "date": "2019-12-31T00:00:00",
      "reading": 50.0,
      "consumption": 140.0,
      "reading_type": "Manual Historical Entry",
      "manual": true
    },
    {
      "date": "2020-12-31T00:00:00",
      "reading": 100.0,
      "consumption": 150.0,
      "reading_type": "Manual Historical Entry",
      "manual": true
    }
  ],
  "2181453194": [
    {
      "date": "2019-12-31T00:00:00",
      "reading": 5.0,
      "consumption": 15.0,
      "reading_type": "Manual Historical Entry",
      "manual": true
    }
  ]
}
```

**Important:** Restart the add-on after manual editing.

## Deleting Historical Readings

To delete a specific historical reading:

```yaml
shell_command:
  delete_water_reading: >
    echo '{"action":"delete","meter_number":"{{ meter_number }}","date":"{{ date }}"}'
    > /addons/waz-nieplitz-water-meter/data/historical_command.json
```

Then create a script:

```yaml
delete_water_reading:
  alias: Delete Water Meter Reading
  fields:
    meter_number:
      description: Meter number
      example: "15093668"
    date:
      description: Reading date (YYYY-MM-DD or DD.MM.YYYY)
      example: "2020-12-31"
  sequence:
    - service: shell_command.delete_water_reading
      data:
        meter_number: "{{ meter_number }}"
        date: "{{ date }}"
```

## Viewing Historical Readings

### In Developer Tools

1. Go to **Developer Tools** → **States**
2. Search for `sensor.waz_nieplitz_water_main` or `sensor.waz_nieplitz_water_garden`
3. View attributes:
   - `historical_readings`: List of all manual historical readings
   - `historical_count`: Number of historical readings

### Example Attributes

```yaml
historical_readings:
  - date: "2019-12-31T00:00:00"
    reading: 50
    consumption: 140
    reading_type: "Manual Historical Entry"
    manual: true
  - date: "2020-12-31T00:00:00"
    reading: 100
    consumption: 150
    reading_type: "Manual Historical Entry"
    manual: true
  - date: "2021-12-31T00:00:00"
    reading: 150
    consumption: 160
    reading_type: "Manual Historical Entry"
    manual: true
historical_count: 3
```

## Complete Setup Example

Here's a complete example for adding historical readings via the UI:

### 1. Create Input Helpers

Go to **Settings** → **Devices & Services** → **Helpers** and create:

- **Input Text**: `input_text.water_meter_number`
  - Name: "Meter Number"
  - Initial value: "15093668"

- **Input Text**: `input_text.water_reading_date`
  - Name: "Reading Date"
  - Pattern: `\d{4}-\d{2}-\d{2}`

- **Input Number**: `input_number.water_reading_value`
  - Name: "Reading Value (m³)"
  - Min: 0, Max: 10000, Step: 1

- **Input Number**: `input_number.water_reading_consumption`
  - Name: "Consumption (m³)"
  - Min: 0, Max: 1000, Step: 1

### 2. Add Shell Command

In `configuration.yaml`:

```yaml
shell_command:
  add_water_reading: >
    echo '{"action":"add","meter_number":"{{ meter_number }}","date":"{{ date }}","reading":{{ reading }},"consumption":{{ consumption }},"reading_type":"Manual Historical Entry"}'
    > /addons/waz-nieplitz-water-meter/data/historical_command.json
```

### 3. Create Script

In `scripts.yaml`:

```yaml
add_historical_water_reading:
  alias: Add Historical Water Reading
  sequence:
    - service: shell_command.add_water_reading
      data:
        meter_number: "{{ states('input_text.water_meter_number') }}"
        date: "{{ states('input_text.water_reading_date') }}"
        reading: "{{ states('input_number.water_reading_value') | float }}"
        consumption: "{{ states('input_number.water_reading_consumption') | float }}"
    - delay:
        seconds: 2
    - service: persistent_notification.create
      data:
        title: Historical Water Reading
        message: "Added reading for {{ states('input_text.water_reading_date') }}"
    - service: input_text.set_value
      target:
        entity_id: input_text.water_reading_date
      data:
        value: ""
    - service: input_number.set_value
      target:
        entity_id: input_number.water_reading_value
      data:
        value: 0
    - service: input_number.set_value
      target:
        entity_id: input_number.water_reading_consumption
      data:
        value: 0
```

### 4. Create Dashboard Card

```yaml
type: entities
title: Add Historical Water Reading
entities:
  - entity: input_text.water_meter_number
  - entity: input_text.water_reading_date
  - entity: input_number.water_reading_value
  - entity: input_number.water_reading_consumption
  - type: button
    name: Add Reading
    icon: mdi:water-plus
    action_name: Add
    tap_action:
      action: call-service
      service: script.add_historical_water_reading
```

## Best Practices

1. **Use consistent date format**: Prefer ISO format (YYYY-MM-DD) for clarity
2. **Add readings chronologically**: Start from oldest to newest
3. **Include consumption if known**: Helps with historical analysis
4. **Verify in logs**: Always check add-on logs after adding readings
5. **Backup the file**: Periodically backup `/data/historical_readings.json`
6. **One reading per year**: Typically you only need annual readings

## Troubleshooting

### Historical readings not appearing

1. Check add-on logs for errors
2. Verify the meter number matches exactly (check sensor attributes)
3. Ensure date format is correct (YYYY-MM-DD or DD.MM.YYYY)
4. Wait 60 seconds for command file to be processed
5. Check that historical_command.json was deleted (means it was processed)

### Shell command not working

Try alternative paths:
```yaml
shell_command:
  # Alternative path option 1
  add_water_reading: >
    echo '...' > /data/historical_command.json

  # Alternative path option 2
  add_water_reading: >
    echo '...' > /config/addons_config/waz-nieplitz-water-meter/historical_command.json
```

### Reading was added but not visible

1. Trigger a manual fetch to update sensors
2. Check Developer Tools → States for the sensor
3. Look at the `historical_readings` attribute
4. Verify the date format in `/data/historical_readings.json`

## Command Reference

### Add Reading Command Structure

```json
{
  "action": "add",
  "meter_number": "15093668",        // Required: Your meter number
  "date": "2020-12-31",              // Required: Date (YYYY-MM-DD or DD.MM.YYYY)
  "reading": 100.5,                  // Required: Meter reading in m³
  "consumption": 150.0,              // Optional: Consumption in m³
  "reading_type": "Manual Entry"     // Optional: Description
}
```

### Delete Reading Command Structure

```json
{
  "action": "delete",
  "meter_number": "15093668",        // Required: Your meter number
  "date": "2020-12-31"               // Required: Date to delete
}
```

## Example: Adding 5 Years of Historical Data

```yaml
script:
  load_historical_water_data:
    alias: Load 5 Years Historical Water Data
    sequence:
      # 2019
      - service: shell_command.add_water_reading
        data:
          meter_number: "15093668"
          date: "2019-12-31"
          reading: 50
          consumption: 140
      - delay: 2

      # 2020
      - service: shell_command.add_water_reading
        data:
          meter_number: "15093668"
          date: "2020-12-31"
          reading: 100
          consumption: 150
      - delay: 2

      # 2021
      - service: shell_command.add_water_reading
        data:
          meter_number: "15093668"
          date: "2021-12-31"
          reading: 150
          consumption: 160
      - delay: 2

      # 2022
      - service: shell_command.add_water_reading
        data:
          meter_number: "15093668"
          date: "2022-12-31"
          reading: 200
          consumption: 155
      - delay: 2

      # Notification
      - service: persistent_notification.create
        data:
          title: Historical Water Data
          message: "Loaded 4 years of historical data"
```

## Integration with Energy Dashboard

Historical readings are stored in sensor attributes for reference but are not directly integrated into the Energy Dashboard statistics. The Energy Dashboard will use the current meter reading as the baseline and track changes from there.

To get historical data into the Energy Dashboard, you would need to:
1. Use the Home Assistant Statistics database directly (advanced)
2. Or accept that the Energy Dashboard shows data from when you first added the sensor

The historical readings in attributes serve as a reference for your complete water usage history.
