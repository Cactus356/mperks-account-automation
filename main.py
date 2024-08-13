#v2.2 8/13/24
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time, logging
#logging.basicConfig(level=10)  # Enable to if there's issues so you can see what's wrong and where

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
					print(f"Please enter valid account numbers between 1 and {total_accounts}.\n")
			except ValueError:
				print("Invalid input. Please enter numbers only.\n")
		else:
			print("Invalid choice. Defaulting to check all accounts.\n")
			return list(range(total_accounts))

def get_cookies(credentials, selected_accounts):
	total_accounts = len(selected_accounts)
	for index, account_index in enumerate(selected_accounts):  # Runs for all selected accounts
		date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		log_file = open("output.txt", "a")
		myMperksEmail, myMperksPassword = credentials[account_index]
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
			log_file.write(f"Cookie saved for {myMperksEmail} at {date_time}\n")
		except Exception as e:  # Issue checking the acount. Prints error to console.
			print(f"An error occurred for {myMperksEmail}: {e}\n")
			log_file.write(f"Error saving cookie for {myMperksEmail} at {date_time}\n")
		finally:
			if driver:
				driver.quit()  # Ensures broswer gets closed
			if index == total_accounts - 1:
				print("Done getting cookies for the selected accounts. Cookies saved to cookies.txt")
				log_file.write("\n\n")
			else:
				print("Waiting 20 seconds before logging into the next account.\n")
				time.sleep(20)
		log_file.close()

def check_account_status(credentials, selected_accounts):
	total_accounts = len(selected_accounts)
	for index, account_index in enumerate(selected_accounts):  # Runs for all selected accounts
		date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		log_file = open("output.txt", "a")
		myMperksEmail, myMperksPassword = credentials[account_index]
		driver = None
		try:
			driver = initialize_driver()

			log_file.write(f"Checking account {myMperksEmail} at {date_time} \n")

			# Load Meijer page, wait, inject cookie, reload page
			driver.get('https://www.meijer.com/shopping/mPerks.html')
			load_cookies(driver, myMperksEmail)
			driver.refresh()
			time.sleep(2)

			# Grab total MPerks Points
			mperks_points = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="user-info__points"]'))).text
			mperks_points_num = mperks_points.split()[0]  # Gets only the first section which should be numbers only
			time.sleep(2)

			# Show amount of unused redeemed rewards
			mperks_rewards = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="rewards-tab-tab"]'))).text
			if mperks_rewards.split('(')[-1].split(')')[0] == "0":  # Checks tab name to total pending rewards
				log_file.write(f"There are no rewards waiting to be used.\n")
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
						log_file.write("An error occurred while processing a rewards class.\n")
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
			log_file.write("An error occurred checking {myMperksEmail}\n")
		finally:
			if index == total_accounts - 1:
				print(f"Finished checking {myMperksEmail}.\n")
				print("Done checking the selected accounts. Results saved to output.txt.\n")
				log_file.write("\n\n")
			else:
				print(f"Finished checking {myMperksEmail}. Waiting 15 seconds before checking the next account.")
				time.sleep(15)
			if driver:
				driver.quit()  # Ensures broswer gets closed
		log_file.close()

