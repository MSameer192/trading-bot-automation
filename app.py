import tkinter as tk
from threading import Thread
from bot import TradingBot
from tkinter import messagebox
from datetime import datetime



class TradingApp:
    def __init__(self, root):
        self.root = root
        self.center_window(self.root, 500, 350)
        self.root.title("Trading Bot GUI")
        self.root.configure(bg="black")  # Set the background color to black

        self.base_amount_var = tk.DoubleVar()
        self.profit_target_var = tk.DoubleVar()
        self.loss_threshold_var = tk.DoubleVar()
        self.martingale_multiplier_var = tk.DoubleVar()
        self.is_trading = False  # Track the trading state
        self.thread = None  # Thread to run the trading bot

        self.create_widgets()

    def center_window(self, window, window_width, window_height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_widgets(self):
        # Adjusting column weights to make both columns take up equal space
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        # Welcome Heading
        welcome_label = tk.Label(
            self.root,
            text="Welcome to Quotex Trading Bot",
            bg="black",
            fg="yellow",
            font=("Times New Roman", 20),
        )
        welcome_label.grid(
            row=0, column=0, columnspan=2, pady=(20, 20)
        )  # Centered heading

        # Base Trade Amount
        base_amount_label = tk.Label(
            self.root,
            text="Base Trade Amount:",
            fg="yellow",
            font=("Helvetica", "13"),
            bg="black",
            padx=7,
            pady=7,
            anchor="w",  # Left align the label text
        )
        base_amount_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        base_amount_entry = tk.Entry(
            self.root, textvariable=self.base_amount_var, bg="black", fg="yellow"
        )
        base_amount_entry.grid(row=1, column=1, pady=(0, 5))

        # Target Profit
        profit_target_label = tk.Label(
            self.root,
            text="Target Profit:",
            fg="yellow",
            font=("Helvetica", "13"),
            bg="black",
            padx=7,
            pady=7,
            anchor="w",  # Left align the label text
        )
        profit_target_label.grid(row=2, column=0, sticky="w", pady=(0, 5))

        profit_target_entry = tk.Entry(
            self.root, textvariable=self.profit_target_var, bg="black", fg="yellow"
        )
        profit_target_entry.grid(row=2, column=1, pady=(0, 5))

        # Stop Loss
        loss_threshold_label = tk.Label(
            self.root,
            text="Stop Loss:",
            fg="yellow",
            font=("Helvetica", "13"),
            bg="black",
            padx=7,
            pady=7,
            anchor="w",  # Left align the label text
        )
        loss_threshold_label.grid(row=3, column=0, sticky="w", pady=(0, 5))

        loss_threshold_entry = tk.Entry(
            self.root, textvariable=self.loss_threshold_var, bg="black", fg="yellow"
        )
        loss_threshold_entry.grid(row=3, column=1, pady=(0, 5))

        # Martingale Multiplier Time
        martingale_multiplier_label = tk.Label(
            self.root,
            text="Martingale Multiplier Time:",
            fg="yellow",
            font=("Helvetica", "13"),
            bg="black",
            padx=7,
            pady=7,
            anchor="w",  # Left align the label text
        )
        martingale_multiplier_label.grid(row=4, column=0, sticky="w", pady=(0, 5))

        martingale_multiplier_entry = tk.Entry(
            self.root,
            textvariable=self.martingale_multiplier_var,
            bg="black",
            fg="yellow",
        )
        martingale_multiplier_entry.grid(row=4, column=1, pady=(0, 5))

        # Start/Stop Button
        self.start_stop_button = tk.Button(
            self.root,
            text="Start Trading",
            command=self.toggle_trading,
            width=15,
            height=2,
            bg="black",
            fg="yellow",
        )
        self.start_stop_button.grid(
            row=5, column=0, columnspan=2, pady=(15, 10)
        )  # Centered button


    def check_license(self):
        # Hardcoded license expiration date (March 23, 2024)
        license_expiration_date = datetime(2024, 5, 26)
        
        # Get the current date
        current_date = datetime.now()

        # Check if the license is still valid
        if current_date <= license_expiration_date:
            return True
        else:
            return False
        
    def toggle_trading(self):
        if self.is_trading == False:
            # If not currently trading, start trading


            # Check license before starting trading
            if not self.check_license():
                messagebox.showwarning(
                    "License Warning", "Your license has expired. Please renew."
                )
                return
            
            # Check if any input field is empty
            if (
                not self.base_amount_var.get()
                or not self.profit_target_var.get()
                or not self.loss_threshold_var.get()
                or not self.martingale_multiplier_var.get()
            ):
                messagebox.showwarning(
                    "Input Warning", "Please fill in all the input fields."
                )
                return

            # Get user inputs and start the trading bot
            self.is_trading = True
            self.start_stop_button["text"] = "Stop Trading"
            self.root.update()  # Force GUI update
            self.start_trading()

        else:
            # If currently trading, stop trading
            self.is_trading = False
            self.start_stop_button["text"] = "Start Trading"
            self.root.update()  # Force GUI update

            # Stop the trading bot and clear input fields
            self.clear_input_fields()
            self.stop_trading()

    def start_trading(self):
        # Get user inputs
        base_amount = self.base_amount_var.get()
        profit_target = self.profit_target_var.get()
        loss_threshold = self.loss_threshold_var.get()
        martingale_multiplier = self.martingale_multiplier_var.get()

        # Create an instance of TradingBot
        self.bot = TradingBot()
        self.bot.investment_amount = base_amount
        self.bot.profit_target = profit_target
        self.bot.loss_threshold = loss_threshold
        self.bot.martingale_multiplier = martingale_multiplier

        # Start the trading bot in a separate thread
        self.thread = Thread(target=self.run_trading_bot)
        self.thread.start()

    def run_trading_bot(self):
        try:
            self.bot.login()

        except Exception as e:
            print(f"An error occurred during trading: {e}")

    def clear_input_fields(self):
        # Clear all input fields
        self.base_amount_var.set("")
        self.profit_target_var.set("")
        self.loss_threshold_var.set("")
        self.martingale_multiplier_var.set("")

    def stop_trading(self):
        if self.is_trading:
            self.is_trading = False

        # Stop the trading bot
        if self.thread and self.thread.is_alive():
            self.bot.stop_trading()
            self.thread.join()  # Wait for the thread to finish


if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()
