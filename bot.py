from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import logging
import urllib3

# Disable urllib3 warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    filename="trading_bot_logs.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class TradingBot:
    def __init__(self):
        print("Bot Trying to Started by app.py")

        self.chrome_driver_path = (
            "./chromedriver/chromedriver"
            # ../chromedriver-linuxNew/chromedriver-linux64/chromedriver
        )
        self.service = Service(self.chrome_driver_path)
        self.driver = uc.Chrome(service=self.service, auto_download=False)
        self.driver.maximize_window()

        # Open the file in read mode
        with open("data.txt", "r") as file:
            # Read all lines from the file
            lines = file.readlines()

        # Iterate through each line and extract information
        for line in lines:
            # Split each line into key and value
            key, value = line.strip().split(" = ")

            # Check if the key is 'password' or 'user'
            if key == "password":
                password = value
            elif key == "user":
                user_id = value
            elif key == "email":
                email = value

        # User settings
        self.investment_amount = None
        self.profit_target = None
        self.loss_threshold = None
        self.martingale_multiplier = None
        self.up_button = None
        self.down_button = None
        self.investment_input = None
        self.next_investment = None
        self.next_button = None
        self.profit_assumption = None
        self.loss_assumption = None
        self.pre_calculator_handler = False
        self.current_currency_percentage_element = None
        self.balance_element = None
        self.account_min_balance = None
        self.account_max_balance = None
        self.password = password
        self.user_id = user_id
        self.email = email
        self.loss_handler = 0
    def find(self, method, value):
        """
        Find element using the specified method.

        Args:
            method (str): Locator method (e.g., 'xpath', 'class', etc.).
            value (str): Locator value.

        Returns:
            WebElement: Found element.

        Raises:
            ValueError: If an invalid locator method is provided.
        """
        if method == "xpath":
            return self.driver.find_element(By.XPATH, value)
        elif method == "id":
            return self.driver.find_element(By.ID, value)
        elif method == "name":
            return self.driver.find_element(By.NAME, value)
        elif method == "class":
            return self.driver.find_element(By.CLASS_NAME, value)
        elif method == "css":
            return self.driver.find_element(By.CSS_SELECTOR, value)
        elif method == "link_text":
            return self.driver.find_element(By.LINK_TEXT, value)
        elif method == "partial_link_text":
            return self.driver.find_element(By.PARTIAL_LINK_TEXT, value)
        else:
            raise ValueError("Invalid locator method provided")

    def user_start_logs(self):
        """
        Get user inputs for bot configuration.
        """
        logging.info("User initiated bot configuration.")
        print("Please provide information for bot configuration:")

        # self.investment_amount = float(input("Investment amount: "))
        # self.profit_target = float(input("Profit target: "))
        # self.loss_threshold = float(input("Loss threshold: "))

        logging.info(
            f"Bot configured with investment amount: {self.investment_amount}, "
            f"profit target: {self.profit_target}, loss threshold: {self.loss_threshold}"
            f" martingale multiplier: {self.martingale_multiplier} times"
        )
        print("Bot configuration complete.")

    def stop_trading(self):
        """
        Gracefully stop the main trading loop.
        """
        logging.info(f"Stopping the trading bot...\n\n")
        print("Stopping the trading bot...")

        # Temporarily adjust the log level to suppress warnings
        previous_log_level = logging.getLogger().getEffectiveLevel()
        logging.getLogger().setLevel(logging.ERROR)

        try:
            self.driver.quit()
        finally:
            # Restore the original log level
            logging.getLogger().setLevel(previous_log_level)

    def login(self):
        """
        Log in to the trading platform.
        """
        self.driver.get("http://qxbroker.com/en")
        self.find("xpath", "//*[@id='top']/div/div[1]/a[2]").click()
        time.sleep(4)

        self.find("xpath", '//*[@id="tab-1"]/form/div[1]/input').send_keys(self.email)
        self.find("xpath", '//*[@id="tab-1"]/form/div[2]/input').send_keys(
            self.password
        )
        self.find("xpath", '//*[@id="tab-1"]/form/button').click()
        logging.info("User initiated login to the trading platform.")
        self.user_start_logs()
        time.sleep(5)

        # Check OTP Popup
        try:
            otp_popup = self.find("xpath", "/html/body/div[2]/main/p")
            if otp_popup:
                time.sleep(20)
                self.start_demo_trading_check_user()
            else:
                time.sleep(5)
                self.start_demo_trading_check_user()

        except NoSuchElementException:
            time.sleep(5)
            self.start_demo_trading_check_user()

    def start_demo_trading_check_user(self):
        """
        Start demo trading after checking user credentials.
        """

        logging.info("User initiated demo trading.")

        self.find("xpath", '//*[@id="root"]/div/div[1]/header/div[7]/div[2]/div/div[2]').click()

        # Check user ID
        user_id = self.find("class", "usermenu__number").text
        if user_id != self.user_id:
            print("Invalid user ID. Please try again with correct credentials.")
            logging.warning(
                "Invalid user ID. Please try again with correct credentials.\n"
            )
            self.stop_trading()
            # return
        time.sleep(2)
        
        """
        Change live account demo trading.
        """

        self.find(
            "xpath",
            '//*[@id="root"]/div/div[1]/header/div[7]/div[2]/div[2]/ul[1]/li[3]',
        ).click()
        time.sleep(1)

        self.find(
            "xpath",
            '//*[@id="root"]/div/div[3]/div/div/div/div[2]/button',
        ).click()
        time.sleep(1)


        time.sleep(6)
        self.monitor_trading_time_get_buttons()

    def monitor_trading_buttons(self):
        """
        Monitor trading buttons and input elements.
        """
        self.up_button = self.find(
            "xpath",
            '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[6]/div[1]/button',
        )
        self.down_button = self.find(
            "xpath",
            '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[6]/div[4]/button',
        )
        self.investment_input = self.find(
            "xpath",
            '//*[@id="root"]/div/div[1]/main/div[2]/div[1]/div/div[5]/div[2]/div/div/input',
        )
        self.balance_element = self.find("class", "usermenu__info-balance")
        self.current_currency_percentage_element = self.find(
            "class", "section-deal__percent"
        )

    def monitor_trading_time_get_buttons(self):
        """
        Monitor trading time and execute trade tasks.
        """
        self.monitor_trading_buttons()  # Retrieve buttons and input once

        while True:
            trade_timing_element = self.find(
                "xpath", '//*[@id="root"]/div/div[1]/main/div[1]/div/div[2]/div[2]/div'
            )
            trade_timing = trade_timing_element.text

            # Split time to check if it's the start of a new minute
            time_parts = trade_timing.split(":")
            seconds_part = int(time_parts[2].split()[0])

            # Check if seconds part is 0 (indicating a new minute)
            if seconds_part == 0:
                self.execute_trade_task()  # Execute trade for every new minute
                time.sleep(50)  # Rest for 50 seconds after executing trade tasks

            elif self.pre_calculator_handler == False:
                print('before pre_calculate_trade')                
                self.pre_calculate_trade()
                print('after pre_calculate_trade')

            time.sleep(
                0.100
            )  # Wait for 100 milliseconds (0.1 seconds) before fetching the time again

    def get_balance(self):
        """
        Get user's balance from the platform.

        Returns:
            float: User's balance.
        """
        balance_text = self.balance_element.text
        print('balance getting')
        balance = float(balance_text.replace("$", "").replace(",", ""))
        print('balance get', balance)
        return balance

    def pre_calculate_trade(self):
        """
        Perform pre-calculation for the next trade.
        """
        print("Pre-calculation running")

        if self.next_investment == None and self.next_button == None:
            print("Initial investment setup")
            self.next_investment = self.investment_amount
            self.next_button = self.up_button
            self.pre_calculator_handler = True

            # Get account start balance and set min and max account range
            self.account_max_balance = self.get_balance() + self.profit_target
            self.account_min_balance = self.get_balance() - self.loss_threshold
            return

        current_balance = self.get_balance()

        # Check Current Perecentage of Currency
        current_percentage = self.current_currency_percentage_element.text
        current_percentage = current_percentage.replace("%", "")
        current_percentage = float(current_percentage) / 100
        mtg_checker = self.loss_handler + 1
        # Account max and min balance checker
        acc_max_balance = (
            current_balance
            + self.investment_amount * current_percentage
            + self.investment_amount
        ) >= self.account_max_balance
        acc_min_balance = current_balance <= self.account_min_balance
        print("Account max balance criteria met:", acc_max_balance)
        print("Account min balance criteria met:", acc_min_balance)

        self.profit_assumption = (
            self.investment_amount,
            self.next_button,
            acc_max_balance,
        )

        self.loss_assumption = (
            self.next_investment * self.martingale_multiplier,
            self.down_button if self.next_button.text == "Up" else self.up_button,
            acc_min_balance,
        )

        self.pre_calculator_handler = True

    def execute_trade_task(self):
        """
        Execute trade tasks based on the previous trade result.
        """
        print("Executing trade task")
        logging.info("Executing trade task")

        # Initial trade trigger directly
        if self.profit_assumption == None and self.loss_assumption == None:
            logging.info(f"Your Start Balance is {self.get_balance()}")
            self.start_trade(self.next_investment, self.next_button)
            return

        # Check last trade result (profit or loss)
        result_element = self.find(
            "xpath",
            '//*[@id="root"]/div/div[1]/main/div[2]/div[2]/div[2]/div[2]/div/div[4]/div',
        )
        print("Last trade result:", result_element.text)

        # Depending on the previous trade result, set the next trade parameters
        if result_element.text == "0.00 $":  # Assume it's a loss
            print("Loss occurred. Adjusting parameters for the next trade...")
            logging.warning("Loss occurred. Adjusting parameters for the next trade.")
            self.loss_handler = self.loss_handler + 1
            (
                self.next_investment,
                self.next_button,
                stop_bot,
            ) = self.loss_assumption  # Unpack the tuple
            if stop_bot:
                print("Your loss criteria met. Stopping the bot.")
                logging.info(f"Your Ending Balance is {self.get_balance()}\n")
                logging.info("User-defined loss criteria met. Stopping the bot.")
                self.stop_trading()

        else:  # Assume it's a profit
            print("Profit earned. Preparing for the next trade...")
            logging.info(
                f"Profit earned. Preparing for the next trade. {result_element.text}"
            )
            (
                self.next_investment,
                self.next_button,
                stop_bot,
            ) = self.profit_assumption  # Unpack the tuple
            
            self.loss_handler = 0
            if stop_bot:
                print("Your profit criteria met. Stopping the bot.")
                logging.info(f"Your Ending Balance is {self.get_balance()}\n")
                logging.info("User-defined profit criteria met. Stopping the bot.")
                self.stop_trading()

        # Perform trade
        self.start_trade(self.next_investment, self.next_button)

    def start_trade(self, investment, button):
        """
        Start the trade with the specified investment and button.

        Args:
            investment (float): Investment amount.
            button (WebElement): Trading button.

        Raises:
            SystemExit: If stop_bot criteria is met.
        """
        investment_input = self.investment_input

        # Select all existing text in the input field
        investment_input.send_keys(Keys.CONTROL + "a")

        # Set a new value in the input field
        investment_input.send_keys(investment)

        # Click the button to start the trade
        button.click()

        self.pre_calculator_handler = False
        print("Trade started. Investment:", investment)
        print("Selected button:", button.text)
        logging.info(
            f"Trade started. Investment: {investment}, Selected button: {button.text}"
        )


if __name__ == "__main__":
    try:
        bot = TradingBot()
        bot.login()

    except Exception as e:
        print(f"An error occurred during: {e}")
        # bot.stop_trading()