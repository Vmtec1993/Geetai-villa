import os
import random
from flask import Flask, render_template, request, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Google Sheets Setup
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    # Check if file exists to avoid crash
    if os.path.exists("credentials.json"):
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("Geetai_Villa_Data").get_worksheet(0)
        inquiry_sheet = client.open("Geetai_Villa_Data").get_worksheet(1)
    else:
        sheet = None
        print("Error: credentials.json not found on server")
except Exception as e:
    print(f"Sheet Error: {e}")
    sheet = None

def get_villas():
    if not sheet: return []
    try:
        data = sheet.get_all_records()
        for villa in data:
            if not villa.get('Rating'):
                villa['Rating'] = round(random.uniform(4.5, 5.0), 1)
        return data
    except:
        return []

@app.route('/')
def index():
    villas = get_villas()
    return render_template('index.html', villas=villas)

@app.route('/villa/<int:villa_id>')
def villa_details(villa_id):
    villas = get_villas()
    villa = next((v for v in villas if v.get('Villa_ID') == villa_id), None)
    if villa:
        return render_template('villa_details.html', villa=villa)
    return "Villa Not Found", 404

@app.route('/inquiry')
def inquiry():
    return render_template('inquiry.html')

@app.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        date = request.form.get('date')
        guests = request.form.get('guests')
        message = request.form.get('message')
        if 'inquiry_sheet' in globals() and inquiry_sheet:
            inquiry_sheet.append_row([name, phone, date, guests, message])
        return render_template('success.html')
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
    
