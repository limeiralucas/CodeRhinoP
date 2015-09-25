from tornado import websocket, web, ioloop
import json
import tempfile
import urllib
import os
import subprocess

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("<h4>CodeRhinoP says WELCOME</h4>")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        print 'Client connected'
            
    def on_close(self):
        print 'Client disconnected'
            
    def on_message(self, json_data):
        data = json.loads(json_data)
        command = data[u'message']
        # Download command
        if command == -1:
            self.write_message(json.dumps{'request': -1, 'code': 'exited'})
        elif command == 0:
            print 'Downloading'
            url = data[u'url']
            path = tempfile.gettempdir() + '/' + data[u'filename']
            try:
                urllib.urlretrieve(url, path)
            except:
                print 'Download error'
                self.write_message(json.dumps({'request': 0, 'code':'dl_error', 'url':url}))
            print 'Downloaded'
            self.write_message(json.dumps({'request': 0, 'code':'dl_ok', 'url':url}))
        # Download if not exists
        elif command == 1:
            print 'Verifying'
            url = data[u'url']
            path = tempfile.gettempdir() + '/' + data[u'filename']
            if os.path.isfile(path) == False:
                try:
                    urllib.urlretrieve(url, path)
                except:
                    print 'Download error'
                    self.write_message(json.dumps({'request': 1, 'code':'dl_error', 'url':url}))
                print 'Downloaded'
                self.write_message(json.dumps({'request': 1, 'code':'dl_ok', 'url':url}))
            else:
                print 'File already exists'
                self.write_message(json.dumps({'request': 1, 'code':'dl_file_already_exists', 'url':url}))
        # Write on temporary directory (tmpdir)
        elif command == 2:
            path = tempfile.gettempdir() + '/' + data[u'filename']
            data = data['bindata']
            try:
                with open(path, 'wb') as f:
                    f.write(b''+data)
            except:
                self.write_message(json.dumps({'request': 2, 'code':'wr_error', 'url':url}))
            print 'Wrote on tmpdir'
            self.write_message(json.dumps({'request': 2, 'code':'wr_ok', 'url':url}))
        elif command == 3:
            filename = data[u'filename']
            tmpdir = tempfile.gettempdir()
            path = tmpdir + '\\' + filename
            stderr = ""
            try:
                subprocess.check_call(
                    tmpdir+"/nbc.exe -d "+path,
                    stderr=subprocess.STDOUT,
                    shell=True)
                print stderr
            except subprocess.CalledProcessError as e:
                print 'Error sending program'
                self.write_message(json.dumps({'request': 3, 'code':'nxt_send_error', 'filename': filename}))
                stderr=e
            if(stderr):
                print stderr
                self.write_message(json.dumps({'request': 3, 'code':'nxt_send_error', 'filename': filename}))
                pass
            print 'Program sent'
            self.write_message(json.dumps({'request': 3, 'code':'nxt_send_ok', 'filename': filename}))
                    
            
app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
])

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()