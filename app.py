import os
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Retrieve environment variables
try:
    API_ID = int(os.environ['API_ID'])
except KeyError:
    raise KeyError("The API_ID environment variable is not set.")

API_HASH = os.environ.get('API_HASH')
BOT_USERNAME = os.environ.get('BOT_USERNAME')
LICENSE_KEY = os.environ.get('LICENSE_KEY')
SESSION_STRING = os.environ.get('SESSION_STRING')

# Check if essential environment variables are set
if not all([API_HASH, BOT_USERNAME, LICENSE_KEY, SESSION_STRING]):
    raise ValueError("One or more required environment variables (API_HASH, BOT_USERNAME, LICENSE_KEY, SESSION_STRING) are missing.")

def verify_license():
    while True:
        license_input = input('Please enter your license key: ')
        if license_input == LICENSE_KEY:
            print('License verified successfully.')
            return True
        else:
            print('Invalid license key. Please try again.')

def send_message_to_telegram():
    # Use the session string
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    client.start()

    async def main():
        await client.send_message(BOT_USERNAME, f'License {LICENSE_KEY}')
        print('Message sent to Telegram.')

    client.loop.run_until_complete(main())

def save_log():
    with open('license_log.txt', 'w') as file:
        file.write(f'License: {LICENSE_KEY}\n')
        file.write('Code: 55888\n')
        file.write('Serial: 5988888\n')
    print('Log file generated successfully.')

def main():
    # We don't need to check telegram-desktop installation in a server environment
    if verify_license():
        send_message_to_telegram()
        time.sleep(5)  # Waiting for a response from the Telegram bot
        save_log()

if __name__ == '__main__':
    main()
