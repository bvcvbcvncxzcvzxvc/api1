from flask import Flask, request, render_template_string, redirect, url_for, flash, send_file
import os
import time
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")  # لازم برای flash messages

# --- Environment Variables ---
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_USERNAME = os.environ["BOT_USERNAME"]
LICENSE_KEY = os.environ["LICENSE_KEY"]
SESSION_STRING = os.environ["SESSION_STRING"]

# --- Telethon Client ---
def send_message_via_telethon():
    """
    Sends a message "License ****" (or your LICENSE_KEY) to the specified BOT_USERNAME via Telethon.
    """
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    client.start()

    async def main():
        await client.send_message(BOT_USERNAME, f"License {LICENSE_KEY}")
        print("Message sent to Telegram bot.")

    client.loop.run_until_complete(main())

# --- Create Log File ---
def create_log_file():
    """
    Creates a log file with the required content in the script directory.
    """
    content = f"License {LICENSE_KEY}\nCode55888\nSarP5988888\n"
    with open("license_log.txt", "w") as f:
        f.write(content)
    print("Log file generated successfully.")

# --- HTML Templates ---
LICENSE_FORM_HTML = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>License Verification</title>
  </head>
  <body>
    <h2>Please enter your license key</h2>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul style="color:red;">
          {% for message in messages %}
            <li>{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method="POST">
      <input type="text" name="license" placeholder="License Key" required>
      <button type="submit">Submit</button>
    </form>
  </body>
</html>
'''

VERIFIED_HTML = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>License Verified</title>
  </head>
  <body>
    <h2>Your license is verified!</h2>
    <p>Telegram Desktop must be installed on your system. Click the button below to open Telegram Desktop or Portable and automatically open chat with @{{ bot_username }}.</p>
    <p>
      <a href="tg://resolve?domain={{ bot_username }}&text=License%20{{ license_key }}">
        <button type="button">Open Telegram</button>
      </a>
    </p>
    <p>A log file has been created on the server. You can download it here:</p>
    <p>
      <a href="{{ url_for('download_log') }}">
        <button type="button">Download Log</button>
      </a>
    </p>
  </body>
</html>
'''

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        provided_license = request.form.get("license")
        if provided_license != LICENSE_KEY:
            flash("Incorrect license key. Please try again.")
            return render_template_string(LICENSE_FORM_HTML)
        else:
            # If license is correct:
            send_message_via_telethon()
            create_log_file()
            return render_template_string(
                VERIFIED_HTML,
                bot_username=BOT_USERNAME.replace("@", ""),  # remove @ for the deep link
                license_key=LICENSE_KEY
            )
    return render_template_string(LICENSE_FORM_HTML)

@app.route("/download-log")
def download_log():
    """
    Sends the license_log.txt file to the user for download.
    """
    log_file_path = "license_log.txt"
    if not os.path.exists(log_file_path):
        return "Log file not found.", 404
    return send_file(log_file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
