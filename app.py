from flask import Flask, request, render_template_string, redirect, url_for, session
from pyrogram import Client, filters
import os

app = Flask(__name__)

# --- Environment Variables ---
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']
BOT_USERNAME = os.environ['BOT_USERNAME']  # e.g., se36We
LICENSE_KEY = os.environ['LICENSE_KEY']

# Creating a Pyrogram client (without async)
client = Client("bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
client.start()

app.secret_key = os.environ.get('SECRET_KEY', 'b4d9fbe7c38e2df1e4d1a0a61b2f8073')

@app.route('/', methods=['GET', 'POST'])
def license_page():
    if request.method == 'POST':
        provided_license = request.form.get('license', '')
        if provided_license == LICENSE_KEY:
            session['license_ok'] = True
            return redirect(url_for('choose_software'))
        else:
            return 'Invalid License Key'
    return '<form method="POST"><input name="license"><button type="submit">Submit</button></form>'

@app.route('/choose_software', methods=['GET', 'POST'])
def choose_software():
    if 'license_ok' not in session:
        return redirect(url_for('license_page'))
    if request.method == 'POST':
        software = request.form.get('software')
        session['software'] = software
        return redirect(url_for('send_message'))
    return '<form method="POST"><button name="software" value="EagleSpy-V5">EagleSpy-V5</button><button name="software" value="CraxsRat-7.6">CraxsRat-7.6</button></form>'

@app.route('/send_message')
def send_message():
    if 'software' not in session:
        return redirect(url_for('choose_software'))

    software = session['software']
    message_text = f'Get {software} link'

    # Sending message without async
    client.send_message(BOT_USERNAME, message_text)

    return redirect(url_for('final'))

@app.route('/final')
def final():
    return 'Message sent successfully!'

@client.on_message(filters.private & filters.text)
def reply_to_user(client, message):
    if 'Get EagleSpy-V5 link' in message.text:
        message.reply_text('Download link for EagleSpy-V5: [Your link here]')
    elif 'Get CraxsRat-7.6 link' in message.text:
        message.reply_text('Download link for CraxsRat-7.6: [Your link here]')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
