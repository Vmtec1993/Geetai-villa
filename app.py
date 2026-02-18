import os
import json
import gspread
import datetime
from flask import Flask, render_template, request, redirect
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets Connection Function
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

# 1. Home Page - विला की लिस्ट दिखाएगा
@app.route('/')
def index():
    try:
        client = get_gspread_client()
        if not client: return "Auth Error: Check Render Settings."
        spreadsheet = client.open("Geetai_Villa_Admin")
        sheet = spreadsheet.get_worksheet(0) # पहला टैब
        villas = sheet.get_all_records()
        return render_template('index.html', villas=villas)
    except Exception as e:
        return f"Error: {str(e)}"

# 2. Villa Details Page - विला की पूरी जानकारी
@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    try:
        client = get_gspread_client()
        spreadsheet = client.open("Geetai_Villa_Admin")
        sheet = spreadsheet.get_worksheet(0)
        villas = sheet.get_all_records()
        villa = next((v for v in villas if str(v.get('Villa_ID')) == str(villa_id)), None)
        if villa:
            return render_template('villa_details.html', villa=villa)
        return "Villa Not Found", 404
    except Exception as e:
        return f"Error: {str(e)}"

# 3. Inquiry Form - शीट में सेव करेगा और WhatsApp पर भेजेगा
@app.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')
        villa_name = request.form.get('villa_name', 'General')
        today = str(datetime.date.today())

        # Google Sheet (Inquiries टैब) में डेटा डालना
        client = get_gspread_client()
        spreadsheet = client.open("Geetai_Villa_Admin")
        inquiry_sheet = spreadsheet.worksheet("Inquiries") # पक्का करें ये टैब बना हुआ है
        inquiry_sheet.append_row([today, name, phone, villa_name, message])

        # WhatsApp पर भेजने के लिए लिंक बनाना
        # यहाँ अपना नंबर डालें (91 के साथ)
        my_number = "91XXXXXXXXXX" 
        text = f"Hello! New Inquiry for {villa_name}.\nName: {name}\nPhone: {phone}\nMessage: {message}"
        whatsapp_url = f"https://wa.me/{my_number}?text={text.replace(' ', '%20')}"

        return redirect(whatsapp_url)
    except Exception as e:
        return f"Form Error: {str(e)}. Did you create the 'Inquiries' tab in your sheet?"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
