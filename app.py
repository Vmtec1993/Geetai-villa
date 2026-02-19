import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_gspread_client():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get("GOOGLE_CREDS")
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Gspread Error: {e}")
        return None

@app.route('/')
def index():
    try:
        client = get_gspread_client()
        if client:
            sheet = client.open("Geetai_Villa_Data").get_worksheet(0)
            # Duplicate header एरर से बचने के लिए सीधा values उठाना
            data = sheet.get_all_values()
            headers = data[0]
            villas = [dict(zip(headers, row)) for row in data[1:]]
            return render_template('index.html', villas=villas)
        return "Database Connection Failed", 500
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return render_template('index.html', villas=[])

@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    try:
        client = get_gspread_client()
        if client:
            sheet = client.open("Geetai_Villa_Data").get_worksheet(0)
            data = sheet.get_all_values()
            headers = data[0]
            villas = [dict(zip(headers, row)) for row in data[1:]]
            villa = next((v for v in villas if str(v.get('Villa_ID', '')).strip() == str(villa_id).strip()), None)
            if not villa:
                return "Villa Not Found", 404
            return render_template('villa_details.html', villa=villa)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/enquiry/<villa_id>')
def enquiry(villa_id):
    # यहाँ सुनिश्चित करें कि villa_id HTML को पास हो रही है
    return render_template('enquiry.html', villa_id=villa_id)

@app.route('/submit_enquiry', methods=['POST'])
def submit_enquiry():
    try:
        client = get_gspread_client()
        if client:
            sheet = client.open("Geetai_Villa_Data").worksheet("Enquiries")
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                request.form.get('name'),
                request.form.get('phone'),
                request.form.get('check_in'),
                request.form.get('check_out'),
                request.form.get('guests'),
                request.form.get('message')
            ]
            sheet.append_row(row)
            return redirect(url_for('success'))
        return "Sheet Connection Failed", 500
    except Exception as e:
        logger.error(f"Submit Error: {e}")
        return f"Submission Failed: Make sure 'Enquiries' tab exists in Google Sheets.", 500

@app.route('/success')
def success():
    # अब यह "Success" पेज को रेंडर करेगा
    return render_template('success.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
