from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time, logging
#logging.basicConfig(level=10)  # Enable to if there's issues so you can see what's wrong and where

log_file = open("output.txt", "a")
log_file.write("*********************************\nCurrent date: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') \
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

def read_existing_cookies(file_path):
	cookies_dict = {}
	try:
		with open(file_path, 'r') as file:
			for line in file:
				email, cookies = line.strip().split(',', 1)
				cookies_dict[email] = cookies
	except FileNotFoundError:
		pass
	return cookies_dict

def save_cookies(driver, email):
	cookies = driver.get_cookies()
	cookies_str = str(cookies)
	existing_cookies = read_existing_cookies("cookies.txt")  # Load existing cookies
	existing_cookies[email] = cookies_str
	with open("cookies.txt", "w") as file:  # Write back all cookies to file
		for key, value in existing_cookies.items():
			file.write(f"{key},{value}\n")

def load_cookies(driver, email):
	cookies_dict = read_existing_cookies("cookies.txt")
	cookies = cookies_dict.get(email, "")
	if cookies:
		for cookie in eval(cookies):
			driver.add_cookie(cookie)

def initialize_driver():  # Set driver options
	options = Options()
	options.add_argument('--disable-popup-blocking')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument("--disk-cache-size=300000000")
	options.add_argument("--incognito")
	return uc.Chrome(options=options)

def get_account_selection(credentials):
	total_accounts = len(credentials)
	while True:
		print(f"\nDo you want to run for all accounts ({total_accounts}) or select specific accounts?")
		choice = input("Enter 1 for all accounts, enter 2 to select specific accounts: ")
		if choice == '1':
			return list(range(total_accounts))  # Return all accounts
		elif choice == '2':
			print("\nAvailable accounts:")
			for i, (email, _) in enumerate(credentials, start=1):
				print(f"{i}. {email}")  # Display email with its corresponding number choice
			selected_indices = input("\nEnter account numbers separated by commas (e.g., 1,2,4): ")
			try:
				selected_indices = [int(i.strip()) - 1 for i in selected_indices.split(',') if i.strip().isdigit()]
				if all(0 <= idx < total_accounts for idx in selected_indices):  # Check for valid indices
					return selected_indices
				else:
					print(f"Please enter valid account numbers between 1 and {total_accounts}.")
			except ValueError:
				print("Invalid input. Please enter numbers only.")
		else:
			print("Invalid choice. Defaulting to check all accounts.")
			return list(range(total_accounts))

def get_cookies(credentials, selected_accounts):
	for index in selected_accounts:  # Runs for all selected accounts
		myMperksEmail, myMperksPassword = credentials[index]
		driver = None  # Initial driver state
		try:
			driver = initialize_driver()
			print(f"Logging into {myMperksEmail}, please wait... ")

			# Load Meijer page and click top right sign in
			driver.get('https://www.meijer.com/shopping/mPerks.html')
			sign_in_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="signin"]')))
			sign_in_1.click()
			sign_in_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="button-container"]')))
			sign_in_2.click()
			time.sleep(2)  # Sometimes it needs an extra 2 seconds, otherwise it takes a shit

			# Find username input field using XPath, enter the username, and click next
			username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="identifier"]')))
			username_field.send_keys(myMperksEmail)
			next_button = driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div/div/div/div[2]/form/div/div[4]/button')
			next_button.click()

			try:  # Waits 5 seconds to detect mPerks login error (Rate limiting? Exact cause unknown.)
				WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "unexpected internal error")]')))
				print("Detected mPerks error after entering email. Refreshing the page should return to email entry.")
				print("Manually enter the email and continue.")
				input("If you have successfully entered the email and are now at the password screen, press <ENTER> to continue.")
			except:  # No error message detected
				pass  # Continue script as normal

			# Find password input field using XPath, enter the password, and click submit
			password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="credentials.passcode"]')))
			password_field.send_keys(myMperksPassword)
			submit_button = driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div/div/div/div[2]/form/div/div[4]/button')
			submit_button.click()

			try:  # Check for mPerks asing for only verification email
				WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[text()="Send Me an Email"]')))
				print("Verification email detected. Complete the 2FA process and log in.")
				input("Once logged in, press <ENTER> to continue the script.")
				email_2fa_found = True  # Verification email alone was asked, set to true to skip the email/phone combo
			except:  # Didn't find the email verification page
				email_2fa_found = False  # Verification email alone was not asked, set to false to check for email/phone combo

			if not email_2fa_found:  # If the verification email alone was not asked
				try:  # Check for mPerks asing for verification email OR phone number
					WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//h2[text()="How Do You Want To Verify?"]')))
					print("Verification email/phone detected. Complete the 2FA process and log in.")
					input("Once logged in, press <ENTER> to continue the script.")
				except:  # Didn't find the email/phone combo page either
					print("No 2FA request found, moving on.")

			# Checks to make sure points total loaded. If they didn't, login failed. This will throw an exception
			print("Making sure the account is logged in, please wait...")
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="user-info__points"]')))
			save_cookies(driver, myMperksEmail)  # Save cookies after successful login
			print(f"Your cookie has been saved for {myMperksEmail}\n")

		except Exception as e:  # Issue checking the acount. Prints error to console.
			print(f"An error occurred for {myMperksEmail}: {e}\n")
		finally:
			if driver:
				driver.quit()  # Ensures broswer gets closed
			if index == len(selected_accounts) - 1:
				print("Done processing all accounts. Cookies.txt should have an entry for every account in credentials.txt.\n")
			else:
				print("Waiting 20 seconds before logging into the next account.\n")
				time.sleep(20)

