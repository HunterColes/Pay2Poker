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

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class PokerPayoutCalculator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Poker Payout Calculator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Default payout weights for top 9 positions
        self.default_weights = [35, 20, 15, 10, 8, 6, 3, 2, 1]
        self.current_weights = self.default_weights.copy()
        
        # Variables
        self.num_players = tk.IntVar(value=9)
        self.buy_in = tk.DoubleVar(value=20.0)
        self.food_per_player = tk.DoubleVar(value=5.0)
        self.bounty_per_player = tk.DoubleVar(value=2.0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🃏 Poker Payout Calculator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Create main sections
        self.create_player_section(main_frame)
        self.create_pool_section(main_frame)
        self.create_weights_section(main_frame)
        self.create_calculate_section(main_frame)
        self.create_results_section(main_frame)
        
    def create_player_section(self, parent):
        """Create the player count section"""
        player_frame = ctk.CTkFrame(parent)
        player_frame.pack(fill="x", pady=(0, 15))
        
        # Player count label
        player_label = ctk.CTkLabel(
            player_frame, 
            text="Number of Players:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        player_label.pack(pady=(15, 5))
        
        # Player slider
        self.player_slider = ctk.CTkSlider(
            player_frame,
            from_=3,
            to=30,
            number_of_steps=27,
            variable=self.num_players,
            command=self.on_player_change
        )
        self.player_slider.pack(pady=5, padx=20, fill="x")
        
        # Player count display
        self.player_count_label = ctk.CTkLabel(
            player_frame,
            text=f"Players: {self.num_players.get()}",
            font=ctk.CTkFont(size=14)
        )
        self.player_count_label.pack(pady=(5, 15))
        
    def create_pool_section(self, parent):
        """Create the pool configuration section"""
        pool_frame = ctk.CTkFrame(parent)
        pool_frame.pack(fill="x", pady=(0, 15))
        
        pool_title = ctk.CTkLabel(
            pool_frame, 
            text="Pool Configuration", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        pool_title.pack(pady=(15, 10))
        
        # Buy-in entry
        buy_in_frame = ctk.CTkFrame(pool_frame, fg_color="transparent")
        buy_in_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(buy_in_frame, text="Buy-in per player ($):").pack(side="left")
        buy_in_entry = ctk.CTkEntry(buy_in_frame, textvariable=self.buy_in, width=100)
        buy_in_entry.pack(side="right")
        
        # Food pool entry
        food_frame = ctk.CTkFrame(pool_frame, fg_color="transparent")
        food_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(food_frame, text="Food pool per player ($):").pack(side="left")
        food_entry = ctk.CTkEntry(food_frame, textvariable=self.food_per_player, width=100)
        food_entry.pack(side="right")
        
        # Bounty pool entry
        bounty_frame = ctk.CTkFrame(pool_frame, fg_color="transparent")
        bounty_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkLabel(bounty_frame, text="Bounty per player ($):").pack(side="left")
        bounty_entry = ctk.CTkEntry(bounty_frame, textvariable=self.bounty_per_player, width=100)
        bounty_entry.pack(side="right")
        
    def create_weights_section(self, parent):
        """Create the payout weights configuration section"""
        weights_frame = ctk.CTkFrame(parent)
        weights_frame.pack(fill="x", pady=(0, 15))
        
        weights_title = ctk.CTkLabel(
            weights_frame, 
            text="Payout Weights (Customizable)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        weights_title.pack(pady=(15, 10))
        
        # Weights display and edit
        self.weights_display = ctk.CTkTextbox(weights_frame, height=80)
        self.weights_display.pack(fill="x", padx=20, pady=5)
        self.update_weights_display()
        
        # Weights control buttons
        weights_btn_frame = ctk.CTkFrame(weights_frame, fg_color="transparent")
        weights_btn_frame.pack(pady=(5, 15))
        
        edit_weights_btn = ctk.CTkButton(
            weights_btn_frame,
            text="Edit Weights",
            command=self.edit_weights
        )
        edit_weights_btn.pack(side="left", padx=5)
        
        reset_weights_btn = ctk.CTkButton(
            weights_btn_frame,
            text="Reset to Default",
            command=self.reset_weights
        )
        reset_weights_btn.pack(side="left", padx=5)
        
    def create_calculate_section(self, parent):
        """Create the calculate button section"""
        calculate_btn = ctk.CTkButton(
            parent,
            text="Calculate Payouts",
            command=self.calculate_payouts,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        calculate_btn.pack(pady=15)
        
    def create_results_section(self, parent):
        """Create the results display section"""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        results_title = ctk.CTkLabel(
            results_frame, 
            text="Payout Results", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_title.pack(pady=(15, 10))
        
        # Results display
        self.results_display = ctk.CTkTextbox(results_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.results_display.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
    def on_player_change(self, value):
        """Handle player count slider change"""
        players = int(value)
        self.player_count_label.configure(text=f"Players: {players}")
        
    def update_weights_display(self):
        """Update the weights display textbox"""
        weights_text = "Current weights: " + ", ".join(map(str, self.current_weights))
        weights_text += f"\n(Will use first {self.calculate_payout_positions()} positions based on player count)"
        self.weights_display.delete("1.0", "end")
        self.weights_display.insert("1.0", weights_text)
        
    def calculate_payout_positions(self):
        """Calculate how many positions get paid based on player count"""
        return math.ceil(self.num_players.get() / 3)
        
    def edit_weights(self):
        """Open dialog to edit payout weights"""
        dialog = WeightsEditDialog(self.root, self.current_weights)
        if dialog.result:
            self.current_weights = dialog.result
            self.update_weights_display()
            
    def reset_weights(self):
        """Reset weights to default values"""
        self.current_weights = self.default_weights.copy()
        self.update_weights_display()
        
    def calculate_payouts(self):
        """Calculate and display the payout results"""
        try:
            num_players = self.num_players.get()
            buy_in = self.buy_in.get()
            food_per_player = self.food_per_player.get()
            bounty_per_player = self.bounty_per_player.get()
            
            # Calculate pools
            main_pool = num_players * buy_in
            food_pool = num_players * food_per_player
            bounty_pool = num_players * bounty_per_player
            
            # Calculate payout positions
            payout_positions = self.calculate_payout_positions()
            
            # Get relevant weights
            relevant_weights = self.current_weights[:payout_positions]
            total_weight = sum(relevant_weights)
            
            # Calculate individual payouts
            payouts = []
            for i, weight in enumerate(relevant_weights):
                payout = (weight / total_weight) * main_pool
                payouts.append((i + 1, payout))
                
            # Format results
            self.display_results(payouts, main_pool, food_pool, bounty_pool, num_players)
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for all fields.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def display_results(self, payouts: List[Tuple[int, float]], main_pool: float, 
                       food_pool: float, bounty_pool: float, num_players: int):
        """Display the calculated results"""
        result_text = f"🏆 POKER TOURNAMENT PAYOUT RESULTS 🏆\n"
        result_text += "=" * 50 + "\n\n"
        
        result_text += f"👥 Total Players: {num_players}\n"
        result_text += f"💰 Main Prize Pool: ${main_pool:.2f}\n"
        result_text += f"🍕 Food Pool: ${food_pool:.2f}\n"
        result_text += f"🎯 Bounty Pool: ${bounty_pool:.2f}\n"
        result_text += f"💵 Total Collected: ${main_pool + food_pool + bounty_pool:.2f}\n\n"
        
        result_text += "🏅 MAIN TOURNAMENT PAYOUTS:\n"
        result_text += "-" * 30 + "\n"
        
        for position, payout in payouts:
            position_emoji = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
            emoji = position_emoji[position - 1] if position <= len(position_emoji) else "🏅"
            result_text += f"{emoji} {self.get_position_suffix(position)} Place: ${payout:.2f}\n"
            
        result_text += "\n💡 ADDITIONAL POOLS:\n"
        result_text += "-" * 20 + "\n"
        result_text += f"🍕 Food Pool: ${food_pool:.2f} (to be used for food/drinks)\n"
        result_text += f"🎯 Bounty Pool: ${bounty_pool:.2f} (${bounty_pool/num_players:.2f} per player)\n"
        result_text += "   💀 Each knockout earns the bounty amount!\n\n"
        
        result_text += "📊 PAYOUT BREAKDOWN:\n"
        result_text += "-" * 20 + "\n"
        total_paid = sum(payout[1] for payout in payouts)
        result_text += f"Total Main Payouts: ${total_paid:.2f}\n"
        result_text += f"Remaining in Main Pool: ${main_pool - total_paid:.2f}\n"
        
        # Clear and display results
        self.results_display.delete("1.0", "end")
        self.results_display.insert("1.0", result_text)
        
    def get_position_suffix(self, position: int) -> str:
        """Get the appropriate suffix for position numbers"""
        if 10 <= position % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(position % 10, "th")
        return f"{position}{suffix}"
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


class WeightsEditDialog:
    def __init__(self, parent, current_weights):
        self.result = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Edit Payout Weights")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        # Create UI
        self.setup_dialog_ui(current_weights)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def setup_dialog_ui(self, current_weights):
        """Setup the dialog UI"""
        # Title
        title = ctk.CTkLabel(
            self.dialog, 
            text="Edit Payout Weights", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=20)
        
        # Instructions
        instructions = ctk.CTkLabel(
            self.dialog,
            text="Enter comma-separated weights (e.g., 35,20,15,10,8,6,3,2,1):",
            wraplength=350
        )
        instructions.pack(pady=10)
        
        # Entry field
        self.weights_entry = ctk.CTkEntry(self.dialog, width=350)
        self.weights_entry.pack(pady=10)
        self.weights_entry.insert(0, ",".join(map(str, current_weights)))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_weights
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        )
        cancel_btn.pack(side="left", padx=10)
        
    def save_weights(self):
        """Save the edited weights"""
        try:
            weights_text = self.weights_entry.get().strip()
            weights = [int(w.strip()) for w in weights_text.split(",") if w.strip()]
            
            if not weights:
                raise ValueError("No weights entered")
                
            if any(w <= 0 for w in weights):
                raise ValueError("All weights must be positive")
                
            self.result = weights
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", 
                               "Please enter valid positive integers separated by commas.")


if __name__ == "__main__":
    app = PokerPayoutCalculator()
    app.run()