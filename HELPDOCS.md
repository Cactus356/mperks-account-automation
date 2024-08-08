## How to use:
Requires undetected_chromedriver - ```pip install undetected-chromedriver```  
Requires Selenium - ```pip install selenium```  

Fill credentials.txt with your mPerks account logins in the form of ```email,password```, one per line. Run get_cookies.py and follow any console prompts that pop up. Refer to troubleshooting below if more info is needed. Run account_checker.py, again follow any console propmts that show up. Most issues happen running get_cookies.py, so you should be fine if you made it here

## Troubleshooting:
Start by uncommenting "logging.basicConfig(level=10)" at the top of the script - This will print full logs to the console. Pay attention to where it breaks - Is it not finding an element or something else?See if you can fix what it's asking for. Otherwise open an issue and include the last chunk of console output and I'll see what I can do.  

### Credentials.txt
Can have blank lines and commented out lines. Keep the format ```email,password``` - No space after the comma. The password can have some special characters, but I'd probably avoid spaces, commas, and quotes, both single and double. Basically !@#$%^&* should be fine. This isn't tested per se, but if something isn't working while logging in, I'd check here. An example credentials.txt has been provided.  

Logins can be commented out for both get_cookies and account_checker.
You can mix and match - So if there's 8 logins, you can run 1,2,3,4 through get_cookies, edit the credentials.txt, then run 5,6,7,8 through account_checker, provided they already had cookies saved in cookies.txt If an account fails, it should run though the rest of the logins provided. When finished, leaved the failed one uncommented and run it again to try just that failed one.

### Cookies.txt
Does not need to be created, get_cookies will create it if it doesn't exist. One cookie per line, should be in the form of ```email,[lots of text here]```  

cookies.txt doesn't like blank lines, and unless you touch anything manually, get_cookies should just format it properly. You shouldn't need to comment anything out in cookies.txt - Cookies are only read when it's corresponding email is called. Basically just don't touch this unless you're deleting an entire line.

### mPerks "unexpected internal error"
I ran into this quite often while testing, must be some sort of rate limiting. Although when I purposefully tried to trigger it by spamming logins, I coulnd't, so who knows. Basically after the email is entered and submitted, instead of the password page, you'll get an error page. The script _should_ detect this and pause itself - You just need to manually fix the login:  
- A refresh of the page usually brings you back to the email entry - Manually enter the email and continue. Hopefully you're on password entry now.
- If it still errors, again refresh and go back to the email entry. Select unlock account and enter the email. They'll send you an email, in my case they alays said my account wasn't locked and I was good to log in.
- Go back to the email entry and manually enter it again. Hopefully you're now on the password entry.
Basically just refresh / go back / unlock / whatever manually until you get to password entry. Once on password entry, press any key while in the console window and the script will enter the password and continue with the rest.

### mPerks 2FA:
Every account I tested on a new device and/or IP would trigger a 2FA check in the form of an email or phone code. The script should detect that it's asking for 2FA and pause itself. You need to manually complete the 2FA requirements. Select send email or text, submit the code, and you should move forward to the password screen. Once on password entry, press any key while in the console window and the script will enter the password and continue with the rest.
