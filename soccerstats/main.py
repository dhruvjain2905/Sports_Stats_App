from flask import Flask, render_template, request, session, redirect, jsonify, flash
import os
from datetime import timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
import random
import httplib2
import os
from apiclient import discovery
from google.oauth2 import service_account

my_dict = {"PC": "B", "PI": "C", "SOG": "D", "SM": "E", "PL": "F", "TM": "G", "TMa": "H"}
app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # need to change

SERVICE_ACCOUNT_FILE = 'keys.json'

#just some setup
SCOPES = [
          "https://www.googleapis.com/auth/drive", 
          "https://www.googleapis.com/auth/drive.file", 
          "https://www.googleapis.com/auth/spreadsheets"
          ]

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

sheets_service = discovery.build('sheets', 'v4', credentials=creds)
drive_service = discovery.build('drive', 'v3', credentials=creds)
spreadsheet = {
    'properties': {
        'title': "soccer_stats"
    }
}


@app.route("/")
def red():
    return redirect('/add_players')
@app.route('/add_players', methods=['GET', 'POST'])
def add_players():
    if request.method == 'POST':
        num = request.form.get('password')
        email = request.form.get('email')
        session['email'] = email
        num = num.replace(" ","")
        num = list(num.split(","))
        print(num)
        session['number'] = num
        creation_response = sheets_service.spreadsheets().create(body=spreadsheet,
        fields='spreadsheetId').execute()

        spreadsheet_id = creation_response.get('spreadsheetId')
# The ID and range of a sample spreadsheet.
        session["spread_id"] = spreadsheet_id#"1tp-ucsg0x2_t1ySE13vrzM1cnHwV-WJvW2Y18MjL-zM"
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        my_list = [[i] for i in session['number']]
        length = len(session['number'])+1
        print(session['spread_id'])
        req = sheet.values().update(spreadsheetId=session["spread_id"], range="Sheet1!A2:A"+str(length), valueInputOption="USER_ENTERED", body={"values": my_list}).execute()
        objects = [["Pass Completed", "Pass Incomplete", "SOG", "Shot Miss", "Poss Loss", "Tackle Miss", "Tackle Made"]]
        req = sheet.values().update(spreadsheetId=session["spread_id"], range="Sheet1!B1:H1", valueInputOption="USER_ENTERED", body={"values": objects}).execute()
        zeros = [[0 for i in range(7)] for i in range(length-1)]
        req = sheet.values().update(spreadsheetId=session["spread_id"], range="Sheet1!B2:H"+str(length), valueInputOption="USER_ENTERED", body={"values": zeros}).execute()
        return redirect('/stocks')
    return render_template("add_stock.html")
    

@app.route('/stocks/', methods = ["POST", "GET"])
def list_stocks():
    return render_template('stocks.html')


@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()
    print(output) 
    flash("Event Added", "sucess")
    print(type(output))
    out = output.split()
    out = [i.replace('"','') for i in out]
    print(out)
    print(session['number'])
    n = session['number'].index(out[0])
    pos = 2+n
    letter = my_dict[out[1]]
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    res = sheet.values().get(spreadsheetId=session["spread_id"],
                                    range='Sheet1!'+letter+str(pos)+':'+letter+str(pos)).execute()

    values = res.get('values', [])
    values = int(values[0][0]) + 1

    req = sheet.values().update(spreadsheetId=session["spread_id"], range='Sheet1!'+letter+str(pos)+':'+letter+str(pos), valueInputOption="USER_ENTERED", body={"values": [[values]]}).execute()
    return redirect("/stocks")

@app.route('/done', methods=["GET", "POST"])
def send():
    new_file_permission = {
    'type': 'group',
    'role': 'writer',
    'emailAddress':session['email']
}

    permission_response = drive_service.permissions().create(
    fileId=session["spread_id"], body=new_file_permission).execute()

    return redirect("/add_players")
    
if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="192.168.1.162", port=5000)