import os
import json
import gspread
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials
import requests

app = Flask(__name__)

# --- Google Sheets Setup (Using Environment Variables) ---
# रेंडर में आपने जिस नाम से Variable बनाया है (जैसे: GOOGLE_CREDS), उसका इस्तेमाल करें
creds_json = os.environ.get('GOOGLE_CREDS') 

if creds_json:
    # अगर Key मिल गई, तो उसे JSON में बदलें
    info = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    client = gspread.authorize(creds)
else:
    # अगर रेंडर में वेरिएबल नहीं मिला, तो एरर न आए इसके लिए (Debug)
    print("Error: GOOGLE_CREDS environment variable not found!")

# अपनी शीट के नाम
sheet = client.open("Villas_Data").sheet1 
enquiry_sheet = client.open("Villas_Data").get_worksheet(1)

# --- Telegram Config ---
TELEGRAM_TOKEN = "7913354522:AAH1XxMP1EMWC59fpZezM8zunZrWQcAqH18"
TELEGRAM_CHAT_ID = "6746178673"

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- Routes ---

@app.route('/')
def index():
    villas = sheet.get_all_records()
    return render_template('index.html', villas=villas)

@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    villas = sheet.get_all_records()
    villa = next((v for v in villas if str(v['Villa_ID']) == str(villa_id)), None)
    if villa:
        return render_template('villa_details.html', villa=villa)
    return "Villa not found", 404

@app.route('/enquiry/<villa_id>', methods=['GET', 'POST'])
def enquiry(villa_id):
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        guests = request.form.get('guests')

        # शीट में सेव करना
        enquiry_sheet.append_row([villa_id, name, phone, checkin, checkout, guests])

        # टेलीग्राम अलर्ट
        alert_msg = (
            f"🔔 *New Villa Enquiry!*\n\n"
            f"🏡 *Villa:* {villa_id}\n"
            f"👤 *Name:* {name}\n"
            f"📞 *Phone:* {phone}\n"
            f"📅 *Dates:* {checkin} to {checkout}\n"
            f"👥 *Guests:* {guests}"
        )
        send_telegram_alert(alert_msg)
        return render_template('success.html')
    
    return render_template('enquiry.html', villa_id=villa_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
