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

        #num = num.replace(" ","")
        num = list(num.split(","))
        num = [i.strip() for i in num]

        events = request.form.get('eves')
        #events = events.replace(" ","")
        events = list(events.split(","))

       
        print(num)
        print(events)
        session["undos"] = []
        session['number'] = num
        session["number2"] = [i.replace(" ", "") for i in num]
        session['events'] = events
        session["events2"] = [i.replace(" ", "") for i in events]
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
        objects = [events]
        l = len(events)
        letter_dict = {"B": 1, "C":2, "D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15,"Q":16,"R":17,"S":18,"T":19,"U":20,"V":21,"W":22,"X":23,"Y":24,"Z":25}
        def get_key(val):
            for key, value in letter_dict.items():
                if val == value:
                    return key
 
                return "key doesn't exist"
 
# Driver Code
 
        letter = get_key(l)
 

        req = sheet.values().update(spreadsheetId=session["spread_id"], range="Sheet1!B1:"+str(l)+"1", valueInputOption="USER_ENTERED", body={"values": objects}).execute()
        zeros = [[0 for i in range(l)] for i in range(length-1)]
        req = sheet.values().update(spreadsheetId=session["spread_id"], range="Sheet1!B2:"+str(l)+str(length), valueInputOption="USER_ENTERED", body={"values": zeros}).execute()
        try: 
            new_file_permission = {
        'type': 'group',
        'role': 'writer',
        'emailAddress':session['email']
    }

            permission_response = drive_service.permissions().create(
            fileId=session["spread_id"], body=new_file_permission).execute()
        
        except:
            flash("Could not send spreadsheet to email", category="error")
            return(redirect("/add_players"))

        session["link"] = "https://docs.google.com/spreadsheets/d/"+session["spread_id"]

        return redirect('/stocks')
    return render_template("add_stock.html")
    

@app.route('/stocks/', methods = ["POST", "GET"])
def list_stocks():
    return render_template('stocks.html')


@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()
    print(output) 
    print(session['email'])
    
    my_list = session["undos"]
    print(my_list)
    my_list.append(output)
    if len(my_list) > 5:
        my_list.pop(0)
    
    session["undos"] = my_list
    print(session["undos"])

    out = output.replace('~',' ')
    out = out.split()
    out = [i.replace('"','') for i in out]
    print(out)

    print(session['number2'])
    n = session['number2'].index(out[0])
    pos = 2+n
    print(out[1])
    print(session['events2'])
    letter = session["events2"].index(out[1])
    print(letter)
    letter_dict = {"B": 1, "C":2, "D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15,"Q":16,"R":17,"S":18,"T":19,"U":20,"V":21,"W":22,"X":23,"Y":24,"Z":25}
    def get_key(val):
        for key, value in letter_dict.items():
            if val == value:
                return key
 
            return "key doesn't exist"
    print(list(letter_dict.keys())[list(letter_dict.values()).index(letter+1)])
# Driver Code
    letter = list(letter_dict.keys())[list(letter_dict.values()).index(letter+1)]


    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    print('Sheet1!'+letter+str(pos)+':'+letter+str(pos))
    res = sheet.values().get(spreadsheetId=session["spread_id"],
                                    range='Sheet1!'+letter+str(pos)+':'+letter+str(pos)).execute()

    values = res.get('values', [])
    values = int(values[0][0]) + 1

    req = sheet.values().update(spreadsheetId=session["spread_id"], range='Sheet1!'+letter+str(pos)+':'+letter+str(pos), valueInputOption="USER_ENTERED", body={"values": [[values]]}).execute()
    return redirect("/stocks")

@app.route('/done', methods=["GET", "POST"])
def send():
    ###new_file_permission = {
    #'type': 'group',
    #'role': 'writer',
    #'emailAddress':session['email']
#}

    #permission_response = drive_service.permissions().create(
    #fileId=session["spread_id"], body=new_file_permission).execute()

    return redirect("/add_players")

@app.route('/undo', methods=["GET", "POST"])
def remov_el():
    the_list = session["undos"]
    print(the_list)
    if len(the_list) > 0:
        output = the_list[-1]
        out = output.replace('~',' ')
        out = out.split()
        out = [i.replace('"','') for i in out]
        print(out)

        print(session['number2'])
        n = session['number2'].index(out[0])
        pos = 2+n
        print(out[1])
        print(session['events2'])
        letter = session["events2"].index(out[1])
        print(letter)
        letter_dict = {"B": 1, "C":2, "D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15,"Q":16,"R":17,"S":18,"T":19,"U":20,"V":21,"W":22,"X":23,"Y":24,"Z":25}
        def get_key(val):
            for key, value in letter_dict.items():
                if val == value:
                    return key
    
                return "key doesn't exist"
        print(list(letter_dict.keys())[list(letter_dict.values()).index(letter+1)])
    # Driver Code
        letter = list(letter_dict.keys())[list(letter_dict.values()).index(letter+1)]


        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        print('Sheet1!'+letter+str(pos)+':'+letter+str(pos))
        res = sheet.values().get(spreadsheetId=session["spread_id"],
                                        range='Sheet1!'+letter+str(pos)+':'+letter+str(pos)).execute()

        values = res.get('values', [])
        values = int(values[0][0]) - 1

        
        req = sheet.values().update(spreadsheetId=session["spread_id"], range='Sheet1!'+letter+str(pos)+':'+letter+str(pos), valueInputOption="USER_ENTERED", body={"values": [[values]]}).execute()
        
        the_list.pop(-1)
        session["undos"] = the_list
        
        flash("Stat Removed", category = "success")

        return redirect("/stocks")
    else:
        flash("Could not remove further stats", category="error")
        return redirect("/stocks")

    
if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="192.168.1.162", port=5000)