import SimpleHTTPServer
import SocketServer
import json
import serial.tools.list_ports
import cgi
import subprocess
import tempfile
import urllib
import os.path
import platform
import threading

import sys
from PyQt4 import QtGui, QtCore
PORT = 9222
threads = []
tray = []

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
        
        #interpret post data
        length = int(self.headers['content-length'])
        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        msg = postvars["msg"][0]
        
        #set response headers
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        #actions to each message
        if(msg == "list_serialPorts"):
            #list serial ports with something connected
            ports = list(serial.tools.list_ports.comports())
            ports_connected = []
            for p in ports:
                if(p[2] != 'n/a'):
                    ports_connected.append(p)
            json_response = json.dumps(ports_connected)
            self.wfile.write(bytes(json_response));
            pass
        elif(msg == "send_programArduino"):
            #send program to arduino using avrdude
            tray[0].show_message("CodeRhino", "Sending program to Arduino")
            sendport = postvars["port"][0]
            tmpdir = tempfile.gettempdir()
            filename = postvars["filename"][0]
            stderr = ""
            subprocess.check_output(
                "cd "+tmpdir+" && "+tmpdir+"\\avrdude.exe -F -V -c arduino -p ATMEGA328P -P "+sendport+
                " 115200 -U flash:w:"+tmpdir+"\\"+filename+":i",
                stderr=subprocess.STDOUT,
                shell=True)
            if(stderr):
                print stderr
                self.wfile.write("error")
                tray[0].show_message("CodeRhino", "Cannot send program to Arduino")
                pass
            else:
                self.wfile.write("sent")
                tray[0].show_message("CodeRhino", "Program sent to Arduino")
                pass
            pass
        elif(msg == "send_programNxt"):
            #send program to nxt brick using nbc
            tray[0].show_message("CodeRhino", "Sending program to NXT")
            filename = postvars["filename"][0]
            tmpdir = tempfile.gettempdir()
            stderr = ""
            try:
                subprocess.check_call(
                    tmpdir+"\\nbc.exe -d "+tmpdir+"\\"+filename,
                    stderr=subprocess.STDOUT,
                    shell=True)
                print stderr
            except subprocess.CalledProcessError as e:
                tray[0].show_message("CodeRhino", "Cannot send program to NXT")
                stderr=e
            if(stderr):
                print stderr
                self.wfile.write("error")
                tray[0].show_message("CodeRhino", "Cannot send program to NXT")
                pass
            else:
                self.wfile.write("sent")
                tray[0].show_message("CodeRhino", "Program sent to NXT")
                pass
            pass
        elif(msg == "download"):
            #download a file
            filename = postvars["filename"][0]
            url = postvars["url"][0]
            tmpdir = tempfile.gettempdir()
            filedownloaded = urllib.URLopener()
            try:
                filedownloaded.retrieve(url, tmpdir+"/"+filename)
            except:
                self.wfile.write("error")
            else:
                #return a success message
                self.wfile.write("downloaded")
            pass
        elif(msg == "download_ifNotExists"):
            #download a file if it not exists (already downloaded)
            filename = postvars["filename"][0]
            url = postvars["url"][0]
            tmpdir = tempfile.gettempdir()
            if(os.path.isfile(tmpdir+"/"+filename) == False):
                filedownloaded = urllib.URLopener()
                try:
                    filedownloaded.retrieve(url, tmpdir+"/"+filename)
                except:
                    #returns a error message
                    self.wfile.write("error")
                else:
                    #returns a success message
                    self.wfile.write("downloaded")
            else:
                self.wfile.write("downloaded")
            pass
        elif(msg == "write_tmpdir"):
            #writes a binary file on temp dir
            filename = postvars["filename"][0]
            data = postvars["bindata"][0]
            tmpdir = tempfile.gettempdir()
            try:
                with open(tmpdir+"/"+filename, "wb") as f:
                    f.write(b''+data)
            except:
                #returns a error message
                self.wfile.write("error")
            else:
                #returns a success message
                self.wfile.write("wrote")
            pass
        elif(msg == "get_os"):
            #returns the os name
            self.wfile.write(platform.system())
            pass
        elif(msg == "get_arch"):
            #returns the architecture of machine
            self.wfile.write(platform.machine())
            pass


class RightClickMenu(QtGui.QMenu):
    def __init__(self, parent=None):
        QtGui.QMenu.__init__(self, "File", parent)
        
        icon = QtGui.QIcon("exit.ico")
        exitAction = QtGui.QAction(icon, "&Exit", self)
        exitAction.triggered.connect(lambda: exit_program())
        self.addAction(exitAction)
        
class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.setIcon(QtGui.QIcon("icon.ico"))
        #Menu
        self.right_menu = RightClickMenu()
        self.setContextMenu(self.right_menu)
    
    def welcome(self):
        self.showMessage("CodeRhinoP is running", "Now you can use client applications")
    
    def show_message(self, title, msg):
        self.showMessage(title, msg)
    
    def show(self):
        QtGui.QSystemTrayIcon.show(self)
        QtCore.QTimer.singleShot(100, self.welcome)
        
def start_server():
    print "Serving at port", PORT, "on", platform.system(), ":", platform.machine()
    httpd = SocketServer.TCPServer(("localhost", PORT), CustomHandler)
    httpd.serve_forever()

def exit_program():
    for thread in threads:
        thread.stop()
    sys.exit()
    
def main():
    app = QtGui.QApplication([])
    tray.append(SystemTrayIcon())
    tray[0].show()
    
    threads.append(threading.Thread(target=start_server))
    for thread in threads:
        thread.start()
    app.exec_()

if __name__ == "__main__":
    main()