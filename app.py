import os
import subprocess
import time
from telethon import TelegramClient, events


# Environment Variables
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_USERNAME = os.getenv('BOT_USERNAME', '@se36We')
LICENSE_KEY = os.getenv('LICENSE_KEY', '123')
SESSION_STRING = os.getenv('SESSION_STRING')


def check_telegram_installed():
    try:
        subprocess.run(['telegram-desktop', '-version'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def verify_license():
    while True:
        license_input = input('Please enter your license key: ')
        if license_input == LICENSE_KEY:
            print('License verified successfully.')
            return True
        else:
            print('Invalid license key. Please try again.')


def send_message_to_telegram():
    client = TelegramClient('session_name', API_ID, API_HASH)
    client.start()

    async def main():
        await client.send_message(BOT_USERNAME, f'License {LICENSE_KEY}')
        print('Message sent to Telegram.')

    client.loop.run_until_complete(main())


def save_log():
    with open('license_log.txt', 'w') as file:
        file.write(f'License: {LICENSE_KEY}\n')
        file.write(f'Code: 55888\n')
        file.write(f'Serial: 5988888\n')
    print('Log file generated successfully.')


def main():
    if not check_telegram_installed():
        print('Telegram Desktop is not installed. Please install it and try again.')
        return

    if verify_license():
        send_message_to_telegram()
        time.sleep(5)  # Waiting for a response from the Telegram bot
        save_log()


if __name__ == '__main__':
    main()
