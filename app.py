import os
import json
import gspread
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials
import requests

app = Flask(__name__)

# --- Google Sheets Setup ---
creds_json = os.environ.get('GOOGLE_CREDS')
sheet = None
enquiry_sheet = None

if creds_json:
    try:
        info = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        
        SHEET_ID = "1wXlMNAUuW2Fr4L05ahxvUNn0yvMedcVosTRJzZf_1ao"
        main_spreadsheet = client.open_by_key(SHEET_ID)
        sheet = main_spreadsheet.sheet1
        
        try:
            enquiry_sheet = main_spreadsheet.worksheet("Enquiries")
        except:
            enquiry_sheet = sheet
    except Exception as e:
        print(f"Sheet Error: {e}")

# --- Telegram Alert (Direct Method) ---
TELEGRAM_TOKEN = "7913354522:AAH1XxMP1EMWC59fpZezM8zunZrWQcAqH18"
TELEGRAM_CHAT_ID = "6746178673"

def send_telegram_alert(message):
    try:
        # ब्राउज़र वाले लिंक की तरह ही काम करेगा
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        # यहाँ हम POST का इस्तेमाल कर रहे हैं जो सबसे सुरक्षित है
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- Routes ---

@app.route('/')
def index():
    if sheet:
        try:
            villas = sheet.get_all_records()
            return render_template('index.html', villas=villas)
        except Exception as e:
            print(f"Index Page Error: {e}")
    return "Database Connection Error", 500

@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    if sheet:
        try:
            villas = sheet.get_all_records()
            villa = next((v for v in villas if str(v.get('Villa_ID')) == str(villa_id)), None)
            if villa:
                return render_template('villa_details.html', villa=villa)
        except Exception as e:
            print(f"Details Error: {e}")
    return "Villa not found", 404

@app.route('/enquiry/<villa_id>', methods=['GET', 'POST'])
def enquiry(villa_id):
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        guests = request.form.get('guests')
        message = request.form.get('message')

        # Google Sheet में डाटा डालना
        if enquiry_sheet:
            try:
                enquiry_sheet.append_row([villa_id, name, phone, check_in, check_out, guests, message])
            except: pass

        # टेलीग्राम नोटिफिकेशन
        alert_text = f"New Enquiry!\nVilla: {villa_id}\nName: {name}\nPhone: {phone}"
        send_telegram_alert(alert_text)
        
        # यहाँ सिर्फ एक मैसेज दिखाएगा अगर success.html नहीं है तो
        return "<h1>Thank You! Your Enquiry has been sent.</h1><a href='/'>Back to Home</a>"
    
    return render_template('enquiry.html', villa_id=villa_id)

if __name__ == '__main__':
    # Render के लिए पोर्ट फिक्स
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
