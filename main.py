from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import sys
import time
import logging


# Set up logging
logging.basicConfig(filename='trading_bot_logs.log', level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class TradingBot:
    def __init__(self):
        self.chrome_driver_path = "../chromedriver-linuxNew/chromedriver-linux64/chromedriver"
        self.service = Service(self.chrome_driver_path)
        self.driver = uc.Chrome(service=self.service)
        self.driver.maximize_window()

        # User settings
        self.user_id = 'ID: 34024297'
        self.investment_amount = None
        self.profit_target = None
        self.loss_threshold = None
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

    def get_user_inputs(self):
        """
        Get user inputs for bot configuration.
        """
        logging.info("User initiated bot configuration.")
        print("Please provide information for bot configuration:")
        self.investment_amount = float(input("Investment amount: "))
        self.profit_target = float(input("Profit target: "))
        self.loss_threshold = float(input("Loss threshold: "))
        logging.info(f"Bot configured with investment amount: {self.investment_amount}, "
                     f"profit target: {self.profit_target}, loss threshold: {self.loss_threshold}")
        print("Bot configuration complete.")

    def login(self):
        """
        Log in to the trading platform.
        """
        self.driver.get("https://qxbroker.com/en")
        self.find("xpath", "//*[@id='top']/div/div[1]/a[2]").click()
        time.sleep(4)

        login_email = "sameer192.official@gmail.com"
        password = ""
        with open("./pass.txt") as file:
            password = file.readline()

        self.find("xpath", '//*[@id="tab-1"]/form/div[1]/input').send_keys(login_email)
        self.find("xpath", '//*[@id="tab-1"]/form/div[2]/input').send_keys(password)
        self.find("xpath", '//*[@id="tab-1"]/form/button').click()
        logging.info("User initiated login to the trading platform.")
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

        self.find("xpath", '//*[@id="root"]/div/div[1]/header/div[8]/div[2]').click()

        # Check user ID
        user_id = self.find("class", 'usermenu__number').text
        if user_id != self.user_id:
            print('Invalid user ID. Please try again with correct credentials.')
            return

        self.find("xpath", '//*[@id="root"]/div/div[1]/header/div[8]/div[2]/div[2]/ul[1]/li[3]').click()
        time.sleep(5)

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
        self.current_currency_percentage_element =  self.find("class", 'section-deal__percent')

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
                self.pre_calculate_trade()

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
        balance = float(balance_text.replace("$", "").replace(",", ""))
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
        current_percentage = current_percentage.replace('%', '')
        current_percentage = float(current_percentage)/100
        
        # Account max and min balance checker
        acc_max_balance = (current_balance + self.investment_amount * current_percentage + self.investment_amount) >= self.account_max_balance
        acc_min_balance = current_balance <= self.account_min_balance
        print('Account max balance criteria met:', acc_max_balance)
        print('Account min balance criteria met:', acc_min_balance)

        self.profit_assumption = (self.investment_amount, self.next_button, acc_max_balance)
        self.loss_assumption = (self.next_investment * 2, self.down_button if self.next_button.text == "Up" else self.up_button, acc_min_balance)
        self.pre_calculator_handler = True

    def execute_trade_task(self):
        """
        Execute trade tasks based on the previous trade result.
        """
        print("Executing trade task")
        logging.info("Executing trade task")

        # Initial trade trigger directly
        if self.profit_assumption == None and self.loss_assumption == None:
            self.start_trade(self.next_investment, self.next_button)
            return

        # Check last trade result (profit or loss)
        result_element = self.find('xpath', '//*[@id="root"]/div/div[1]/main/div[2]/div[2]/div[2]/div[2]/div/div[4]/div')
        print('Last trade result:', result_element.text)

        # Depending on the previous trade result, set the next trade parameters
        if result_element.text == '0.00 $':  # Assume it's a loss
            print('Loss occurred. Adjusting parameters for the next trade...')
            logging.warning("Loss occurred. Adjusting parameters for the next trade.")

            self.next_investment, self.next_button, stop_bot = self.loss_assumption  # Unpack the tuple
            if stop_bot:
                print("Your loss criteria met. Stopping the bot.")
                logging.info("User-defined loss criteria met. Stopping the bot.")
                sys.exit()
        else:  # Assume it's a profit
            print('Profit earned. Preparing for the next trade...')
            logging.info(f"Profit earned. Preparing for the next trade. {result_element.text}")
            self.next_investment, self.next_button, stop_bot = self.profit_assumption  # Unpack the tuple
            if stop_bot:
                print("Your profit criteria met. Stopping the bot.")
                logging.info("User-defined profit criteria met. Stopping the bot.")
                sys.exit()

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
        logging.info(f"Trade started. Investment: {investment}, Selected button: {button.text}")


if __name__ == "__main__":
    bot = TradingBot()
    bot.get_user_inputs()  
    bot.login()
