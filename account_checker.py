# v1.0 8/7/2024
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time, logging
#logging.basicConfig(level=10)  # Enable to if there's issues so you can see what's wrong and where

with open("output.log", "a") as file:  # Start log with date and time
	file.write("*********************************\nCurrent date: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') \
	 + "\n*********************************\n\n")

def read_credentials(file_path):  # Function to read credentials from a file
	credentials = []
	with open(file_path, 'r') as file:
		for line in file:
			line = line.strip()
			if not line or line.startswith('#'):  # Skip empty lines and comment lines
				continue
			email, password = line.split(',')
			credentials.append((email, password))
	return credentials

def load_cookies(driver, email):  # Function to load cookies
	with open("cookies.txt", "r") as file:
		for line in file:
			if not line or line.startswith('#'):  # Skip empty lines and comment lines
				continue
			stored_email, cookies = line.strip().split(',', 1)
			if stored_email == email:
				for cookie in eval(cookies):  # Use eval to convert string back to list
					driver.add_cookie(cookie)
				break

# Read credentials
credentials = read_credentials("credentials.txt")
total_accounts = len(credentials)

print("Make sure you run get_cookies.py first and that your cookies.txt has cookies for any account you want to use.")
input("Read the help doc if you're unsure about anything. Otherwise press <ENTER> to begin.\n")

for index, (myMperksEmail, myMperksPassword) in enumerate(credentials):  # Loop will try every login specified in the credentials.txt
	driver = None
	try:
		options = Options()
		options.add_argument('--disable-popup-blocking')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		#options.add_argument('--headless')
		#options.add_argument('--disable-gpu')
		options.add_argument("--disk-cache-size=300000000")  # limiting the cache storage to 300 MB
		options.add_argument("--incognito")

		driver = uc.Chrome(options=options) #, browser_executable_path="/usr/bin/chromium-browser", driver_executable_path="/tmp/chromedriver")

		with open("output.log", "a") as file:  # Add  account email to log
			file.write("Account: " + str(myMperksEmail) + "\n")

		# Load Meijer page, wait, inject cookie, reload page
		driver.get('https://www.meijer.com/shopping/mPerks.html')
		time.sleep(5)
		load_cookies(driver, myMperksEmail)
		driver.get('https://www.meijer.com/shopping/mPerks.html')
		time.sleep(2)

		# Grab total MPerks Points
		mperks_points = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="user-info__points"]'))).text
		mperks_points_num = mperks_points.split()[0]  # Gets only the first section which should be numbers only
		time.sleep(2)

		# Show amount of unused redeemed rewards
		mperks_rewards = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="rewards-tab-tab"]'))).text
		if mperks_rewards.split('(')[-1].split(')')[0] == "0":  # Checks tab name to total pending rewards
			with open("output.log", "a") as file:
				file.write("There are no rewards waiting to be used\n")
			time.sleep(2)
		else:  # If tab name is anything else like "1", "3", etc, get the value of every reward along with expiry date
			mperks_rewards_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="rewards-tab-tab"]')))
			mperks_rewards_tab.click()
			rewards_classes = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@class, "card rounded mperks-rewards-tile")]')))
			time.sleep(1)
			for rewards_class in rewards_classes:  # Gets text of one or more unused reward tiles
				try:
					# Get text from mperks-rewards-tile__price-title -> ads-price
					save_amount = rewards_class.find_element(By.XPATH, './/div[contains(@class, "mperks-rewards-tile__price-title")]//span[contains(@class, "ads-price")]').text
					# Get text from mperks-rewards-tile__body-text
					save_on_what = rewards_class.find_element(By.CLASS_NAME, 'mperks-rewards-tile__body-text').text
					# Get text from mperks-rewards-tile__valid-text (or a class that contains it)
					valid_thru = rewards_class.find_element(By.XPATH, './/*[contains(@class, "mperks-rewards-tile__valid-text")]').text
					full_reward_text = f"{save_amount} on {save_on_what}. {valid_thru}."
					with open("output.log", "a") as file:
						file.write("Unused reward found: " + str(full_reward_text) + "\n")
					time.sleep(1)
				except Exception as e:
					print(f"An error occurred while processing a rewards class:\n\n{e}\n")

		# Check for GC promo available
		mperks_earn_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="earn-tab-tab"]')))
		mperks_earn_tab.click()  # Clicks on the "earn" tab found above
		time.sleep(2)
		try:  # Searches for a earn task that has the GC specific photo and then saves the earn text in gc_promo_result
			gc_img_class = driver.find_element(By.XPATH, '//img[@class="mperks-earn-tile-update__image" and @src="https://static.meijer.com/DigitalCoupon/GiftCards.jpg"]')
			gc_element = gc_img_class.find_element(By.XPATH, '..//..//..//..')  # Navigate up to the card element
			title_element_text = gc_element.find_element(By.CLASS_NAME, 'card-body__title').text
			description_element = gc_element.find_element(By.CLASS_NAME, 'mperks-earn-tile-update__description')
			description_element_text  = description_element.find_element(By.CLASS_NAME, 'ads-paragraph').text
			through_element_text = gc_element.find_element(By.CLASS_NAME, 'mperks-earn-tile-update__through-text').text
			gc_promo_result = f'Current GC promo: {title_element_text} {description_element_text}. {through_element_text}.'
		except NoSuchElementException:  # No GC promo
			gc_promo_result = "Current GC promo: No promo found"
		with open("output.log", "a") as file:
			file.write("Total mPerks points: " + str(mperks_points_num) + "\n" + str(gc_promo_result) + "\n\n")
	except Exception as e:  # Issue checking the acount
		with open("output.log", "a") as file:
			file.write("An error occurred while checking " + str(myMperksEmail) + "\n")
		print(f"\nAn error occurred for {myMperksEmail}: \n\n{e}\n")
	finally:  # Once mPerks points, rewards, and promos have been checked
		if driver:
			driver.quit()  # Ensures broswer gets closed
		if index == total_accounts - 1:  # Run if this was the last account
			print("Done checking all accounts in the credentials file. Results saved to output.log.\n")
			with open("output.log", "a") as file:
				file.write("\n\n")  # Adding blank lines to end of file
		else:  # More accounts, finish and restart 'for' loop
			print(f"Finished checking {myMperksEmail}. Waiting 15 seconds before checking the next account.")
			time.sleep(15)

