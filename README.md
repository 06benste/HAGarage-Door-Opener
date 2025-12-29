# Garage Door Opener Integration for Home Assistant

A Home Assistant custom integration for controlling a garage door using dual relays and two position sensors. This integration creates a cover entity that can be controlled from Home Assistant's UI, automations, and voice assistants.

## Features

- **Dual Relay Control**: Uses separate momentary switches for open/up and close/down operations
- **Flexible Position Sensing**: Works with any contact sensor that provides open/closed or on/off values (e.g., IKEA Parasoll, door sensors, window sensors)
- **Configurable Sensor States**: Supports sensors that use 'on'/'off', 'open'/'closed', or any combination
- **Movement Timeout Detection**: Monitors door movement and detects if the door gets stuck
- **Stuck Door Notifications**: Optional persistent notifications when the door doesn't complete movement in the expected time
- **UI-Based Configuration**: Easy setup through Home Assistant's integration UI - no YAML editing required!

## Requirements

- Home Assistant 2023.1 or later
- Two binary sensors (any contact sensor - door sensors, window sensors, etc.)
- Two switch entities (momentary/inching switches, e.g., ZG-005-RF relay channels)

## Installation

### Method 1: HACS (Home Assistant Community Store) - Recommended

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots menu (⋮) in the top right
4. Select **Custom repositories**
5. Add this repository:
   - **Repository**: `https://github.com/06benste/HAGarage-Door-Opener`
   - **Category**: Integration
6. Click **ADD**
7. Go back to **Integrations**
8. Click **Explore & Download Repositories**
9. Search for "Garage Door Opener"
10. Click **Download**
11. Restart Home Assistant

### Method 2: Manual Installation

1. Download or clone this repository
2. Copy the `custom_components/garage_door_opener` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. The integration will be available in **Settings** → **Devices & Services** → **Add Integration**

## Configuration

### Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for "Garage Door Opener"
4. Click on it and fill in the configuration:
   - **Garage Door Name**: Enter a friendly name (default: "Garage Door")
   - **Closed Position Sensor**: Select your closed position binary sensor
   - **Closed Sensor State**: Select the state your sensor shows when door is closed (`off`, `on`, `closed`, or `open` - default: `off`)
   - **Open Position Sensor**: Select your open position binary sensor
   - **Open Sensor State**: Select the state your sensor shows when door is open (`off`, `on`, `closed`, or `open` - default: `off`)
   - **Open/Up Relay Switch**: Select your switch that opens the door
   - **Close/Down Relay Switch**: Select your switch that closes the door
   - **Time to Fully Open**: Enter expected time in seconds (default: 20)
   - **Time to Fully Close**: Enter expected time in seconds (default: 25)
   - **Enable Stuck Door Notification**: Toggle to enable/disable notifications (default: enabled)
5. Click **SUBMIT**

The integration will:
- Create a cover entity for your garage door
- Handle movement timing internally (no timer helper needed)
- Monitor for stuck doors and send notifications (if enabled)

## Usage

Once configured, you'll have a new cover entity (e.g., `cover.garage_door_<name>`) that you can:

- Control from the Home Assistant UI
- Use in automations
- Control via voice assistants (Google Assistant, Alexa, etc.)
- Monitor in dashboards

The cover entity will automatically update its state based on your position sensors, and if enabled, the automation will notify you if the door doesn't complete movement in the expected time.

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| Garage Door Name | Friendly name for the cover | "Garage Door" |
| Closed Position Sensor | Binary sensor for closed position | Required |
| Closed Sensor State | State value when door is closed | `off` |
| Open Position Sensor | Binary sensor for open position | Required |
| Open Sensor State | State value when door is open | `off` |
| Open/Up Relay Switch | Switch that opens the door | Required |
| Close/Down Relay Switch | Switch that closes the door | Required |
| Time to Fully Open | Expected open time in seconds | 20 |
| Time to Fully Close | Expected close time in seconds | 25 |
| Enable Stuck Door Notification | Enable timeout notifications | true |

## Troubleshooting

### Integration Not Appearing

- Ensure you've copied the files to `custom_components/garage_door_opener/`
- Restart Home Assistant completely (not just reload)
- Check the logs for any errors

### Cover Entity Not Working

- Verify your position sensors are working correctly
- Check that sensor state values are correctly configured
- Ensure sensor entity IDs are correctly selected
- Verify that the "Closed Sensor State" and "Open Sensor State" match what your sensors actually show

### Door Not Responding to Commands

- Verify your relay switches are working
- Check that switches are configured as momentary/inching switches
- Ensure switch entity IDs are correctly selected

### Stuck Door Notifications Not Appearing

- Verify "Enable Stuck Door Notification" is enabled in the integration configuration
- Ensure the door movement times are set correctly
- Check that the door actually takes longer than the configured time to move
- Check Home Assistant logs for any errors

## Supported Devices

This integration has been tested with:
- **Relays**: ZG-005-RF inching channels
- **Sensors**: IKEA Parasoll contact sensors, Aqara door sensors
- Other compatible devices should work as well

## File Structure

```
garageblueprint/
├── custom_components/
│   └── garage_door_opener/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── cover.py
│       ├── const.py
│       └── strings.json
├── blueprint.yaml              # Legacy blueprint (for stuck notification only)
├── template_cover_example.yaml # Legacy YAML example (for reference)
├── README.md
├── LICENSE
└── .gitignore
```

## Migration from Blueprint/YAML

If you were using the previous blueprint/YAML configuration:

1. **Remove the old YAML configuration** from your `configuration.yaml`
2. **Remove the old template cover** (it will be replaced by the integration)
3. **Install this integration** using the methods above
4. **Configure through the UI** - much easier than editing YAML!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on GitHub
3. Check Home Assistant community forums

## Changelog

### Version 1.0.0
- Initial integration release
- UI-based configuration
- Automatic cover entity creation
- Automatic stuck door automation creation
- Support for flexible sensor states
- Dual relay control with momentary switches
