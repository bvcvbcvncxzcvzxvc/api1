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

def verify_license(provided_license):
    """
    Non-interactive license verification.
    Compare the provided license with the LICENSE_KEY environment variable.
    """
    if provided_license == LICENSE_KEY:
        print('License verified successfully.')
        return True
    else:
        print('Invalid license key.')
        return False

def send_message_to_telegram():
    # Use the session string for authentication
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
    # In a non-interactive environment, you should get the license key from another source.
    # For demonstration, we assume the provided license is the same as the environment variable.
    provided_license = LICENSE_KEY  # Replace this with the actual license input in a web request if needed.

    if verify_license(provided_license):
        send_message_to_telegram()
        time.sleep(5)  # Waiting for a response from the Telegram bot
        save_log()

if __name__ == '__main__':
    main()
