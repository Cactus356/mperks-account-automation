# Changelog  

## v2.0 (8/11/24)
- Combines get_cookies and account_checker into one script
- Menu prompts for module selection, including get cookies, account checking, and instructions
- Account selection for both modules can now be done in the console instead of having to edit the credentials.txt file to exclude accounts
- Cookies.txt will now overwrite the existing cookie for each selected account to avoid writing duplicates

## v1.0 (8/7/24)
- Initial release
- Uses get_cookies.py to log into all accounts and save cookies into a text file
- Uses account_checker.py to quickly re-log into all accounts, reporting total mPerks points, unused coupons, and unclaimed rewards
- Store accounts in credentials.txt
