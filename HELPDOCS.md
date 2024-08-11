## How to use:
Requires undetected_chromedriver - ```pip install undetected-chromedriver```  
Requires Selenium - ```pip install selenium```  

Fill credentials.txt with your mPerks account logins in the form of ```email,password```, one per line. Run main.py and follow any console prompts that pop up. Start by getting cookies for your accounts. Then you can run the checker and again, follow any console propmts that show up. Refer to troubleshooting below if more info is needed - Most issues happen during getting cookies, so you should be fine if you made it past that.

## Troubleshooting:
Start by uncommenting "logging.basicConfig(level=10)" at the top of the script - This will print full logs to the console. Pay attention to where it breaks - Is it not finding an element or something else?See if you can fix what it's asking for. Otherwise open an issue and include the last chunk of console output and I'll see what I can do.  

### Credentials.txt
Can have blank lines and commented out lines. Keep the format ```email,password``` - No space after the comma. The password can have some special characters, but I'd probably avoid spaces, commas, and quotes, both single and double. Basically !@#$%^&* should be fine. This isn't tested per se, but if something isn't working while logging in, I'd check here. An example credentials.txt has been provided.  

Logins can be commented out so they aren't imported.
Alternatively, you can keep all accounts enabled in the credentials file, but then use the option within the script to specify all or specific accounts. This prevents having to always edit the credentials file, or forgetting you had one disabled or something.

### Cookies.txt
Does not need to be created, script will create it if it doesn't exist.

One cookie per line, should be in the form of ```email,[lots of text here]```  

Getting cookies will overwrite the existing cookie for the specified account. so you don't need to delete cookies.txt or individual entries. Example, if you have 8 accounts and cookies for all 8, but run the cookie grabber and only select accounts 3 and 7, only 3 and 7 will be updated in cookies,txt, the rest will remain unchanged.

cookies.txt doesn't like blank lines, and unless you touch anything manually, the script should just format it properly. You shouldn't need to comment anything out in cookies.txt - Cookies are only read when it's corresponding email is called. Basically just don't touch this unless you're deleting an entire line.

### mPerks "unexpected internal error"
I ran into this quite often while testing, must be some sort of rate limiting. Although when I purposefully tried to trigger it by spamming logins, I coulnd't, so who knows. Basically after the email is entered and submitted, instead of the password page, you'll get an error page with a red box and some message. The script _should_ detect this and pause itself - You just need to manually fix the login:  
- A refresh of the page usually brings you back to the email entry - Manually enter the email and continue. Hopefully you're on password entry now.
- If it still errors, again refresh and go back to the email entry. Select unlock account and enter the email. They'll send you an email, in my case they alays said my account wasn't locked and I was good to log in.
- Go back to the email entry and manually enter it again. Hopefully you're now on the password entry.
Basically just refresh / go back / unlock / whatever manually until you get to password entry. Once on password entry, press any key while in the console window to continue the script as normal.

### mPerks 2FA:
Every account I tested on a new device and/or IP would trigger a 2FA check in the form of an email or phone code. The script should detect that it's asking for 2FA and pause itself. You need to manually complete the 2FA requirements. Select send email or text, submit the code, and you should move forward to the password screen. Once on password entry, press any key while in the console window to continue the script as normal.
