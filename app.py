from flask import Flask, render_template, request, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# Google Sheets Setup
def get_sheets_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        # अपनी शीट का नाम यहाँ चेक कर लेना
        sheet = client.open("Geetai_Villa_Data").get_all_records()
        return sheet
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/')
def index():
    villas = get_sheets_data()
    return render_template('index.html', villas=villas)

@app.route('/villa/<villa_id>')
def villa_details(villa_id):
    villas = get_sheets_data()
    villa = next((v for v in villas if str(v.get('Villa_ID', '')) == str(villa_id)), None)
    if villa is None:
        return "<h1>Villa Not Found!</h1><a href='/'>Go Back</a>", 404
    return render_template('villa_details.html', villa=villa)

# --- Enquiry & Success Routes ---

@app.route('/enquiry/<villa_id>')
def enquiry(villa_id):
    villas = get_sheets_data()
    villa = next((v for v in villas if str(v.get('Villa_ID', '')) == str(villa_id)), None)
    return render_template('enquiry.html', villa=villa)

@app.route('/submit_enquiry', methods=['POST'])
def submit_enquiry():
    try:
        # फॉर्म से डेटा लेना
        villa_name = request.form.get('villa_name', 'Unknown Villa')
        user_name = request.form.get('name', 'Guest')
        user_phone = request.form.get('phone', 'No Phone')
        
        # आप चाहें तो यहाँ डेटा को प्रिंट कर सकते हैं देखने के लिए
        print(f"Booking Request: {villa_name} by {user_name} ({user_phone})")
        
        return redirect(url_for('success'))
    except Exception as e:
        print(f"Error submitting enquiry: {e}")
        return "Something went wrong. Please try again.", 500

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
