# Library imports
import mysql.connector
from getpass import getpass
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import shutil
import json

# Database information
DEFAULT_HOST = "localhost"
DEFAULT_USER = "root"
DEFAULT_PASSWORD = "root"
DEFAULT_DB = "f1racing"

# Server information
DEFAULT_PORT = 8080
HOSTNAME = "localhost"
PATH = "HTML"

if not os.path.isdir(PATH):
    print("Error! The HTML dir with the web templates has not been found.")
    print("Please make sure that you are running this script from the same folder as where the HTML folder is located.")
    print("Existing...")
    os._exit(-1)

try:
    # SQL database connection and queries functions
    print("We need the credentials to create the MySQL connection. Press enter to use the default parameter in brackets or enter your own values for the following parameters:")
    host = input(f"Host [{DEFAULT_HOST}]: ")
    host = DEFAULT_HOST if host == "" else host

    user = input(f"User [{DEFAULT_USER}]: ")
    user = DEFAULT_USER if user == "" else user

    password = getpass(f"Password [{DEFAULT_PASSWORD}]: ")
    password = DEFAULT_PASSWORD if password == "" else password

    database = input(f"Database [{DEFAULT_DB}]: ")
    database = DEFAULT_DB if database == "" else database

    connection = mysql.connector.connect(host=host, user=user, password=password, database=database)

    if connection.is_connected():
        print("The connection to MySQL was successfully established!")
    cursor = connection.cursor()

    def get_columns(table_name):
        if table_name == "F1Awards":
            columns = ['AwardID', 'DriverID', 'AwardName', 'AwardDescription', 'AwardImage', 'Date']
        elif table_name == "Team":
            columns = ['TeamName', 'Base', 'TeamChief', 'TechnicalChief', 'Chassis', 'PowerUnit', 'FirstTeamEntry', 'WorldChampionships', 'HighestRaceFinish', 'PolePosition', 'FastestLaps']
        elif table_name == "Driver":
            columns = ['DriverID', 'Name', 'TeamName', 'Country', 'Podiums', 'Points', 'GrandPrixEntered', 'WorldChampionships', 'HighestRaceFinish', 'DateOfBirth', 'GlobalRank']
        elif table_name == "Race":
            columns = ['RaceID', 'Laps', 'Location', 'TrackName']
        elif table_name == "RaceTrack":
            columns = ['TrackName', 'FirstGrandPrix', 'NumberOfLaps', 'LapRecord', 'RaceDistance', 'CircuitLength']
        elif table_name == "RaceSchedule":
            columns = ['ScheduleID', 'RaceID', 'TrackName', 'StartTime', 'EndTime', 'Date', 'Broadcaster']
        elif table_name == "RaceDriverDetails":
            columns = ['RaceID', 'DriverID', 'Car', 'RacePoints', 'TimeRetired', 'Position']
        return columns

    def get_drivers():
        select_query = """
            SELECT * from Driver
        """
        cursor.execute(select_query)
        drivers_sql = cursor.fetchall()
        drivers = []

        for driver in drivers_sql:
            drivers.append({'DriverID': driver[0], 'Name': driver[1], 'TeamName': driver[2], 'Country': driver[3], 'Podiums': driver[4], 'Points': driver[5], 'GrandPrixEntered': driver[6], 'WorldChampionships': driver[7], 'HighestRaceFinish': driver[8], 'DateOfBirth': driver[9], 'GlobalRank': driver[10]})

        return drivers

    def get_f1awards():
        select_query = """
            SELECT * from F1Awards
        """
        cursor.execute(select_query)
        f1awards_sql = cursor.fetchall()
        f1awards = []

        for f1award in f1awards_sql:
            f1awards.append({'AwardID': f1award[0], 'DriverID': f1award[1], 'AwardName': f1award[2], 'AwardDescription': f1award[3], 'AwardImage': f1award[4], 'Date': f1award[5]})

        return f1awards

    def get_races():
        select_query = """
            SELECT * from Race
        """
        cursor.execute(select_query)
        races_sql = cursor.fetchall()
        races = []

        for race in races_sql:
            races.append({'RaceID': race[0], 'Laps': race[1], 'Location': race[2], 'TrackName': race[3]})

        return races

    def get_racedriverdetails():
        select_query = """
            SELECT * from RaceDriverDetails
        """
        cursor.execute(select_query)
        racedriverdetails_sql = cursor.fetchall()
        racedriverdetails = []

        for details in racedriverdetails_sql:
            racedriverdetails.append({'RaceID': details[0], 'DriverID': details[1], 'Car': details[2], 'RacePoints': details[3], 'TimeRetired': details[4], 'Position': details[5]})

        return racedriverdetails

    def get_raceschedules():
        select_query = """
            SELECT * from RaceSchedule
        """
        cursor.execute(select_query)
        raceschedules_sql = cursor.fetchall()
        raceschedules = []

        for schedule in raceschedules_sql:
            raceschedules.append({'ScheduleID': schedule[0], 'RaceID': schedule[1], 'TrackName': schedule[2], 'StartTime': schedule[3], 'EndTime': schedule[4], 'Date': schedule[5], 'Broadcaster': schedule[6]})

        return raceschedules

    def get_racetracks():
        select_query = """
            SELECT * from RaceTrack
        """
        cursor.execute(select_query)
        racetracks_sql = cursor.fetchall()
        racetracks = []

        for track in racetracks_sql:
            racetracks.append({'TrackName': track[0], 'FirstGrandPrix': track[1], 'NumberOfLaps': track[2], 'LapRecord': track[3], 'RaceDistance': track[4], 'CircuitLength': track[5]})

        return racetracks

    def get_teams():
        select_query = """
            SELECT * from Team
        """
        cursor.execute(select_query)
        teams_sql = cursor.fetchall()
        teams = []

        for team in teams_sql:
            teams.append({'TeamName': team[0], 'Base': team[1], 'TeamChief': team[2], 'TechnicalChief': team[3], 'Chassis': team[4], 'PowerUnit': team[5], 'FirstTeamEntry': team[6], 'WorldChampionships': team[7], 'HighestRaceFinish': team[8], 'PolePosition': team[9], 'FastestLaps': team[10]})

        return teams

    #CUD operations
    def create_record(table_name, data):
        columns = get_columns(table_name)
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data))
        connection.commit()

    def update_record(table_name, record_id, primary_key, data):
        columns = get_columns(table_name)
        set_values = ', '.join([f"{key}=%s" for key in columns])
        query = f"UPDATE {table_name} SET {set_values} WHERE {primary_key}=%s"
        cursor.execute(query, tuple(data) + (record_id,))
        connection.commit()

    def update_record_2pks(table_name, record_id_1, record_id_2, primary_key_1, primary_key_2, data):
        columns = get_columns(table_name)
        set_values = ', '.join([f"{key}=%s" for key in columns])
        query = f"UPDATE {table_name} SET {set_values} WHERE {primary_key_1}=%s AND {primary_key_2}=%s"
        cursor.execute(query, tuple(data) + (record_id_1, record_id_2,))
        connection.commit()

    def delete_record(table_name, record_id, primary_key):
        query = f"DELETE FROM {table_name} WHERE {primary_key}=%s"
        cursor.execute(query, (record_id,))
        connection.commit()

    def delete_record_2pks(table_name, record_id_1, record_id_2, primary_key_1, primary_key_2):
        query = f"DELETE FROM {table_name} WHERE {primary_key_1}=%s AND {primary_key_2}=%s"
        cursor.execute(query, (record_id_1, record_id_2,))
        connection.commit()

    # HTML server code
    class MyServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)

            template_mode = False
            asset = False
            try:
                if self.path == '/':
                    print(f"DEBUG: Sending index.html with path {self.path}")
                    file = open(f'{PATH}/index.html', 'r')
                elif self.path in ['/f1awards', '/team', '/driver', '/race', '/racetrack', '/raceschedule', '/racedriverdetails']:
                    template_mode = True
                    print(f"DEBUG: Sending template.html with path {self.path}")
                    file = open(f'{PATH}/template.html', 'r')
                else:
                    print(f"DEBUG: Sending {PATH}{self.path} with path {self.path}")
                    file = open(f'{PATH}{self.path}', 'rb')
                    asset = True
            except:
                template_mode = True
                print(f"DEBUG: Sending error page with path {self.path}")
                file = open(f'{PATH}/error.html')

            if asset:
                if "favicon" in self.path:
                    self.send_header("Content-type", "image/jpeg")
                else:
                    self.send_header("Content-type", "text/html")
                self.end_headers()
                shutil.copyfileobj(file, self.wfile)
                file.close()
            else:
                self.send_header("Content-type", "text/html")
                self.end_headers()
                # Read the whole file
                lines = file.readlines()
                file.close()
            
                # Loop through the rest of the file and print each line
                title = ""
                for line in lines:
                    line_written = False
                    if template_mode:
                        if f'<a href="{self.path}">' in line:
                            title = line.split('">')[1].split('</a>')[0]
                            append_line = line.replace(f'<a href="{self.path}">', f'<a class="active" href="{self.path}">')
                        elif "<!-- TITLE -->" in line:
                            title = title if title[-1] == 's' else f"{title}s"
                            append_line = f'{line.replace("<!-- TITLE -->", title)}'
                        elif "<!-- COLUMN_NAMES -->" in line:
                            if self.path == "/f1awards":
                                columns = ['ID', 'DriverID', 'AwardName', 'AwardDescription', 'AwardImage', 'Date', 'Actions']
                            elif self.path == "/team":
                                columns = ['Name', 'Base', 'Chief', 'TechChief', 'Chassis', 'PowerUnit', 'FirstEntry', 'Championships', 'HighestFinish', 'PolePos', 'FastestLaps', 'Actions']
                            elif self.path == "/driver":
                                columns = ['ID', 'Name', 'Team', 'Country', 'Podiums', 'Points', 'GrandPrixEntered', 'Championships', 'HighestRaceFinish', 'DateOfBirth', 'GlobalRank', 'Actions']
                            elif self.path == "/race":
                                columns = ['ID', 'Laps', 'Location', 'TrackName', 'Actions']
                            elif self.path == "/racetrack":
                                columns = ['Name', 'FirstGrandPrix', 'NumberOfLaps', 'LapRecord', 'RaceDistance', 'CircuitLength', 'Actions']
                            elif self.path == "/raceschedule":
                                columns = ['ScheduleID', 'RaceID', 'TrackName', 'StartTime', 'EndTime', 'Date', 'Broadcaster', 'Actions']
                            elif self.path == "/racedriverdetails":
                                columns = ['RaceID', 'DriverID', 'Car', 'RacePoints', 'TimeRetired', 'Position', 'Actions']
                            for column in columns:
                                self.wfile.write(bytes(f'<th>{column}</th>', "utf-8"))
                            line_written = True
                        elif "<!-- ROWS -->" in line:
                            if self.path == "/f1awards":
                                rows = get_f1awards()
                                table_name = "F1Awards"
                                primary_key = "AwardID"
                            elif self.path == "/team":
                                rows = get_teams()
                                table_name = "Team"
                                primary_key = "TeamName"
                            elif self.path == "/driver":
                                rows = get_drivers()
                                table_name = "Driver"
                                primary_key = "DriverID"
                            elif self.path == "/race":
                                rows = get_races()
                                table_name = "Race"
                                primary_key = "RaceID"
                            elif self.path == "/racetrack":
                                rows = get_racetracks()
                                table_name = "RaceTrack"
                                primary_key = "TrackName"
                            elif self.path == "/raceschedule":
                                rows = get_raceschedules()
                                table_name = "RaceSchedule"
                                primary_key = "ScheduleID"
                            elif self.path == "/racedriverdetails":
                                rows = get_racedriverdetails()
                                table_name = "RaceDriverDetails"
                                primary_key = "RaceID"
                                primary_key_2 = "DriverID"
                            for row in rows:
                                self.wfile.write(bytes('<tr><td class="limiter"></td>', "utf-8"))

                                i = 1
                                for column in row.keys():
                                    self.wfile.write(bytes(f"""<td id="{row[primary_key]}{f';{row[primary_key_2]}' if 'primary_key_2' in locals() else ''}-{i}">{row[column]}</td>""", "utf-8"))
                                    i += 1

                                # Add action buttons
                                self.wfile.write(bytes(f"""<td><span onClick="modify('{row[primary_key]}{f';{row[primary_key_2]}' if "primary_key_2" in locals() else ''}')" id="{row[primary_key]}{f';{row[primary_key_2]}' if 'primary_key_2' in locals() else ''}-modify">✏️</span><span onClick="remove('{row[primary_key]}{f';{row[primary_key_2]}' if "primary_key_2" in locals() else ''}')" id="{row[primary_key]}{f';{row[primary_key_2]}' if 'primary_key_2' in locals() else ''}-remove">❌</span></td>""", "utf-8"))

                                self.wfile.write(bytes('<td class="limiter"></td></tr>', "utf-8"))

                            line_written = True
                        elif "<!-- ERROR PATH -->" in line:
                            append_line = f'{line.replace("<!-- ERROR PATH -->", self.path)}'
                        elif "<!-- PATH -->" in line:
                            append_line = f'{line.replace("<!-- PATH -->", self.path)}'
                        else:
                            append_line = f"{line}"
                    else:
                        append_line = f"{line}"
                    if not line_written:
                        self.wfile.write(bytes(append_line, "utf-8"))
        
        def do_DELETE(self):
            print("Something should be deleted :)")
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            post_data_str = post_data_bytes.decode("UTF-8")
            res = json.loads(post_data_str)
            print(f"I got this from the delete record: {res}")
            if self.path == "/f1awards":
                table_name = "F1Awards"
                primary_key = "AwardID"
            elif self.path == "/team":
                table_name = "Team"
                primary_key = "TeamName"
            elif self.path == "/driver":
                table_name = "Driver"
                primary_key = "DriverID"
            elif self.path == "/race":
                table_name = "Race"
                primary_key = "RaceID"
            elif self.path == "/racetrack":
                table_name = "RaceTrack"
                primary_key = "TrackName"
            elif self.path == "/raceschedule":
                table_name = "RaceSchedule"
                primary_key = "ScheduleID"
            elif self.path == "/racedriverdetails":
                table_name = "RaceDriverDetails"
                primary_key = "RaceID"
                primary_key_2 = "DriverID"
            
            try:
                if "primary_key_2" in locals():
                    delete_record_2pks(table_name, res['PK'].split(';')[0], res.split(';')[1], primary_key, primary_key_2)
                    print(f"Removed entry from {table_name} with 2 PKs!")
                else:
                    delete_record(table_name, res['PK'], primary_key)
                    print(f"Removed entry from {table_name} with 1 PK!")
                self.wfile.write(bytes(json.dumps({'res': "ok"}), "utf-8"))
            except Exception as e:
                msg = f"Catched exception from database: {e}."
                print(msg)
                self.wfile.write(bytes(json.dumps({'res': "fail", 'msg': msg}), "utf-8"))

        def do_PUT(self):
            print("Something should be updated :D")
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            post_data_str = post_data_bytes.decode("UTF-8")
            res = json.loads(post_data_str)
            print(f"I got this from the update record: {res}")
            if self.path == "/f1awards":
                table_name = "F1Awards"
                primary_key = "AwardID"
            elif self.path == "/team":
                table_name = "Team"
                primary_key = "TeamName"
            elif self.path == "/driver":
                table_name = "Driver"
                primary_key = "DriverID"
            elif self.path == "/race":
                table_name = "Race"
                primary_key = "RaceID"
            elif self.path == "/racetrack":
                table_name = "RaceTrack"
                primary_key = "TrackName"
            elif self.path == "/raceschedule":
                table_name = "RaceSchedule"
                primary_key = "ScheduleID"
            elif self.path == "/racedriverdetails":
                table_name = "RaceDriverDetails"
                primary_key = "RaceID"
                primary_key_2 = "DriverID"
            
            try:
                if "primary_key_2" in locals():
                    update_record_2pks(table_name, res['PK'].split(';')[0], res.split(';')[1], primary_key, primary_key_2, res['data'])
                    print(f"Updated entry from {table_name} with 2 PKs!")
                else:
                    update_record(table_name, res['PK'], primary_key, res['data'])
                    print(f"Updated entry from {table_name} with 1 PK!")
                self.wfile.write(bytes(json.dumps({'res': "ok"}), "utf-8"))
            except Exception as e:
                msg = f"Catched exception from database: {e}."
                traceback.print_exc()
                print(msg)
                self.wfile.write(bytes(json.dumps({'res': "fail", 'msg': msg}), "utf-8"))

        def do_POST(self):
            print("Something should be created :))")
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            post_data_str = post_data_bytes.decode("UTF-8")
            res = json.loads(post_data_str)
            print(f"I got this from the create record: {res}")
            if self.path == "/f1awards":
                table_name = "F1Awards"
                primary_key = "AwardID"
            elif self.path == "/team":
                table_name = "Team"
                primary_key = "TeamName"
            elif self.path == "/driver":
                table_name = "Driver"
                primary_key = "DriverID"
            elif self.path == "/race":
                table_name = "Race"
                primary_key = "RaceID"
            elif self.path == "/racetrack":
                table_name = "RaceTrack"
                primary_key = "TrackName"
            elif self.path == "/raceschedule":
                table_name = "RaceSchedule"
                primary_key = "ScheduleID"
            elif self.path == "/racedriverdetails":
                table_name = "RaceDriverDetails"
                primary_key = "RaceID"
                primary_key_2 = "DriverID"
            
            try:
                create_record(table_name, res['data'])
                print(f"Created a new row on {table_name}K!")
                self.wfile.write(bytes(json.dumps({'res': "ok"}), "utf-8"))
            except Exception as e:
                msg = f"Catched exception from database: {e}."
                traceback.print_exc()
                print(msg)
                self.wfile.write(bytes(json.dumps({'res': "fail", 'msg': msg}), "utf-8"))

    print("We need the information to create HTML server. Press enter to use the default parameter in brackets or enter your own values for the following parameters:")
    port = input(f"Port [{DEFAULT_PORT}]: ")
    port = DEFAULT_PORT if port == "" else int(port)


    # Main code
    webServer = HTTPServer((HOSTNAME, port), MyServer)
    print("Web server started at http://%s:%s" % (HOSTNAME, port))
    webServer.serve_forever()

except Exception as e:
    print(f"There was a failure with the database: {e}.\nExisting...")
    traceback.print_exc()
except KeyboardInterrupt:
    print("\nExiting...")

if 'webServer' in locals():
    webServer.server_close()
