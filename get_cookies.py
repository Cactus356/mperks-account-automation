# v1.0 8/7/2024
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
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

def save_cookies(driver, email):
    cookies = driver.get_cookies()
    with open("cookies.txt", "a") as file:
        file.write(f"{email},{str(cookies)}\n")

# Read credentials
credentials = read_credentials("credentials.txt")
total_accounts = len(credentials)  # Used to calculate how many loops to run and print the final message

for index, (myMperksEmail, myMperksPassword) in enumerate(credentials):  # Runs for every login in credentials.txt
	driver = None  # Initial driver state
	try:
		options = Options()
		options.add_argument('--disable-popup-blocking')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		#options.add_argument('--headless')  # Can probably turned on after running all accounts once and 2FA won't trigger
		#options.add_argument('--disable-gpu')  # Can probably turned on after running all accounts once and 2FA won't trigger
		options.add_argument("--disk-cache-size=300000000")  # limiting the cache storage to 300 MB
		options.add_argument("--incognito")

		driver = uc.Chrome(options=options)  #, browser_executable_path="/usr/bin/chromium-browser", driver_executable_path="/tmp/chromedriver")

		# Load Meijer page and click top right sign in
		print(f"Logging into {myMperksEmail}, please wait... ")
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

		try: # Waits 5 seconds to detect mPerks login error (Rate limiting? Exact cause unknown.)
			WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "unexpected internal error")]')))
			print("Detected mPerks error after entering email. Refer to help docs for more info.")
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

		# Checks to make sure points total loaded. If they didn't, login failed. This will throw an exceptiond.
		print("Making sure the account is logged in, please wait...")
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="user-info__points"]')))
		save_cookies(driver, myMperksEmail)  # Save cookies after successful login
		driver.quit()  # Close browser
		print(f"Your cookie has been saved for {myMperksEmail}\n")

	except Exception as e:  # Issue checking the acount. Prints error to console.
		print(f"An error occurred for {myMperksEmail}: {e}\n")

	finally:
		if driver:
			driver.quit()  # Ensures broswer gets closed
		if index == total_accounts - 1:
			print("Done processing all accounts. Cookies.txt should have an entry for every accoint in credentials.txt.\n")
		else:
			print("Waiting 20 seconds before logging into the next account.\n")
			time.sleep(20)
