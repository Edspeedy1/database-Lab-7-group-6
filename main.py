import http.server
import sqlite3
import json

PORT = 8042

CONN = sqlite3.connect("database.db")
CURSOR = CONN.cursor()

class customRequestHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '/home':
            self.path = '/index.html'
        self.path = "/web/" + self.path
        print("post" + self.path)
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/teams':
            teams = CURSOR.execute("SELECT teamName FROM teams").fetchall()
            self.send_json_response(200, teams)
        elif self.path == '/players':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
            teamID = CURSOR.execute("SELECT teamId FROM teams WHERE teamName = ?", (data['team'],)).fetchone()[0]
            players = CURSOR.execute("SELECT firstName, lastName, playerId FROM players WHERE teamId = ?", (teamID,)).fetchall()
            self.send_json_response(200, list(map(lambda x: {"name":x[0] + " " + x[1], "id":x[2]}, players)))
        elif self.path == '/stats':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
            print(data)
            stats = CURSOR.execute("SELECT blocks, points FROM players WHERE playerId = ?", (data['player'],)).fetchone()
            print(stats)
            self.send_json_response(200, {"blocks": stats[0], "points": stats[1]})

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

with http.server.HTTPServer(("", PORT), customRequestHandler) as httpd:
    print("serving at port", PORT)
    print("http://localhost:" + str(PORT))
    httpd.serve_forever()