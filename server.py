import SimpleHTTPServer
import SocketServer
import json
import serial.tools.list_ports

PORT = 9222

DUMMY_RESPONSE = "<h1>CodeRhinoP</h1>"

class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print "GET REQUEST"
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-length", len(DUMMY_RESPONSE))
        self.end_headers()
        self.wfile.write(DUMMY_RESPONSE)
        
    def do_POST(self):
        print "POST REQUEST"
        ports = list(serial.tools.list_ports.comports())
        ports_connected = []
        for p in ports:
            if(p[2] != 'n/a'):
                ports_connected.append(p)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        json_response = json.dumps(ports_connected)
        self.wfile.write(bytes(json_response));
        

httpd = SocketServer.TCPServer(("", PORT), CustomHandler)

print "serving at port", PORT
httpd.serve_forever()