def check_account_status(credentials, selected_accounts):
	for index in selected_accounts:
		myMperksEmail, myMperksPassword = credentials[index]
		driver = None
		try:
			driver = initialize_driver()

			log_file.write("Account: " + str(myMperksEmail) + "\n")

			# Load Meijer page, wait, inject cookie, reload page
			driver.get('https://www.meijer.com/shopping/mPerks.html')
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
				log_file.write("There are no rewards waiting to be used\n")
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
						log_file.write("Unused reward found: " + str(full_reward_text) + "\n")
						time.sleep(1)
					except Exception as e:
						print(f"An error occurred while processing a rewards class:\n\n{e}\n")
						log_file.write("An error occurred while processing a rewards class")
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
			log_file.write("Total mPerks points: " + str(mperks_points_num) + "\n" + str(gc_promo_result) + "\n\n")
		except Exception as e:  # Issue checking the acount
			print(f"An error occurred for {myMperksEmail}: {e}\n")
		finally:
			if driver:
				driver.quit()  # Ensures broswer gets closed
			#if index == len(selected_accounts) - 1:
			#	print("Done processing all accounts.\n\n\n")
			print(f"Finished checking {myMperksEmail}. Waiting 15 seconds before checking the next account.")
			time.sleep(15)
	print("Done checking all accounts, returning to main menu.\n")
	log_file.write("\n\n")

def main():
	credentials = read_credentials("credentials.txt")
	while True:
		print("\n1. Get cookies\n2. Check account stats\n8. Instructions\n9. Quit\n")
		choice = input("Enter your choice: ")
		if choice == '1':
			selected_accounts = get_account_selection(credentials)
			get_cookies(credentials, selected_accounts)
		elif choice == '2':
			selected_accounts = get_account_selection(credentials)
			check_account_status(credentials, selected_accounts)
		elif choice == '8':
			print("\nPut all account logins into credentials.txt in the form of email,password")
			print("Select 'Get cookies' - This will log into the selected accounts and save a session cookie for each login")
			print("Getting cookies may prompt 2FA - Follow the instructions in the console")
			print("Once you have cookies saved into cookies.txt, you can check your account stats")
			print("All infomation will be put into a file called output.txt")
			print("Help document located at - 'https://github.com/Cactus356/mperks-account-automation/blob/main/HELPDOCS.md'")
		elif choice == '9':
			print("Quitting.")
			log_file.close()
			break
		else:
			print("Invalid choice, please enter 1, 2, 8, or 9.")

if __name__ == "__main__":
    main()
