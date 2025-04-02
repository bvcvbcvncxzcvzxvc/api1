from flask import Flask, request, render_template_string, flash, send_file, url_for
import os

app = Flask(__name__)
# If SECRET_KEY is not provided in the environment, use the following default value.
# Note: In production, it's strongly recommended to set your own SECRET_KEY.
app.secret_key = os.environ.get("SECRET_KEY", "b4d9fbe7c38e2df1e4d1a0a61b2f8073")

# --- Environment Variables (no defaults for sensitive info) ---
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
BOT_USERNAME = os.environ["BOT_USERNAME"]  # Expected without the '@' in deep link
LICENSE_KEY = os.environ["LICENSE_KEY"]

# --- HTML Templates with Professional Style ---
LICENSE_FORM_HTML = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>License Verification</title>
    <style>
      body {
        background-color: #f7f7f7;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
      }
      .container {
        background: #fff;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        text-align: center;
        max-width: 400px;
        width: 100%;
      }
      input[type="text"] {
        width: 80%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 16px;
      }
      button {
        padding: 10px 20px;
        background-color: #007bff;
        color: #fff;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
      }
      button:hover {
        background-color: #0056b3;
      }
      .error {
        color: #ff0000;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Please enter your license key</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <ul class="error">
            {% for message in messages %}
              <li>{{ message }}</li>
            {% endfor %}
          </ul>
        {% endif %}
      {% endwith %}
      <form method="POST">
        <input type="text" name="license" placeholder="License Key" required>
        <br>
        <button type="submit">Submit</button>
      </form>
    </div>
  </body>
</html>
'''

VERIFIED_HTML = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>License Confirmed</title>
    <style>
      body {
        background-color: #f7f7f7;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
      }
      .container {
        background: #fff;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        text-align: center;
        max-width: 500px;
        width: 100%;
      }
      button {
        padding: 10px 20px;
        background-color: #28a745;
        color: #fff;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
      }
      button:hover {
        background-color: #218838;
      }
      a {
        text-decoration: none;
      }
      .action-btn {
        margin: 10px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>Your license is confirmed!</h2>
      <p>
        To complete the process, your Telegram Desktop/Portable must be installed.
        Click the button below to open Telegram. It will automatically open a chat with
        <strong>@{{ bot_username }}</strong> with the pre-filled message <strong>"License {{ license_key }}"</strong>.
      </p>
      <p>
        <a href="tg://resolve?domain={{ bot_username }}&text=License%20{{ license_key }}" class="action-btn">
          <button type="button">Open Telegram</button>
        </a>
      </p>
      <p>
        A log file has been generated on the server. Click below to download it:
      </p>
      <p>
        <a href="{{ url_for('download_log') }}" class="action-btn">
          <button type="button">Download Log</button>
        </a>
      </p>
    </div>
  </body>
</html>
'''

# --- Create Log File Function ---
def create_log_file():
    """
    Creates a log file with the required content.
    """
    log_content = f"License {LICENSE_KEY}\nCode55888\nSarP5988888\n"
    with open("license_log.txt", "w") as f:
        f.write(log_content)
    print("Log file generated successfully.")

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        provided_license = request.form.get("license")
        if provided_license != LICENSE_KEY:
            flash("Incorrect license key. Please enter the correct license key.")
            return render_template_string(LICENSE_FORM_HTML)
        else:
            create_log_file()
            return render_template_string(
                VERIFIED_HTML,
                bot_username=BOT_USERNAME,
                license_key=LICENSE_KEY
            )
    return render_template_string(LICENSE_FORM_HTML)

@app.route("/download-log")
def download_log():
    """
    Sends the generated log file to the user for download.
    """
    log_file_path = "license_log.txt"
    if not os.path.exists(log_file_path):
        return "Log file not found.", 404
    return send_file(log_file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