def redeem_points(credentials, selected_accounts):
	total_accounts = len(selected_accounts)
	for index, account_index in enumerate(selected_accounts):  # Runs for all selected accounts
		date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		log_file = open("output.txt", "a")
		myMperksEmail, myMperksPassword = credentials[account_index]
		driver = None
		try:
			driver = initialize_driver()

			log_file.write(f"Trying to redeem for account {myMperksEmail} at {date_time} \n")

			# Load Meijer page, wait, inject cookie, reload page
			driver.get('https://www.meijer.com/shopping/mPerks.html')
			load_cookies(driver, myMperksEmail)
			driver.refresh()
			time.sleep(2)

			# Grab total MPerks Points
			mperks_points = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="user-info__points"]'))).text
			mperks_points_num = int(mperks_points.split()[0])  # Gets only the first section which should be numbers only
			time.sleep(2)

			# Make sure the redeem tab is selected
			mperks_redeem_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="redeem-tab-tab"]')))
			mperks_redeem_tab.click()

			while True:  # Find all reward elements, check for cash rewards that can be redeemed, and redeem
				all_rewards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.mperks-redeem-tile')))
				redeemable_rewards = []
				for reward in all_rewards:  # Check all rewards
					price_element = reward.find_element(By.CSS_SELECTOR, '[data-testid="ads-price"]')  # Get the price text
					price_text = price_element.text.strip()
					if "Save $" in price_text and "your total purchase" in reward.text:  # Only consider cash rewards
						price_value = int(price_text.replace("Save $", "").strip()) * 1000  # Get $ amount and convert to points
						button = reward.find_element(By.CSS_SELECTOR, '[data-testid="ads-button"]')  # Check if redeem is enabled
						if button.is_enabled() and mperks_points_num >= price_value:
							redeemable_rewards.append((reward, price_value))  # Store both the element and its cost

				if not redeemable_rewards:  # Checks if there are no redeemable rewards left
					print(f"No redeemable cash rewards for {myMperksEmail}.")
					log_file.write("No redeemable cash rewards.\n\n")
					break  # Exit the loop

				highest_reward, highest_cost = max(redeemable_rewards, key=lambda x: x[1])  # Sort and get highest reward
				redeem_button = highest_reward.find_element(By.CSS_SELECTOR, '[data-testid="ads-button"]')  # Button of highest cash reward
				redeem_button.click()
				confirm_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="ads-button" and contains(text(), "Confirm")]')))
				confirm_button.click()
				print(f"Redeemed reward for ${highest_cost // 1000} dollars.")
				log_file.write(f"Redeemed reward on {myMperksEmail} for ${highest_cost // 1000} dollars.\n")
				mperks_points_num -= highest_cost  # Update mperks_points_total
				driver.refresh()  # Refresh page to force reload of redeemable rewards. Otherwise takes some time on its own.

		except Exception as e:  # Issue checking the acount
			print(f"An error occurred redeeming points for {myMperksEmail}: {e}\n")
			log_file.write("An error occurred redeeming points on {myMperksEmail}\n")
		finally:
			if index == total_accounts - 1:
				print(f"Finished with {myMperksEmail}.\n")
				print("Done redeeming on selected accounts, returning to main menu. Check output.txt for the results.\n")
				log_file.write("\n\n")
			else:
				print(f"Finished with {myMperksEmail}. Waiting 15 seconds before checking the next account.\n")
				time.sleep(15)
			if driver:
				driver.quit()  # Ensures broswer gets closed
		log_file.close()

