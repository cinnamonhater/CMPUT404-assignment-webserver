#  coding: utf-8 
import socketserver
from pathlib import Path
from email.utils import formatdate

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

#Initializing variables
msg_200 = 'HTTP/1.1 200 OK\r\n'
msg_405 = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
msg_404 = 'HTTP/1.1 404 Not Found\r\n'
msg_301 = 'HTTP/1.1 301 Moved Permanently\r\n'
htmlcontent = "Content-Type: text/html; charset=utf-8\r\n"
csscontent = "Content-Type: text/css; charset=utf-8\r\n"

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):

        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n\n" % self.data)
        decodedData = self.data.decode('utf-8')
        
        #Getting the name of the method
        decodedsplitdata = decodedData.split()
        method = decodedsplitdata[0]

        #Dealing with requests other than GET
        if method == "POST" or method == "PUT" or method == "DELETE":
            message = msg_405
            self.request.sendall(message.encode())
            return

        elif method == "GET":

            #Getting the URI
            if (len(decodedData) > 1):
                split_info = decodedData.split()
                addressother = split_info[1]
            
            address = "www" + addressother
            path = Path(address)
            
            if path.exists():
                
                #For an HTML file
                if address.endswith('html'): 
                    file_data = open(path, "r").read()
                    message = msg_200
                    message += htmlcontent
                
                #For a css file
                elif address.endswith('css'):
                    file_data = open(path,"r").read()
                    message = msg_200
                    message += csscontent
                
                elif address.endswith("/") :
                    address = address + "index.html"
                    path = Path(address)
                    file_data = open(path,"r").read() 
                    message = msg_200
                    message += htmlcontent

                elif not address.endswith('/'):
                    addressalt = address + "/index.html"
                    path = Path(address)
                    pathother = Path(addressalt)

                    if not pathother.exists():
                        message = msg_404
                        file_data = ""
                    else: 
                        file_data = open(pathother,"r").read()
                        message = msg_301
                        message += htmlcontent
                        message += "Location:http://127.0.0.1:8080{}/\r\n".format(addressother)
                    
                #Adding date, time, and length of packet to the header
                message += "Date:{}\r\n".format(formatdate(timeval=None, localtime=False, usegmt=True))
                message += "Content-Length: {}\r\n".format(len(file_data))

                message += "\r\n"

                #Adding the contents of the file to teh packet
                message += file_data

            else:
                #Path doesn't exist
                message = msg_404

            self.request.sendall(message.encode())
        
    
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    
    with socketserver.TCPServer((HOST, PORT), MyWebServer) as server:
        server.serve_forever()
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C