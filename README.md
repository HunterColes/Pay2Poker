# 🃏 Poker Payout Calculator

A sleek, interactive GUI application for calculating poker tournament payouts with customizable weights, food pool, and bounty pool features.

## Features

### 🎨 Modern Poker-Themed Design
- **Dark poker green color scheme** that mimics a real poker table
- **Gold accents** for highlights and important information
- **Clean, professional layout** with left controls and right results

### 🎚️ Interactive Controls
- **Real-time updates** - no calculate button needed!
- **Player slider** supporting 3-30 players
- **Instant payout calculation** as you adjust any value
- **Responsive interface** that updates immediately

### 💰 Flexible Pool Management
- **Buy-in pool** - main tournament prize pool
- **Food pool** - separate fund for food and drinks
- **Bounty pool** - head-to-head knockout rewards

### ⚖️ Customizable Payout Weights
- **Default weights**: [35, 20, 15, 10, 8, 6, 3, 2, 1] for top 9 positions
- **Interactive weights editor** in a separate clean window
- **Add/remove positions** dynamically
- **Real-time weight adjustment** with immediate payout updates
- **Reset to defaults** option

### 📊 Smart Payout Logic
- **Automatic position calculation**: Number of paid positions = ⌈Players ÷ 3⌉
- **Proportional payouts** based on weight distribution
- **Clear breakdown** of all pools and totals

## Installation

1. Install required dependencies:
```bash
pip install customtkinter
```

2. Run the application:
```bash
python poker_payout_calculator.py
```

Or double-click `run_calculator.bat` on Windows.

## Usage

### Basic Setup
1. **Adjust player count** using the slider (3-30 players)
2. **Set buy-in amount** per player
3. **Configure food pool** contribution per player
4. **Set bounty amount** per player for knockouts

### Customizing Weights
1. Click **"🔧 Customize Weights"** to open the weights editor
2. **Adjust individual weights** for each position
3. **Add or remove positions** as needed
4. **Changes apply instantly** to the main calculator

### Understanding Results
The right panel shows:
- **🏆 Tournament Overview** - total pools and collections
- **🏅 Main Tournament Payouts** - position-based prize distribution
- **💡 Additional Pools** - food and bounty pool information
- **📊 Summary** - payout totals and remaining funds

## Examples

### 9 Players, $20 Buy-in
- **Players**: 9
- **Buy-in**: $20/player
- **Food**: $5/player  
- **Bounty**: $2/player
- **Positions paid**: 3 (⌈9÷3⌉)
- **Weights used**: [35, 20, 15]

**Result**:
- 🥇 1st Place: $105.00 (35/70 × $180)
- 🥈 2nd Place: $60.00 (20/70 × $180)  
- 🥉 3rd Place: $45.00 (15/70 × $180)
- 🍕 Food Pool: $45.00
- 🎯 Bounty Pool: $18.00

### 21 Players, $25 Buy-in
- **Players**: 21
- **Buy-in**: $25/player
- **Positions paid**: 7 (⌈21÷3⌉)
- **Total prize pool**: $525.00

The payout calculator automatically uses the first 7 weights and distributes the prize pool proportionally.

## Technical Details

- **Framework**: CustomTkinter for modern GUI
- **Real-time updates**: Variable tracing for instant calculations
- **Responsive design**: Adapts to different window sizes
- **Error handling**: Graceful handling of invalid inputs
- **Cross-platform**: Works on Windows, macOS, and Linux

## Color Scheme

The poker-themed color palette includes:
- **Felt Green**: Deep poker table background
- **Dark Green**: Control panel backgrounds
- **Light Green**: Section highlights
- **Accent Green**: Interactive elements
- **Gold**: Important text and highlights
- **Card White**: Standard text

## License

This project is open source and available under the MIT License.