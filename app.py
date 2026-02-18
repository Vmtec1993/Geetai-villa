import os
import json
import gspread
import datetime
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 1. Google Sheets Connection
def get_gspread_client():
    creds_json = os.environ.get('GOOGLE_CREDS')
    if not creds_json:
        return None
    try:
        creds_dict = json.loads(creds_json.strip())
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

# 2. Home Page (All Villas)
@app.route('/')
def index():
    try:
        client = get_gspread_client()
        if not client:
            return "Auth Error: Check Render Settings."
        
        spreadsheet = client.open("Geetai_Villa_Admin")
        sheet = spreadsheet.get_worksheet(0)
        villas = sheet.get_all_records()
        return render_template('index.html', villas=villas)
    except Exception as e:
        return f"Error loading index: {str(e)}"

# 3. Villa Details Page (The missing piece)
@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    try:
        client = get_gspread_client()
        spreadsheet = client.open("Geetai_Villa_Admin")
        sheet = spreadsheet.get_worksheet(0)
        villas = sheet.get_all_records()
        
        # शीट में Villa_ID कॉलम के साथ मैच करना
        villa = next((v for v in villas if str(v.get('Villa_ID')) == str(villa_id)), None)
        
        if villa:
            return render_template('villa_details.html', villa=villa)
        return "<h1>Villa Not Found</h1><p>Please check the ID in Google Sheet.</p>", 404
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Inquiry Form
@app.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')
        today = str(datetime.date.today())

        client = get_gspread_client()
        inquiry_sheet = client.open("Geetai_Villa_Admin").worksheet("Inquiries")
        inquiry_sheet.append_row([name, phone, message, today])

        return "<h1>Success!</h1><script>setTimeout(function(){ window.location.href='/'; }, 2000);</script>"
    except Exception as e:
        return f"Form Error: {str(e)}"

if __name__ == "__main__":
    # रेंडर के लिए पोर्ट सेटिंग
    port
           
