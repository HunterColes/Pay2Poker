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
        self.root.geometry("1200x1200")
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
        
        # Timer variables
        self.game_duration = tk.IntVar(value=180)  # Default 3 hours in minutes
        self.current_time = 0  # Current time in seconds
        self.timer_running = False
        self.timer_job = None
        self.timer_direction = tk.StringVar(value="countdown")  # countdown or countup
        
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
        
        # Initial calculation and display updates
        self.update_total_per_player()
        self.calculate_payouts()
        self.reset_timer()  # Initialize timer
        
    def create_label(self, parent, text, size=12, weight="normal", color="card_white", **pack_kwargs):
        """Helper method to create consistently styled labels"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=size, weight=weight),
            text_color=POKER_COLORS[color]
        )
        if pack_kwargs:
            label.pack(**pack_kwargs)
        return label
    
    def create_title_label(self, parent, text, emoji="", size=18, **pack_kwargs):
        """Helper method to create title labels with consistent styling"""
        title_text = f"{emoji} {text}" if emoji else text
        return self.create_label(
            parent, 
            title_text, 
            size=size, 
            weight="bold", 
            color="gold",
            **pack_kwargs
        )
    
    def create_entry_row(self, parent, label_text, variable, width=100):
        """Helper method to create label + entry rows"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", padx=20, pady=5)
        
        self.create_label(row_frame, label_text).pack(side="left")
        
        entry = ctk.CTkEntry(
            row_frame,
            textvariable=variable,
            width=width,
            fg_color=POKER_COLORS["dark_green"],
            border_color=POKER_COLORS["accent_green"]
        )
        entry.pack(side="right")
        return row_frame
    
    def safe_get_value(self, variable, default=0.0):
        """Safely get value from tkinter variable with fallback"""
        try:
            return variable.get()
        except tk.TclError:
            return default
        
    def setup_ui(self):
        """Setup the user interface with left controls, middle results, and right timer/chips"""
        # Main horizontal container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left side - Controls and Bank
        left_frame = ctk.CTkFrame(main_container, fg_color="transparent", width=475)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Controls frame (top part of left side)
        controls_frame = ctk.CTkFrame(left_frame, fg_color=POKER_COLORS["dark_green"])
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Bank frame (bottom part of left side)
        self.bank_frame = ctk.CTkFrame(left_frame, fg_color=POKER_COLORS["dark_green"])
        self.bank_frame.pack(fill="both", expand=True)
        
        # Middle - Tournament Results
        middle_frame = ctk.CTkFrame(main_container, fg_color=POKER_COLORS["medium_green"], width=400)
        middle_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        middle_frame.pack_propagate(False)
        
        # Right side - Timer and Blinds
        right_frame = ctk.CTkFrame(main_container, fg_color="transparent", width=350)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        # Timer frame (top part of right side)
        timer_frame = ctk.CTkFrame(right_frame, fg_color=POKER_COLORS["dark_green"])
        timer_frame.pack(fill="x", pady=(0, 10))
        
        # Blinds frame (bottom part of right side)
        blinds_frame = ctk.CTkFrame(right_frame, fg_color=POKER_COLORS["dark_green"])
        blinds_frame.pack(fill="both", expand=True)
        
        # Setup all sections
        self.setup_controls(controls_frame)
        self.setup_bank(self.bank_frame)
        self.setup_results(middle_frame)
        self.setup_timer(timer_frame)
        self.setup_blinds(blinds_frame)
        
    def setup_controls(self, parent):
        """Setup the control panel on the left side"""
        # Title
        title_label = self.create_title_label(
            parent, 
            "Poker Payout Calculator", 
            "🃏", 
            size=24, 
            pady=(20, 30)
        )
        
        # Create control sections
        self.create_player_section(parent)
        self.create_pool_section(parent)
        self.create_weights_section(parent)
        
    def setup_results(self, parent):
        """Setup the results panel on the right side"""
        # Results title
        self.results_title = self.create_title_label(
            parent,
            "Tournament Payouts",
            "💰",
            size=20,
            pady=(20, 15)
        )
        
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
            fg_color=POKER_COLORS["dark_green"],
            progress_color=POKER_COLORS["accent_green"],
            button_color=POKER_COLORS["gold"],
            button_hover_color=POKER_COLORS["gold"]
        )
        self.player_slider.set(self.num_players.get())  # Set initial value manually
        self.player_slider.pack(pady=5, padx=20, fill="x")
        
        # Bind mouse events for optimized updates
        self.player_slider.bind("<ButtonRelease-1>", self.on_player_slider_release)
        self.player_slider.bind("<B1-Motion>", self.on_player_slider_drag)
        
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
        
        self.create_title_label(pool_frame, "Pool Configuration", "💵", size=16, pady=(15, 10))
        
        # Create entry rows using helper method
        self.create_entry_row(pool_frame, "Buy-in per player ($):", self.buy_in)
        self.create_entry_row(pool_frame, "Food pool per player ($):", self.food_per_player)
        self.create_entry_row(pool_frame, "Bounty per player ($):", self.bounty_per_player)
        
        # Total per player display
        total_frame = ctk.CTkFrame(pool_frame, fg_color=POKER_COLORS["dark_green"], corner_radius=8)
        total_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        self.create_label(
            total_frame,
            "💳 Total Due Per Player:",
            size=14,
            weight="bold"
        ).pack(side="left", padx=15, pady=8)
        
        self.total_per_player_label = self.create_label(
            total_frame,
            "$0.00",
            size=16,
            weight="bold",
            color="gold"
        )
        self.total_per_player_label.pack(side="right", padx=15, pady=8)
        
    def create_weights_section(self, parent):
        """Create the payout weights configuration section"""
        weights_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["light_green"])
        weights_frame.pack(fill="x", pady=(0, 15), padx=20)
        
        self.create_title_label(weights_frame, "Payout Weights", "⚖️", size=16, pady=(15, 10))
        
        # Current weights display
        self.weights_summary = self.create_label(
            weights_frame,
            self.get_weights_summary(),
            size=12,
            color="gold"
        )
        self.weights_summary.pack(pady=5, padx=20, anchor="w")
        
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
        bank_title = self.create_title_label(
            parent,
            "Bank Tracker",
            "🏦",
            pady=(20, 10)
        )
        
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
                'all': tk.BooleanVar(value=False),
                'eliminated': tk.BooleanVar(value=False),
                'payed_out': tk.BooleanVar(value=False)
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
        
        # Create header row with labels
        header_frame = ctk.CTkFrame(self.bank_scroll, fg_color=POKER_COLORS["medium_green"])
        header_frame.pack(fill="x", pady=(0, 5), padx=5)
        
        # Player name label
        ctk.CTkLabel(
            header_frame,
            text="Player Name",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=POKER_COLORS["card_white"],
            width=120
        ).pack(side="left", padx=(5, 10), pady=5)
        
        # Labels frame for checkboxes
        labels_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        labels_frame.pack(side="right", padx=5, pady=5)
        
        # Checkbox labels
        labels = [
            ("Buy-In", POKER_COLORS["card_white"]),
            ("Food", POKER_COLORS["card_white"]),
            ("Bounty", POKER_COLORS["card_white"]),
            ("All", POKER_COLORS["gold"]),
            ("❌", "#DC143C"),  # Red X for eliminated
            ("⭐", "#FFD700")   # Gold star for payed out
        ]
        
        for label_text, color in labels:
            ctk.CTkLabel(
                labels_frame,
                text=label_text,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=color,
                width=36
            ).pack(side="left", padx=0)
        
        # Create player rows
        for i, player in enumerate(self.player_data):
            self.create_player_row(i, player)
        
        # Update pool summary
        self.update_pool_summary()
        
    def create_player_row(self, index, player):
        """Create a row for a player with name entry and checkboxes"""
        player_frame = ctk.CTkFrame(self.bank_scroll, fg_color=POKER_COLORS["dark_green"])
        player_frame.pack(fill="x", pady=1, padx=5)
        
        # Player name entry
        name_var = tk.StringVar(value=player['name'])
        name_var.trace_add("write", lambda *args: self.on_player_name_change(index, name_var.get()))
        
        name_entry = ctk.CTkEntry(
            player_frame,
            textvariable=name_var,
            width=120,
            height=28,
            fg_color=POKER_COLORS["felt_green"],
            border_color=POKER_COLORS["accent_green"]
        )
        name_entry.pack(side="left", padx=(5, 10), pady=3)
        
        # Checkboxes frame
        checks_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        checks_frame.pack(side="right", padx=5, pady=3)
        
        # Buy-in checkbox
        buy_in_check = ctk.CTkCheckBox(
            checks_frame,
            text="",
            variable=player['buy_in'],
            command=lambda: self.on_checkbox_change(index),
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            checkmark_color=POKER_COLORS["dark_green"]
        )
        buy_in_check.pack(side="left", padx=8)
        
        # Food checkbox
        food_check = ctk.CTkCheckBox(
            checks_frame,
            text="",
            variable=player['food'],
            command=lambda: self.on_checkbox_change(index),
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            checkmark_color=POKER_COLORS["dark_green"]
        )
        food_check.pack(side="left", padx=8)
        
        # Bounty checkbox
        bounty_check = ctk.CTkCheckBox(
            checks_frame,
            text="",
            variable=player['bounty'],
            command=lambda: self.on_checkbox_change(index),
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            checkmark_color=POKER_COLORS["dark_green"]
        )
        bounty_check.pack(side="left", padx=8)
        
        # All checkbox
        all_check = ctk.CTkCheckBox(
            checks_frame,
            text="",
            variable=player['all'],
            command=lambda: self.on_all_checkbox_change(index),
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=POKER_COLORS["gold"],
            hover_color=POKER_COLORS["accent_green"],
            checkmark_color=POKER_COLORS["dark_green"]
        )
        all_check.pack(side="left", padx=8)
        
        # Eliminated checkbox (red X when checked)
        eliminated_check = ctk.CTkCheckBox(
            checks_frame,
            text="",
            variable=player['eliminated'],
            command=lambda: self.update_pool_summary(),
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            fg_color="#DC143C",  # Crimson red
            hover_color="#B22222",  # Dark red
            checkmark_color=POKER_COLORS["dark_green"]
        )
        eliminated_check.pack(side="left", padx=8)
        
        # Payed out checkbox (gold star effect)
        payed_out_check = ctk.CTkCheckBox(
            checks_frame,
            text="",
            variable=player['payed_out'],
            command=lambda: self.update_pool_summary(),
            width=20,
            height=20,
            checkbox_width=18,
            checkbox_height=18,
            fg_color="#FFD700",  # Gold
            hover_color="#FFA500",  # Orange
            checkmark_color=POKER_COLORS["dark_green"]
        )
        payed_out_check.pack(side="left", padx=8)
        
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
        """Handle 'All' checkbox change - only affects payment checkboxes"""
        if index < len(self.player_data):
            player = self.player_data[index]
            all_checked = player['all'].get()
            player['buy_in'].set(all_checked)
            player['food'].set(all_checked)
            player['bounty'].set(all_checked)
            self.update_pool_summary()
        
    def update_pool_summary(self):
        """Update the pool summary display"""
        try:
            # Calculate totals using safe value retrieval
            num_players = self.num_players.get()
            buy_in = self.safe_get_value(self.buy_in)
            food_per_player = self.safe_get_value(self.food_per_player)
            bounty_per_player = self.safe_get_value(self.bounty_per_player)
            
            total_pool = num_players * (buy_in + food_per_player + bounty_per_player)
            
            # Calculate total paid and player statistics
            total_paid = 0
            eliminated_count = 0
            payed_out_count = 0
            
            for player in self.player_data:
                if player['buy_in'].get():
                    total_paid += buy_in
                if player['food'].get():
                    total_paid += food_per_player
                if player['bounty'].get():
                    total_paid += bounty_per_player
                if player['eliminated'].get():
                    eliminated_count += 1
                if player['payed_out'].get():
                    payed_out_count += 1
            
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
                
            # Update percent label with additional stats
            remaining_players = num_players - eliminated_count
            percent_text = f"Paid: {percent_paid:.1f}% | Active: {remaining_players} | Paid Out: {payed_out_count}"
            
            self.percent_paid_label.configure(
                text=percent_text,
                text_color=color
            )
        except Exception as e:
            # Handle any errors gracefully
            if hasattr(self, 'total_pool_label'):
                self.total_pool_label.configure(text="Total Pool: $0.00")
            if hasattr(self, 'total_paid_label'):
                self.total_paid_label.configure(text="Total Paid: $0.00")
            if hasattr(self, 'percent_paid_label'):
                self.percent_paid_label.configure(text="Paid: 0% | Active: 0 | Paid Out: 0")
        
    def get_position_suffix(self, position: int) -> str:
        """Get the appropriate suffix for position numbers"""
        if 10 <= position % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(position % 10, "th")
        return f"{position}{suffix}"
    
    def on_player_change(self, value):
        """Handle player count slider change - optimized for final value only"""
        player_count = int(value)
        self.player_count_label.configure(text=f"Players: {player_count}")
        # Update the variable without triggering trace callbacks
        self.num_players.set(player_count)
        self.update_player_data()  # Update bank data when player count changes
        self.calculate_payouts()
    
    def on_player_slider_drag(self, event):
        """Handle slider drag - only update display label for performance"""
        try:
            current_value = self.player_slider.get()
            player_count = int(current_value)
            self.player_count_label.configure(text=f"Players: {player_count}")
        except:
            pass
    
    def on_player_slider_release(self, event):
        """Handle slider release - perform full update"""
        try:
            current_value = self.player_slider.get()
            self.on_player_change(current_value)
        except:
            pass
    
    def on_value_change(self, *args):
        """Handle any value change that requires recalculation"""
        self.calculate_payouts()
        # Update bank summary if bank exists
        if hasattr(self, 'total_pool_label'):
            self.update_pool_summary()
        # Update total per player display
        if hasattr(self, 'total_per_player_label'):
            self.update_total_per_player()
    
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
    
    def update_total_per_player(self):
        """Update the total amount due per player display"""
        try:
            # Get current values using safe retrieval
            buy_in = self.safe_get_value(self.buy_in)
            food_per_player = self.safe_get_value(self.food_per_player)
            bounty_per_player = self.safe_get_value(self.bounty_per_player)
            
            total_per_player = buy_in + food_per_player + bounty_per_player
            
            if hasattr(self, 'total_per_player_label'):
                self.total_per_player_label.configure(text=f"${total_per_player:.2f}")
        except (ValueError, AttributeError):
            if hasattr(self, 'total_per_player_label'):
                self.total_per_player_label.configure(text="$0.00")
    
    def calculate_payouts(self):
        """Calculate and display tournament payouts"""
        try:
            # Clear existing results
            for widget in self.results_scroll.winfo_children():
                widget.destroy()
            
            # Get current values using safe retrieval
            num_players = self.num_players.get()
            buy_in = self.safe_get_value(self.buy_in)
            food_per_player = self.safe_get_value(self.food_per_player)
            bounty_per_player = self.safe_get_value(self.bounty_per_player)
            
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
        
    def setup_timer(self, parent):
        """Setup the blind timer panel"""
        # Timer title
        timer_title = self.create_title_label(
            parent,
            "Blind Timer",
            "⏰",
            pady=(15, 10)
        )
        
        # Game duration setting
        duration_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["light_green"])
        duration_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            duration_frame,
            text="Game Duration (minutes):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=POKER_COLORS["card_white"]
        ).pack(pady=(10, 5))
        
        duration_entry = ctk.CTkEntry(
            duration_frame,
            textvariable=self.game_duration,
            width=100,
            fg_color=POKER_COLORS["dark_green"],
            border_color=POKER_COLORS["accent_green"],
            justify="center"
        )
        duration_entry.pack(pady=(0, 10))
        
        # Timer mode selection
        mode_frame = ctk.CTkFrame(duration_frame, fg_color="transparent")
        mode_frame.pack(pady=(0, 10))
        
        countdown_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Countdown",
            variable=self.timer_direction,
            value="countdown",
            command=self.reset_timer,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            text_color=POKER_COLORS["card_white"]
        )
        countdown_radio.pack(side="left", padx=5)
        
        countup_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Count Up",
            variable=self.timer_direction,
            value="countup",
            command=self.reset_timer,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            text_color=POKER_COLORS["card_white"]
        )
        countup_radio.pack(side="left", padx=5)
        
        # Timer display
        timer_display_frame = ctk.CTkFrame(parent, fg_color=POKER_COLORS["felt_green"])
        timer_display_frame.pack(fill="x", padx=15, pady=10)
        
        self.timer_display = ctk.CTkLabel(
            timer_display_frame,
            text="3:00:00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=POKER_COLORS["gold"]
        )
        self.timer_display.pack(pady=20)
        
        # Progress bar
        self.timer_progress = ctk.CTkProgressBar(
            timer_display_frame,
            width=280,
            height=15,
            fg_color=POKER_COLORS["dark_green"],
            progress_color=POKER_COLORS["accent_green"]
        )
        self.timer_progress.pack(pady=(0, 15))
        
        # Timer control buttons
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(pady=10)
        
        self.start_pause_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Start",
            command=self.toggle_timer,
            fg_color=POKER_COLORS["accent_green"],
            hover_color=POKER_COLORS["medium_green"],
            width=80
        )
        self.start_pause_btn.pack(side="left", padx=5)
        
        reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Reset",
            command=self.reset_timer,
            fg_color=POKER_COLORS["medium_green"],
            hover_color=POKER_COLORS["dark_green"],
            width=80
        )
        reset_btn.pack(side="left", padx=5)
        
        # Initialize timer display
        self.update_timer_display()

    def setup_blinds(self, parent):
        """Setup the blinds panel"""
        # Blinds title
        blinds_title = self.create_title_label(
            parent,
            "Blinds",
            "🎯",
            pady=(15, 10)
        )
        
        # Placeholder content for now
        placeholder_label = self.create_label(
            parent,
            "Blind structure configuration\ncoming soon...",
            size=14
        )
        placeholder_label.pack(expand=True)

    def toggle_timer(self):
        """Start or pause the timer"""
        if self.timer_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        """Start the timer"""
        self.timer_running = True
        self.start_pause_btn.configure(text="⏸️ Pause")
        self.update_timer()

    def pause_timer(self):
        """Pause the timer"""
        self.timer_running = False
        self.start_pause_btn.configure(text="▶️ Start")
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

    def reset_timer(self):
        """Reset the timer"""
        self.pause_timer()
        if self.timer_direction.get() == "countdown":
            self.current_time = self.game_duration.get() * 60  # Convert to seconds
        else:
            self.current_time = 0
        self.update_timer_display()

    def update_timer(self):
        """Update the timer every second"""
        if self.timer_running:
            if self.timer_direction.get() == "countdown":
                self.current_time -= 1
                if self.current_time <= 0:
                    self.current_time = 0
                    self.pause_timer()
                    self.flash_timer_red()
            else:
                self.current_time += 1
                max_time = self.game_duration.get() * 60
                if self.current_time >= max_time:
                    self.current_time = max_time
                    self.pause_timer()
                    self.flash_timer_red()
            
            self.update_timer_display()
            self.timer_job = self.root.after(1000, self.update_timer)

    def update_timer_display(self):
        """Update the timer display and progress bar"""
        # Format time display
        hours = self.current_time // 3600
        minutes = (self.current_time % 3600) // 60
        seconds = self.current_time % 60
        time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        self.timer_display.configure(text=time_str)
        
        # Update progress bar
        total_time = self.game_duration.get() * 60
        if total_time > 0:
            if self.timer_direction.get() == "countdown":
                progress = 1 - (self.current_time / total_time)
            else:
                progress = self.current_time / total_time
            self.timer_progress.set(progress)
        else:
            self.timer_progress.set(0)
        
        # Change color based on time remaining
        if self.timer_direction.get() == "countdown":
            time_remaining_ratio = self.current_time / (self.game_duration.get() * 60) if self.game_duration.get() > 0 else 0
            if time_remaining_ratio <= 0.1:  # Last 10%
                self.timer_display.configure(text_color="#FF4444")  # Red
            elif time_remaining_ratio <= 0.25:  # Last 25%
                self.timer_display.configure(text_color="#FFA500")  # Orange
            else:
                self.timer_display.configure(text_color=POKER_COLORS["gold"])
        else:
            self.timer_display.configure(text_color=POKER_COLORS["gold"])

    def flash_timer_red(self):
        """Flash the timer red when time is up"""
        def flash(count=0):
            if count < 6:  # Flash 3 times
                color = "#FF0000" if count % 2 == 0 else POKER_COLORS["gold"]
                self.timer_display.configure(text_color=color)
                self.root.after(300, lambda: flash(count + 1))
        flash()
        
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