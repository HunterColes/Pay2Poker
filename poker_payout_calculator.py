#!/usr/bin/env python3
"""
Poker Payout Calculator
A sleek GUI application for calculating poker tournament payouts with customizable weights,
food pool, and bounty pool features.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import math
from typing import List, Dict, Tuple

# Set appearance mode and poker green color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Custom poker green colors
POKER_COLORS = {
    "dark_green": "#0D4F3C",      # Dark poker table green
    "medium_green": "#1B5E20",    # Medium green
    "light_green": "#2E7D32",     # Lighter green
    "accent_green": "#4CAF50",    # Bright green accent
    "felt_green": "#0A3D2E",      # Deep felt green
    "gold": "#FFD700",            # Gold for highlights
    "card_white": "#F5F5F5"       # Card white
}


class PokerPayoutCalculator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🃏 Poker Payout Calculator")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self.root.configure(fg_color=POKER_COLORS["felt_green"])
        
        # Default payout weights for top 9 positions
        self.default_weights = [35, 20, 15, 10, 8, 6, 3, 2, 1]
        self.current_weights = self.default_weights.copy()
        
        # Variables for interactive updates
        self.num_players = tk.IntVar(value=9)
        self.buy_in = tk.DoubleVar(value=20.0)
        self.food_per_player = tk.DoubleVar(value=5.0)
        self.bounty_per_player = tk.DoubleVar(value=2.0)
        
        # Weights window reference
        self.weights_window = None
        
        # Player payment tracking
        self.player_data = []  # List of dicts with player info and payment status
        self.bank_frame = None
        
        self.setup_ui()
        
        # Add trace callbacks after UI setup
        self.num_players.trace_add("write", self.on_value_change)
        self.buy_in.trace_add("write", self.on_value_change)
        self.food_per_player.trace_add("write", self.on_value_change)
        self.bounty_per_player.trace_add("write", self.on_value_change)
        
        # Initial calculation
        self.calculate_payouts()
        
    def setup_ui(self):
        """Setup the user interface with left controls and right results"""
        # Main horizontal container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left side - Controls and Bank
        left_frame = ctk.CTkFrame(main_container, fg_color="transparent", width=500)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Controls frame (top part of left side)
        controls_frame = ctk.CTkFrame(left_frame, fg_color=POKER_COLORS["dark_green"])
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Bank frame (bottom part of left side)
        self.bank_frame = ctk.CTkFrame(left_frame, fg_color=POKER_COLORS["dark_green"])
        self.bank_frame.pack(fill="both", expand=True)
        
        # Right side - Results
        right_frame = ctk.CTkFrame(main_container, fg_color=POKER_COLORS["medium_green"])
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Setup left side controls
        self.setup_controls(controls_frame)
        
        # Setup bank section
        self.setup_bank(self.bank_frame)
        
        # Setup right side results
        self.setup_results(right_frame)
        
    def setup_controls(self, parent):
        """Setup the control panel on the left side"""
        # Title
        title_label = ctk.CTkLabel(
            parent, 
            text="🃏 Poker Payout Calculator", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        title_label.pack(pady=(20, 30))
        
        # Create control sections
        self.create_player_section(parent)
        self.create_pool_section(parent)
        self.create_weights_section(parent)
        
    def setup_results(self, parent):
        """Setup the results panel on the right side"""
        # Results title
        self.results_title = ctk.CTkLabel(
            parent,
            text="💰 Tournament Payouts",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        self.results_title.pack(pady=(20, 15))
        
        # Scrollable frame for results
        self.results_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color=POKER_COLORS["felt_green"],
            scrollbar_fg_color=POKER_COLORS["dark_green"]
        )
        self.results_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
    def create_player_section(self, parent):
        """Create the player count section"""
        player_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["light_green"])
        player_frame.pack(fill="x", pady=(0, 15), padx=20)
        
        # Player count label
        player_label = ctk.CTkLabel(
            player_frame, 
            text="Number of Players:", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        )
        player_label.pack(pady=(15, 5))
        
        # Player slider
        self.player_slider = ctk.CTkSlider(
            player_frame,
            from_=3,
            to=30,
            number_of_steps=27,
            variable=self.num_players,
            command=self.on_player_change,
            fg_color=POKER_COLORS["dark_green"],
            progress_color=POKER_COLORS["accent_green"],
            button_color=POKER_COLORS["gold"],
            button_hover_color=POKER_COLORS["gold"]
        )
        self.player_slider.pack(pady=5, padx=20, fill="x")
        
        # Player count display
        self.player_count_label = ctk.CTkLabel(
            player_frame,
            text=f"Players: {self.num_players.get()}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        self.player_count_label.pack(pady=(5, 15))
        
    def create_pool_section(self, parent):
        """Create the pool configuration section"""
        pool_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["light_green"])
        pool_frame.pack(fill="x", pady=(0, 15), padx=20)
        
        pool_title = ctk.CTkLabel(
            pool_frame, 
            text="💵 Pool Configuration", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        )
        pool_title.pack(pady=(15, 10))
        
        # Buy-in entry
        buy_in_frame = ctk.CTkFrame(pool_frame, fg_color="transparent")
        buy_in_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            buy_in_frame, 
            text="Buy-in per player ($):",
            text_color=POKER_COLORS["card_white"]
        ).pack(side="left")
        buy_in_entry = ctk.CTkEntry(
            buy_in_frame, 
            textvariable=self.buy_in, 
            width=100,
            fg_color=POKER_COLORS["dark_green"],
            border_color=POKER_COLORS["accent_green"]
        )
        buy_in_entry.pack(side="right")
        
        # Food pool entry
        food_frame = ctk.CTkFrame(pool_frame, fg_color="transparent")
        food_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            food_frame, 
            text="Food pool per player ($):",
            text_color=POKER_COLORS["card_white"]
        ).pack(side="left")
        food_entry = ctk.CTkEntry(
            food_frame, 
            textvariable=self.food_per_player, 
            width=100,
            fg_color=POKER_COLORS["dark_green"],
            border_color=POKER_COLORS["accent_green"]
        )
        food_entry.pack(side="right")
        
        # Bounty pool entry
        bounty_frame = ctk.CTkFrame(pool_frame, fg_color="transparent")
        bounty_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkLabel(
            bounty_frame, 
            text="Bounty per player ($):",
            text_color=POKER_COLORS["card_white"]
        ).pack(side="left")
        bounty_entry = ctk.CTkEntry(
            bounty_frame, 
            textvariable=self.bounty_per_player, 
            width=100,
            fg_color=POKER_COLORS["dark_green"],
            border_color=POKER_COLORS["accent_green"]
        )
        bounty_entry.pack(side="right")
        
    def create_weights_section(self, parent):
        """Create the payout weights configuration section"""
        weights_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["light_green"])
        weights_frame.pack(fill="x", pady=(0, 15), padx=20)
        
        weights_title = ctk.CTkLabel(
            weights_frame, 
            text="⚖️ Payout Weights", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        )
        weights_title.pack(pady=(15, 10))
        
        # Current weights display
        self.weights_summary = ctk.CTkLabel(
            weights_frame,
            text=self.get_weights_summary(),
            font=ctk.CTkFont(size=12),
            text_color=POKER_COLORS["gold"],
            justify="left"
        )
        self.weights_summary.pack(pady=5, padx=20)
        
        # Weights control buttons
        weights_btn_frame = ctk.CTkFrame(weights_frame, fg_color="transparent")
        weights_btn_frame.pack(pady=(5, 15))
        
        edit_weights_btn = ctk.CTkButton(
            weights_btn_frame,
            text="🔧 Customize Weights",
            command=self.open_weights_window,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            text_color=POKER_COLORS["card_white"]
        )
        edit_weights_btn.pack(side="left", padx=5)
        
        reset_weights_btn = ctk.CTkButton(
            weights_btn_frame,
            text="🔄 Reset",
            command=self.reset_weights,
            fg_color=POKER_COLORS["dark_green"],
            hover_color=POKER_COLORS["medium_green"],
            text_color=POKER_COLORS["card_white"]
        )
        reset_weights_btn.pack(side="left", padx=5)
        
    def setup_bank(self, parent):
        """Setup the bank panel for tracking player payments"""
        # Bank title
        bank_title = ctk.CTkLabel(
            parent,
            text="🏦 Bank Tracker",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        bank_title.pack(pady=(20, 10))
        
        # Pool summary section
        pool_summary_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["light_green"])
        pool_summary_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.total_pool_label = ctk.CTkLabel(
            pool_summary_frame,
            text="Total Pool: $0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        )
        self.total_pool_label.pack(pady=5)
        
        self.total_paid_label = ctk.CTkLabel(
            pool_summary_frame,
            text="Total Paid: $0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        )
        self.total_paid_label.pack(pady=5)
        
        self.percent_paid_label = ctk.CTkLabel(
            pool_summary_frame,
            text="Percent Paid: 0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        self.percent_paid_label.pack(pady=(5, 10))
        
        # Scrollable frame for player rows
        self.bank_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color=POKER_COLORS["medium_green"],
            scrollbar_fg_color=POKER_COLORS["dark_green"]
        )
        self.bank_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initialize player data and display
        self.update_player_data()
        
    def update_player_data(self):
        """Update player data list when player count changes"""
        num_players = self.num_players.get()
        
        # Adjust player data list to match current player count
        while len(self.player_data) < num_players:
            self.player_data.append({
                'name': f"Player {len(self.player_data) + 1}",
                'buy_in': tk.BooleanVar(value=False),
                'food': tk.BooleanVar(value=False),
                'bounty': tk.BooleanVar(value=False),
                'all': tk.BooleanVar(value=False)
            })
        
        # Remove excess players
        while len(self.player_data) > num_players:
            self.player_data.pop()
        
        # Update the bank display
        self.update_bank_display()
        
    def update_bank_display(self):
        """Update the bank display with current player data"""
        # Clear existing player rows
        for widget in self.bank_scroll.winfo_children():
            widget.destroy()
        
        # Create player rows
        for i, player in enumerate(self.player_data):
            self.create_player_row(i, player)
        
        # Update pool summary
        self.update_pool_summary()
        
    def create_player_row(self, index, player):
        """Create a row for a player with name entry and checkboxes"""
        player_frame = ctk.CTkFrame(self.bank_scroll, fg_color=POKER_COLORS["dark_green"])
        player_frame.pack(fill="x", pady=2, padx=5)
        
        # Player name entry
        name_var = tk.StringVar(value=player['name'])
        name_var.trace_add("write", lambda *args: self.on_player_name_change(index, name_var.get()))
        
        name_entry = ctk.CTkEntry(
            player_frame,
            textvariable=name_var,
            width=120,
            fg_color=POKER_COLORS["felt_green"],
            border_color=POKER_COLORS["accent_green"]
        )
        name_entry.pack(side="left", padx=5, pady=5)
        
        # Checkboxes frame
        checks_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        checks_frame.pack(side="right", padx=5, pady=5)
        
        # Buy-in checkbox
        buy_in_check = ctk.CTkCheckBox(
            checks_frame,
            text="Buy-in",
            variable=player['buy_in'],
            command=lambda: self.on_checkbox_change(index),
            width=60,
            text_color=POKER_COLORS["card_white"],
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"]
        )
        buy_in_check.pack(side="left", padx=2)
        
        # Food checkbox
        food_check = ctk.CTkCheckBox(
            checks_frame,
            text="Food",
            variable=player['food'],
            command=lambda: self.on_checkbox_change(index),
            width=50,
            text_color=POKER_COLORS["card_white"],
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"]
        )
        food_check.pack(side="left", padx=2)
        
        # Bounty checkbox
        bounty_check = ctk.CTkCheckBox(
            checks_frame,
            text="Bounty",
            variable=player['bounty'],
            command=lambda: self.on_checkbox_change(index),
            width=60,
            text_color=POKER_COLORS["card_white"],
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"]
        )
        bounty_check.pack(side="left", padx=2)
        
        # All checkbox
        all_check = ctk.CTkCheckBox(
            checks_frame,
            text="All",
            variable=player['all'],
            command=lambda: self.on_all_checkbox_change(index),
            width=40,
            text_color=POKER_COLORS["gold"],
            fg_color=POKER_COLORS["gold"],
            hover_color=POKER_COLORS["accent_green"]
        )
        all_check.pack(side="left", padx=2)
        
    def on_player_name_change(self, index, new_name):
        """Handle player name change"""
        if index < len(self.player_data):
            self.player_data[index]['name'] = new_name
        
    def on_checkbox_change(self, index):
        """Handle individual checkbox changes"""
        if index < len(self.player_data):
            player = self.player_data[index]
            # Check if all individual checkboxes are checked
            all_checked = (player['buy_in'].get() and 
                          player['food'].get() and 
                          player['bounty'].get())
            player['all'].set(all_checked)
            self.update_pool_summary()
        
    def on_all_checkbox_change(self, index):
        """Handle 'All' checkbox change"""
        if index < len(self.player_data):
            player = self.player_data[index]
            all_checked = player['all'].get()
            player['buy_in'].set(all_checked)
            player['food'].set(all_checked)
            player['bounty'].set(all_checked)
            self.update_pool_summary()
        
    def update_pool_summary(self):
        """Update the pool summary display"""
        # Calculate totals
        num_players = self.num_players.get()
        buy_in = self.buy_in.get()
        food_per_player = self.food_per_player.get()
        bounty_per_player = self.bounty_per_player.get()
        
        total_pool = num_players * (buy_in + food_per_player + bounty_per_player)
        
        # Calculate total paid
        total_paid = 0
        for player in self.player_data:
            if player['buy_in'].get():
                total_paid += buy_in
            if player['food'].get():
                total_paid += food_per_player
            if player['bounty'].get():
                total_paid += bounty_per_player
        
        # Calculate percentage
        percent_paid = (total_paid / total_pool * 100) if total_pool > 0 else 0
        
        # Update labels
        self.total_pool_label.configure(text=f"Total Pool: ${total_pool:.2f}")
        self.total_paid_label.configure(text=f"Total Paid: ${total_paid:.2f}")
        
        # Color code the percentage based on completion
        if percent_paid >= 100:
            color = POKER_COLORS["accent_green"]
        elif percent_paid >= 75:
            color = POKER_COLORS["gold"]
        else:
            color = POKER_COLORS["card_white"]
            
        self.percent_paid_label.configure(
            text=f"Percent Paid: {percent_paid:.1f}%",
            text_color=color
        )
        
    def get_position_suffix(self, position: int) -> str:
        """Get the appropriate suffix for position numbers"""
        if 10 <= position % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(position % 10, "th")
        return f"{position}{suffix}"
    
    def on_player_change(self, value):
        """Handle player count slider change"""
        player_count = int(value)
        self.player_count_label.configure(text=f"Players: {player_count}")
        self.update_player_data()  # Update bank data when player count changes
        self.calculate_payouts()
    
    def on_value_change(self, *args):
        """Handle any value change that requires recalculation"""
        self.calculate_payouts()
        # Update bank summary if bank exists
        if hasattr(self, 'total_pool_label'):
            self.update_pool_summary()
    
    def get_weights_summary(self):
        """Get a summary string of current weights"""
        if not self.current_weights:
            return "No weights set"
        
        # Show first few weights
        summary_weights = self.current_weights[:5]
        summary = f"Weights: {', '.join(map(str, summary_weights))}"
        if len(self.current_weights) > 5:
            summary += f"... (+{len(self.current_weights) - 5} more)"
        return summary
    
    def calculate_payouts(self):
        """Calculate and display tournament payouts"""
        try:
            # Clear existing results
            for widget in self.results_scroll.winfo_children():
                widget.destroy()
            
            # Get current values
            num_players = self.num_players.get()
            buy_in = self.buy_in.get()
            food_per_player = self.food_per_player.get()
            bounty_per_player = self.bounty_per_player.get()
            
            # Calculate pools
            prize_pool = num_players * buy_in
            food_pool = num_players * food_per_player
            bounty_pool = num_players * bounty_per_player
            total_pool = prize_pool + food_pool + bounty_pool
            
            # Calculate number of paying positions (max 1/3 of players or length of weights)
            max_paying_positions = min(max(1, num_players // 3), len(self.current_weights))
            
            # Calculate total weight
            paying_weights = self.current_weights[:max_paying_positions]
            total_weight = sum(paying_weights)
            
            if total_weight == 0:
                total_weight = 1  # Prevent division by zero
            
            # Display pool summary
            self.display_pool_summary(prize_pool, food_pool, bounty_pool, total_pool)
            
            # Calculate and display payouts
            for position in range(max_paying_positions):
                weight = paying_weights[position]
                payout = (weight / total_weight) * prize_pool
                
                # Create payout display
                self.create_payout_row(position + 1, payout, weight)
            
            # Display bounty information if applicable
            if bounty_per_player > 0:
                self.display_bounty_info(bounty_per_player, bounty_pool)
                
        except Exception as e:
            # Display error message
            error_label = ctk.CTkLabel(
                self.results_scroll,
                text=f"Error calculating payouts: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=10)
    
    def display_pool_summary(self, prize_pool, food_pool, bounty_pool, total_pool):
        """Display the pool summary at the top of results"""
        summary_frame = ctk.CTkFrame(self.results_scroll, fg_color=POKER_COLORS["dark_green"])
        summary_frame.pack(fill="x", pady=(0, 15), padx=10)
        
        ctk.CTkLabel(
            summary_frame,
            text="💰 Pool Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=POKER_COLORS["gold"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            summary_frame,
            text=f"Prize Pool: ${prize_pool:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=POKER_COLORS["card_white"]
        ).pack()
        
        if food_pool > 0:
            ctk.CTkLabel(
                summary_frame,
                text=f"Food Pool: ${food_pool:.2f}",
                font=ctk.CTkFont(size=12),
                text_color=POKER_COLORS["card_white"]
            ).pack()
        
        if bounty_pool > 0:
            ctk.CTkLabel(
                summary_frame,
                text=f"Bounty Pool: ${bounty_pool:.2f}",
                font=ctk.CTkFont(size=12),
                text_color=POKER_COLORS["card_white"]
            ).pack()
        
        ctk.CTkLabel(
            summary_frame,
            text=f"Total Pool: ${total_pool:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=POKER_COLORS["gold"]
        ).pack(pady=(5, 10))
    
    def create_payout_row(self, position, payout, weight):
        """Create a payout row for a specific position"""
        payout_frame = ctk.CTkFrame(self.results_scroll, fg_color=POKER_COLORS["light_green"])
        payout_frame.pack(fill="x", pady=2, padx=10)
        
        # Position emojis
        position_emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * 20
        emoji = position_emojis[position - 1] if position - 1 < len(position_emojis) else "🏅"
        
        # Position label
        position_text = f"{emoji} {self.get_position_suffix(position)} Place"
        ctk.CTkLabel(
            payout_frame,
            text=position_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        ).pack(side="left", padx=15, pady=10)
        
        # Payout amount
        ctk.CTkLabel(
            payout_frame,
            text=f"${payout:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=POKER_COLORS["gold"]
        ).pack(side="right", padx=15, pady=10)
        
        # Weight indicator
        ctk.CTkLabel(
            payout_frame,
            text=f"(Weight: {weight})",
            font=ctk.CTkFont(size=10),
            text_color=POKER_COLORS["card_white"]
        ).pack(side="right", padx=5, pady=10)
    
    def display_bounty_info(self, bounty_per_player, bounty_pool):
        """Display bounty information"""
        bounty_frame = ctk.CTkFrame(self.results_scroll, fg_color=POKER_COLORS["medium_green"])
        bounty_frame.pack(fill="x", pady=(15, 0), padx=10)
        
        ctk.CTkLabel(
            bounty_frame,
            text="🎯 Bounty Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=POKER_COLORS["gold"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            bounty_frame,
            text=f"Bounty per knockout: ${bounty_per_player:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=POKER_COLORS["card_white"]
        ).pack()
        
        ctk.CTkLabel(
            bounty_frame,
            text=f"Total bounty pool: ${bounty_pool:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=POKER_COLORS["card_white"]
        ).pack(pady=(0, 10))
    
    def open_weights_window(self):
        """Open the weights customization window"""
        if self.weights_window and self.weights_window.winfo_exists():
            self.weights_window.lift()
        else:
            self.weights_window = WeightsWindow(
                self.root, 
                self.current_weights, 
                self.update_weights_callback
            )
    
    def reset_weights(self):
        """Reset weights to default values"""
        self.current_weights = self.default_weights.copy()
        self.weights_summary.configure(text=self.get_weights_summary())
        if self.weights_window and self.weights_window.winfo_exists():
            self.weights_window.update_weights_display(self.current_weights)
        self.calculate_payouts()
    
    def update_weights_callback(self, new_weights):
        """Callback function for when weights are updated"""
        self.current_weights = new_weights
        self.weights_summary.configure(text=self.get_weights_summary())
        self.calculate_payouts()
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


class WeightsWindow:
    def __init__(self, parent, current_weights, update_callback):
        self.update_callback = update_callback
        self.current_weights = current_weights.copy()
        
        # Create weights window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("🎰 Customize Payout Weights")
        self.window.geometry("500x600")
        self.window.configure(fg_color=POKER_COLORS["felt_green"])
        self.window.transient(parent)
        
        # Center the window
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (250)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300)
        self.window.geometry(f"500x600+{x}+{y}")
        
        self.setup_weights_ui()
        
    def setup_weights_ui(self):
        """Setup the weights customization UI"""
        # Title
        title = ctk.CTkLabel(
            self.window, 
            text="🎰 Customize Payout Weights", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        title.pack(pady=20)
        
        # Instructions
        instructions = ctk.CTkLabel(
            self.window,
            text="Adjust the payout weights for each position.\nHigher weights = bigger payouts.",
            font=ctk.CTkFont(size=12),
            text_color=POKER_COLORS["card_white"]
        )
        instructions.pack(pady=10)
        
        # Scrollable frame for weight entries
        self.weights_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color=POKER_COLORS["dark_green"],
            height=350
        )
        self.weights_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Weight entry widgets
        self.weight_entries = []
        self.create_weight_entries()
        
        # Buttons
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.pack(pady=20)
        
        add_position_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add Position",
            command=self.add_position,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"]
        )
        add_position_btn.pack(side="left", padx=5)
        
        remove_position_btn = ctk.CTkButton(
            button_frame,
            text="➖ Remove Last",
            command=self.remove_position,
            fg_color=POKER_COLORS["medium_green"],
            hover_color=POKER_COLORS["dark_green"]
        )
        remove_position_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="✅ Done",
            command=self.window.destroy,
            fg_color=POKER_COLORS["gold"],
            hover_color=POKER_COLORS["accent_green"],
            text_color=POKER_COLORS["dark_green"]
        )
        close_btn.pack(side="left", padx=5)
        
    def create_weight_entries(self):
        """Create weight entry widgets"""
        for widget in self.weights_frame.winfo_children():
            widget.destroy()
        self.weight_entries.clear()
        
        for i, weight in enumerate(self.current_weights):
            position_frame = ctk.CTkFrame(self.weights_frame, fg_color=POKER_COLORS["light_green"])
            position_frame.pack(fill="x", pady=5, padx=10)
            
            position_emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * 20
            emoji = position_emojis[i] if i < len(position_emojis) else "🏅"
            
            ctk.CTkLabel(
                position_frame,
                text=f"{emoji} {self.get_position_suffix(i+1)} Place:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=POKER_COLORS["card_white"]
            ).pack(side="left", padx=10, pady=10)
            
            weight_var = tk.IntVar(value=weight)
            weight_var.trace_add("write", lambda *args, idx=i: self.on_weight_change(idx))
            
            weight_entry = ctk.CTkEntry(
                position_frame,
                textvariable=weight_var,
                width=80,
                fg_color=POKER_COLORS["dark_green"],
                border_color=POKER_COLORS["accent_green"]
            )
            weight_entry.pack(side="right", padx=10, pady=10)
            
            self.weight_entries.append(weight_var)
            
    def get_position_suffix(self, position: int) -> str:
        """Get the appropriate suffix for position numbers"""
        if 10 <= position % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(position % 10, "th")
        return f"{position}{suffix}"
        
    def on_weight_change(self, index):
        """Handle weight change"""
        try:
            new_weight = self.weight_entries[index].get()
            if new_weight > 0:
                self.current_weights[index] = new_weight
                self.update_callback(self.current_weights.copy())
        except (ValueError, tk.TclError):
            pass
            
    def add_position(self):
        """Add a new position"""
        self.current_weights.append(1)
        self.create_weight_entries()
        self.update_callback(self.current_weights.copy())
        
    def remove_position(self):
        """Remove the last position"""
        if len(self.current_weights) > 1:
            self.current_weights.pop()
            self.create_weight_entries()
            self.update_callback(self.current_weights.copy())
            
    def update_weights_display(self, new_weights):
        """Update the weights display"""
        self.current_weights = new_weights.copy()
        self.create_weight_entries()
        
    def winfo_exists(self):
        """Check if window exists"""
        try:
            return self.window.winfo_exists()
        except:
            return False
            
    def lift(self):
        """Bring window to front"""
        self.window.lift()


if __name__ == "__main__":
    app = PokerPayoutCalculator()
    app.run()