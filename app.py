from flask import Flask, request, render_template_string, redirect, url_for, session
import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

# --- Environment Variables ---
# تمامی این متغیرها باید در محیط (مثلاً Render) تنظیم شوند.
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
# BOT_USERNAME ممکن است به عنوان نام کاربری سروری استفاده شود (برای ورود به حساب)
BOT_USERNAME = os.environ["BOT_USERNAME"]  # بدون @ (مثلاً se36We)
LICENSE_KEY = os.environ["LICENSE_KEY"]
# متغیر جدید برای مقصد پیام
DESTINATION_USERNAME = os.environ["DESTINATION_USERNAME"]  # بدون @ (مثلاً destinationUser)

# SECRET_KEY: برای سشن Flask؛ در تولید بهتر است مقدار امن تنظیم شود.
app.secret_key = os.environ.get("SECRET_KEY", "b4d9fbe7c38e2df1e4d1a0a61b2f8073")

# -------------------- HTML Templates --------------------

# صفحه ورود لایسنس
LICENSE_FORM_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>License Verification</title>
  <style>
    body {
      background: linear-gradient(135deg, #74ABE2 0%, #5563DE 100%);
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #333;
    }
    .container {
      background: #fff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.2);
      text-align: center;
      max-width: 420px;
      width: 90%;
      animation: fadeIn 1s ease-in-out;
    }
    h2 {
      margin-bottom: 20px;
    }
    input[type="text"] {
      width: 80%;
      padding: 12px;
      margin: 10px 0;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 16px;
      outline: none;
    }
    button {
      padding: 12px 24px;
      background-color: #FF6B6B;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      margin-top: 10px;
    }
    button:hover {
      background-color: #e85f5f;
    }
    .error {
      color: #ff0000;
      font-weight: bold;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Enter Your License Key</h2>
    {% if error %}
      <p class="error">{{ error }}</p>
    {% endif %}
    <form method="POST">
      <input type="text" name="license" placeholder="License Key" required>
      <br>
      <button type="submit">Verify</button>
    </form>
  </div>
</body>
</html>
'''

# پروگرس‌بار اول (20 ثانیه)
PROGRESS_HTML_1 = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Processing License</title>
  <style>
    body {
      background: linear-gradient(135deg, #ffafbd 0%, #ffc3a0 100%);
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #333;
    }
    .container {
      background: #fff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.2);
      text-align: center;
      max-width: 420px;
      width: 90%;
      animation: fadeIn 0.8s ease-in-out;
    }
    h2 {
      margin-bottom: 20px;
    }
    #progressBar {
      width: 100%;
      background-color: #ddd;
      border-radius: 6px;
      overflow: hidden;
      margin-top: 20px;
      height: 24px;
    }
    #progressBar div {
      height: 24px;
      width: 0%;
      background: linear-gradient(90deg, #42e695 0%, #3bb2b8 100%);
      border-radius: 6px;
    }
    #countdown {
      font-size: 18px;
      margin-top: 15px;
      font-weight: bold;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Please wait while we verify your license...</h2>
    <div id="progressBar"><div></div></div>
    <p id="countdown">20</p>
  </div>
  <script>
    let width = 0;
    let countdown = 20;
    const interval = setInterval(() => {
      width += 5;
      countdown -= 1;
      document.getElementById("progressBar").children[0].style.width = width + "%";
      document.getElementById("countdown").textContent = countdown;
      if (width >= 100) {
        clearInterval(interval);
        window.location.href = "{{ next_url }}";
      }
    }, 1000);
  </script>
</body>
</html>
'''

# صفحه انتخاب نرم‌افزار
CHOOSE_SOFTWARE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Choose Your Software</title>
  <style>
    body {
      background: linear-gradient(to right, #8360c3, #2ebf91);
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #333;
    }
    .container {
      background: #fff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.2);
      text-align: center;
      max-width: 420px;
      width: 90%;
      animation: fadeIn 0.8s ease-in-out;
    }
    h2 {
      margin-bottom: 20px;
    }
    button {
      padding: 12px 24px;
      background-color: #FF6B6B;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      margin: 10px;
    }
    button:hover {
      background-color: #e85f5f;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Please choose the software you want:</h2>
    <form method="POST">
      <button type="submit" name="software" value="EagleSpy-V5">EagleSpy-V5</button>
      <button type="submit" name="software" value="CraxsRat-7.6">CraxsRat-7.6</button>
    </form>
  </div>
</body>
</html>
'''

# پروگرس‌بار دوم (20 ثانیه)
PROGRESS_HTML_2 = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Finalizing Request</title>
  <style>
    body {
      background: linear-gradient(to right, #ff9966, #ff5e62);
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #333;
    }
    .container {
      background: #fff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.2);
      text-align: center;
      max-width: 420px;
      width: 90%;
      animation: fadeIn 0.8s ease-in-out;
    }
    h2 {
      margin-bottom: 20px;
    }
    #progressBar {
      width: 100%;
      background-color: #ddd;
      border-radius: 6px;
      overflow: hidden;
      margin-top: 20px;
      height: 24px;
    }
    #progressBar div {
      height: 24px;
      width: 0%;
      background: linear-gradient(90deg, #42e695 0%, #3bb2b8 100%);
      border-radius: 6px;
    }
    #countdown {
      font-size: 18px;
      margin-top: 15px;
      font-weight: bold;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Please wait while we finalize your request...</h2>
    <div id="progressBar"><div></div></div>
    <p id="countdown">20</p>
  </div>
  <script>
    let width = 0;
    let countdown = 20;
    const interval = setInterval(() => {
      width += 5;
      countdown -= 1;
      document.getElementById("progressBar").children[0].style.width = width + "%";
      document.getElementById("countdown").textContent = countdown;
      if (width >= 100) {
        clearInterval(interval);
        window.location.href = "{{ send_url }}";
      }
    }, 1000);
  </script>
</body>
</html>
'''

# صفحه نهایی پس از ارسال پیام
FINAL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Process Completed</title>
  <style>
    body {
      background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      color: #333;
    }
    .container {
      background: #fff;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.2);
      text-align: center;
      max-width: 500px;
      width: 90%;
      animation: fadeIn 1s ease-in-out;
    }
    h2 {
      margin-bottom: 20px;
    }
    p {
      font-size: 18px;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Process Completed Automatically!</h2>
    <p>Your request has been processed and messages have been sent to the destination.</p>
  </div>
</body>
</html>
'''

# -------------------- Telethon Function --------------------
async def send_telegram_messages(software_choice):
    """
    با توجه به انتخاب نرم‌افزار، پیام‌های مناسب را به مقصد ارسال می‌کند.
    پیام‌ها از حساب سروری (با SESSION_STRING) ارسال می‌شوند.
    مقصد پیام از متغیر DESTINATION_USERNAME تعیین می‌شود.
    """
    async with TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH) as client:
        if software_choice == "EagleSpy-V5":
            message_text = "Get EagleSpy-V5 link"
            link = "https://t.me/c/2344120391/214/233"
        else:
            message_text = "Get CraxsRat-7.6 link"
            link = "https://t.me/c/2267427894/620"
        # ارسال پیام اول
        await client.send_message(DESTINATION_USERNAME, message_text)
        # ارسال پیام دوم (لینک)
        await client.send_message(DESTINATION_USERNAME, link)

# -------------------- Routes --------------------

@app.route("/", methods=["GET", "POST"])
def license_page():
    """
    صفحهٔ اصلی برای وارد کردن لایسنس.
    """
    if request.method == "POST":
        provided_license = request.form.get("license", "")
        if provided_license == LICENSE_KEY:
            session["license_ok"] = True
            return redirect(url_for("progress1"))
        else:
            error_msg = "Incorrect license key. Please enter the correct license key."
            return render_template_string(LICENSE_FORM_HTML, error=error_msg)
    return render_template_string(LICENSE_FORM_HTML, error=None)

@app.route("/progress1")
def progress1():
    """
    پروگرس‌بار اول (۲۰ ثانیه)؛ بعد از اتمام به صفحه انتخاب نرم‌افزار هدایت می‌شود.
    """
    if not session.get("license_ok"):
        return redirect(url_for("license_page"))
    return render_template_string(PROGRESS_HTML_1, next_url=url_for("choose_software"))

@app.route("/choose_software", methods=["GET", "POST"])
def choose_software():
    """
    صفحه انتخاب نرم‌افزار: EagleSpy-V5 یا CraxsRat-7.6.
    """
    if not session.get("license_ok"):
        return redirect(url_for("license_page"))
    if request.method == "POST":
        software_choice = request.form.get("software", "")
        session["software_choice"] = software_choice
        return redirect(url_for("progress2"))
    return render_template_string(CHOOSE_SOFTWARE_HTML)

@app.route("/progress2")
def progress2():
    """
    پروگرس‌بار دوم (۲۰ ثانیه)؛ پس از اتمام، کاربر به endpoint ارسال پیام‌ها هدایت می‌شود.
    """
    if not session.get("license_ok"):
        return redirect(url_for("license_page"))
    software_choice = session.get("software_choice")
    if not software_choice:
        return redirect(url_for("choose_software"))
    return render_template_string(PROGRESS_HTML_2, send_url=url_for("send_messages"))

@app.route("/send_messages")
def send_messages():
    """
    endpoint برای ارسال پیام‌ها به مقصد از طریق Telethon و سپس هدایت به صفحه نهایی.
    """
    if not session.get("license_ok"):
        return redirect(url_for("license_page"))
    software_choice = session.get("software_choice")
    if not software_choice:
        return redirect(url_for("choose_software"))
    asyncio.run(send_telegram_messages(software_choice))
    return redirect(url_for("final"))

@app.route("/final")
def final():
    """
    صفحه نهایی که نشان می‌دهد روند به‌طور خودکار تکمیل شده است.
    """
    return render_template_string(FINAL_HTML)

# -------------------- Main --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