def coupon_clipper(credentials, selected_accounts):
	total_accounts = len(selected_accounts)
	while True:  # Defining search term for coupon
		print("\n1. Use the defult 'Gift Card' search\n2. Enter a custom coupon search\n")
		search_choice = input("Enter your choice: ")
		if search_choice == '1':
			search_term = 'Gift Card'
			break
		elif search_choice == '2':
			search_term = input("\nEnter your search term and press <ENTER>: ")
			break
		else:
			print("\nInvalid choice")
	print(f"\nSearching coupons for '{search_term}'\n")
	for index, account_index in enumerate(selected_accounts):  # Runs for all selected accounts
		date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		log_file = open("output.txt", "a")
		myMperksEmail, myMperksPassword = credentials[account_index]
		driver = None
		try:
			driver = initialize_driver()

			log_file.write(f"Trying to clip coupons for account {myMperksEmail} at {date_time} \n")

			# Load Meijer page, wait, inject cookie, reload page
			driver.get('https://www.meijer.com/shopping/mPerks.html')
			load_cookies(driver, myMperksEmail)
			driver.refresh()
			time.sleep(2)

			# Open the coupons tab
			coupons_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="ads-link" and text()="Coupons"]')))
			coupons_page.click()
			time.sleep(2)

			# Use the search box
			search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@class="search-filter__input search-filter__input--default"]')))
			search_box.clear()  # Removes pre-filled text
			search_box.send_keys(search_term)  # Fills search box with defined term
			search_box_search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="search-filter__submit"]')))
			search_box_search.click()  # Clicks button to search
			time.sleep(5)

			# Clip the coupon
			try:  # Finds all returned coupons for search_term
				coupon_tiles = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "coupon-tile__container")]')))
				print(f"\nFound {len(coupon_tiles)} coupon(s) for '{search_term}'.")
				log_file.write(f"Found {len(coupon_tiles)} coupon(s) for '{search_term}'\n")
				for tile in coupon_tiles:  # Checks each tile for clip or unclip
					clip_button = tile.find_element(By.XPATH, './/button[contains(@class, "coupon-tile__button--clip") or contains(@class, "coupon-tile__button--unclip")]')
					aria_label = clip_button.get_attribute('aria-label').strip()
					coupon_title = tile.find_element(By.CLASS_NAME, "coupon-tile__title-line-clamp-text").text.strip()
					coupon_desc = description = tile.find_element(By.CLASS_NAME, "coupon-tile__desc-line-clamp-text").text.strip()
					coupon_exp = expiration_date = tile.find_element(By.CLASS_NAME, "coupon-tile__date-line-clamp-wrapper").text.strip()
					clipped_coupon_text = f"{coupon_title} {coupon_desc}, valid thru {coupon_exp}"
					try:
						if 'Clip' in aria_label:  # Click if it contains "Clip"
							#coupon_title = tile.find_element(By.CLASS_NAME, "coupon-tile__title-line-clamp-text").text.strip()
							#coupon_desc = description = tile.find_element(By.CLASS_NAME, "coupon-tile__desc-line-clamp-text").text.strip()
							#coupon_exp = expiration_date = tile.find_element(By.CLASS_NAME, "coupon-tile__date-line-clamp-wrapper").text.strip()
							#clipped_coupon_text = f"{coupon_title} {coupon_desc}, valid thru {coupon_exp}"
							clip_button.click()
							print(f"Coupon clipped - {clipped_coupon_text}")
							log_file.write(f"Coupon clipped - {clipped_coupon_text}\n")
						else:  # If doesn't say clip, it's already clipped
							print(f"Coupon already clipped - {clipped_coupon_text}, checking next.")
							log_file.write(f"Coupon already clipped - {clipped_coupon_text}\n")
					except Exception as e:  # Error locating the clip/unclip buttons
						print('Error finding clip buttons: {e}')
				log_file.write(f"Done clipping available '{search_term}' coupons for {myMperksEmail}\n\n")
				coupons_were_found = True  # Don't need to check for "No results" below
			except:
				coupons_were_found = False  # Need to check for "No results" below
			if not coupons_were_found:
				try:  # Look for "No results"
					search_box_search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="back-to-all-coupons__btn" and text()="No Results"]')))
					print(f"No coupons found for '{search_term}'.")
					log_file.write(f"No coupons found for '{search_term}'.\n")
				except Exception as e:  # Error finding coupons
					print(f"Error finding coupon tiles buttons: {e}")
					log_file.write(f"An error occurred finding coupons on {myMperksEmail}\n")
		finally:
			if driver:
				driver.quit()  # Ensures broswer gets closed
			if index == total_accounts - 1:
				print(f"Finished with {myMperksEmail}.\n")
				print("Done clipping coupons on selected accounts, returning to main menu. Check output.txt for the results.\n")
				log_file.write("\n\n")
				log_file.close()  # Closes log file
			else:
				print(f"Finished with {myMperksEmail}. Waiting 15 seconds before checking the next account.\n")
				log_file.close()  # Closes log file
				time.sleep(15)
			if log_file is open:
				log_file.close()  # Ensures log file gets closed

def main():
	credentials = read_credentials("credentials.txt")
	while True:
		print("\n1. Get login cookies (required for 2,3, and 4)\n2. Check account stats (points, unused rewards, unclaimed \
earn tasks)\n3. Redeem points (will redeem ALL points on the account)\n4. Coupon clipper\n5. All of the above\n8. Instructions\n9. Quit\n")
		choice = input("Enter your choice: ")
		if choice == '1':
			selected_accounts = get_account_selection(credentials)
			get_cookies(credentials, selected_accounts)
		elif choice == '2':
			selected_accounts = get_account_selection(credentials)
			check_account_status(credentials, selected_accounts)
		elif choice == '3':
			print("\nThis will redeem all points on the account for $X off your next shopping trip, starting with the largest available to redeem")
			print("Example, if you have 75k points, it will redeem $50, $20, and $5")
			print("It will redeem for the highest reward as long as you have points until you have none left")
			are_you_sure = input("\nPress <ENTER> to continue, press 'q' to return to the main menu: ")
			if are_you_sure == 'q':
				print("\nQuitting redeemer now...")
			else:
				selected_accounts = get_account_selection(credentials)
				redeem_points(credentials, selected_accounts)
		elif choice == '4':
			selected_accounts = get_account_selection(credentials)
			coupon_clipper(credentials, selected_accounts)
		elif choice == '5':
			print("\n1. Use all accounts for all steps\n2. Specify select accounts at each step\n")
			all_or_some = input("Enter your choice: ")
			if all_or_some == '1':
				selected_accounts = list(range(len(credentials)))
			elif all_or_some == '2':
				selected_accounts = get_account_selection(credentials)
			get_cookies(credentials, selected_accounts)
			coupon_clipper(credentials, selected_accounts)
			redeem_points(credentials, selected_accounts)
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
			break
		else:
			print("Invalid choice, please enter 1, 2, 8, or 9.")

if __name__ == "__main__":
    main()
