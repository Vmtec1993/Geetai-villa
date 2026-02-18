import os
import json
import gspread
import datetime
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- GOOGLE SHEETS SETUP ---
def get_gspread_client():
    # Render के Environment Variables से 'GOOGLE_CREDS' उठाएगा
    creds_json = os.environ.get('GOOGLE_CREDS')
    if not creds_json:
        # Local टेस्टिंग के लिए credentials.json
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    else:
        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    return gspread.authorize(creds)

# --- ROUTES ---

# 1. Home Page (Villa List)
@app.route('/')
def index():
    try:
        client = get_gspread_client()
        sheet = client.open("Geetai_Villa_Admin").sheet1
        villas = sheet.get_all_records()
        return render_template('index.html', villas=villas)
    except Exception as e:
        return f"Error loading index: {str(e)}"

# 2. Villa Details Page
@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    try:
        client = get_gspread_client()
        sheet = client.open("Geetai_Villa_Admin").sheet1
        villas = sheet.get_all_records()
        villa = next((v for v in villas if str(v['Villa_ID']) == villa_id), None)
        
        if villa:
            return render_template('villa_details.html', villa=villa)
        return "Villa Not Found", 404
    except Exception as e:
        return f"Error loading details: {str(e)}"

# 3. Inquiry Form Submission (नया हिस्सा)
@app.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    try:
        # फॉर्म से डेटा निकालना
        name = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')
        today = str(datetime.date.today())

        # Google Sheet के 'Inquiries' टैब में सेव करना
        client = get_gspread_client()
        # पक्का करें कि आपकी शीट में 'Inquiries' नाम का टैब है
        inquiry_sheet = client.open("Geetai_Villa_Admin").worksheet("Inquiries")
        inquiry_sheet.append_row([name, phone, message, today])

        # सफलता का मैसेज (इसके बाद HTML वाला JavaScript खुद WhatsApp पर ले जाएगा)
        return "<h1>Success!</h1><p>Redirecting to WhatsApp...</p><script>setTimeout(function(){ window.location.href='/'; }, 3000);</script>"
    
    except Exception as e:
        return f"Form Submission Error: {str(e)}. Please check if 'Inquiries' tab exists in your Google Sheet."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
