
# Meijer mPerks Account Automation
Uses given credentials to check your mPerks account(s) and log coupons, points, and available gift card offers

## What does this do?
It will log into your mPerks account and log the following: Total mPerks points, unused rewards and expiration date (Like save $5 on your next purchase), and any gift card promos that are available on your account (Like earn 5,000 points for every $50 spend on select gift cards)

Here is an example output.txt:
```
Account: email1@website.com
Unused reward found: Save $1 on your total purchase. Valid thru 9/13/24.
Unused reward found: Save $20 on your total purchase. Valid thru 9/13/24.
Total mPerks points: 7368
Current GC promo: No promo found

Account: email2@website.com
Unused reward found: Save $20 on your total purchase. Valid thru 9/12/24.
Unused reward found: Save $20 on your total purchase. Valid thru 9/12/24.
Total mPerks points: 1819
Current GC promo: No promo found

Account: email3@website.com
There are no rewards waiting to be used
Total mPerks points: 0
Current GC promo: Earn 7,500 points for every $50 you spend on select Gift Cards. Through 8/10/24.

Account: email4@website.com
Unused reward found: Save $15 on your total purchase. Valid thru 9/14/24.
Total mPerks points: 102
Current GC promo: Earn 7,500 points for every $50 you spend on select Gift Cards. Through 8/10/24.
```

## How does it work?
You need the undetected_chromedriver installed - https://github.com/ultrafunkamsterdam/undetected-chromedriver <br />
And Selenium - https://www.selenium.dev/documentation/webdriver/getting_started/
```
pip install undetected-chromedriver
pip install selenium
```

Fill credentials.txt with your logins. Run get_cookies.py. Run account_checker.py. Read output.log.

This reads the logins from the credentials file, logs into mPerks, and saves each accounts cookie into cookies.txt. Why do it this way? Getting logged in was the hardest part of all this for me. New devices/IPs will prompt for 2FA, and you can also get rate limited (At least rate limiting is my best guess) and they'll throw errors at you while logging in. I decided to spearate the more complicated login process to produce a cookie file that could then be used to reliably and repeatedly log into the accounts to get the information described above. Basically you just have to push through whatever mPerks throws at you for all your accounts the one time to get the cookies, then the actual checking should run without fail as long as the cookies are still valid.

## What's the point of this?
Some users have multiple mPerks accounts to take advantage of promo offers more than once, often to farm credit card points. Keeping track of what accounts have used gift card offers, how many points they have, and if the points have been redeemed for coupons can get confusing. Instead of manually checking everything on all accounts, this will just do it for you and print a report of everything at the end.

## Disclaimers
- This is not for malicious use and/or account cracking. It has to be given an email and password. It will not try multiple passwords, at least not in a remotely fast way. The first time you run it, each account will ask for a 2FA code from the registered email or phone. 
- This is probably against the mPerks TOS in some way, so this is for hypothetical and testing purposes only. 
- I am not a python developer. I can use Google, ChatGPT, and a lot of free time on the weekends. Between all of that, I can toss some suff together. Yes, I'm sure this code could be better. Yes, I'm sure there's issues. Report them or fix them yourself.
