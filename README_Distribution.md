# Poker Payout Calculator

A GUI application for calculating poker tournament payouts with player payment tracking.

## Features
- Configure number of players (3-30)
- Set buy-in, food pool, and bounty amounts
- Customizable payout weights
- Player payment tracking with checkboxes for buy-in, food, bounty
- Real-time calculation of payouts and bank status

## Running the Application

### Option 1: Run from Source (requires Python)
1. Install Python 3.7+ if not already installed
2. Double-click `run_calculator.bat`

### Option 2: Standalone Executable
1. Double-click `build_standalone.bat` to create a standalone executable
2. The executable will be created in the `dist` folder
3. Share the `PokerPayoutCalculator.exe` file - it runs without Python installation

## Distribution
The standalone executable (`PokerPayoutCalculator.exe`) can be shared with anyone and will run on any Windows computer without requiring Python or any dependencies to be installed.

## Files
- `poker_payout_calculator.py` - Main application code
- `requirements.txt` - Python dependencies
- `run_calculator.bat` - Run from source
- `build_standalone.bat` - Build standalone executable
- `PokerPayoutCalculator.spec` - PyInstaller configuration
- `version_info.txt` - Executable version information

## Building
To create the standalone executable:
1. Run `build_standalone.bat`
2. The executable will be in the `dist` folder
3. The executable is completely self-contained and portable

The executable is typically 30-50MB and includes everything needed to run the application.
