import os
import random
from flask import Flask, render_template, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

def get_sheets_data():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        # credentials.json check
        if os.path.exists("credentials.json"):
            creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
            client = gspread.authorize(creds)
            
            # य़हाँ नाम चेक करें: क्या आपकी शीट का नाम "Geetai_Villa_Data" ही है?
            sheet_name = "Geetai_Villa_Data" 
            spreadsheet = client.open(sheet_name)
            sheet = spreadsheet.get_worksheet(0)
            data = sheet.get_all_records()
            return data
        else:
            print("ERROR: credentials.json file not found on GitHub")
    except Exception as e:
        print(f"SHEET CONNECTION ERROR: {e}")
    return []

@app.route('/')
def index():
    villas = get_sheets_data()
    # अगर शीट कनेक्ट नहीं हुई, तो डमी विला दिखाएगा ताकि साइट खाली न लगे
    if not villas:
        villas = [{
            "Villa_ID": 1, "Name": "Geetai Premium Villa (Sample)", 
            "BHK": "4 BHK", "Price": "12,000", "Rating": 4.9,
            "Image_Main": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800"
        }]
    return render_template('index.html', villas=villas)

@app.route('/villa/<int:villa_id>')
def villa_details(villa_id):
    villas = get_sheets_data()
    villa = next((v for v in villas if v.get('Villa_ID') == villa_id), None)
    if not villa:
        # Fallback for details
        villa = {"Villa_ID": 1, "Name": "Geetai Premium Villa", "Price": "12,000", "BHK": "4 BHK", "Rating": 4.9, "Image_Main": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800", "Description": "Luxury villa in Lonavala with pool."}
    return render_template('villa_details.html', villa=villa)

@app.route('/inquiry')
def inquiry():
    return render_template('inquiry.html')

if __name__ == '__main__':
    app.run(debug=True)
            
