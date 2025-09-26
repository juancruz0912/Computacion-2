import socketserver
import os

class ProcessTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        cur_process = os.getpid()
        response = bytes("{}: {}".format(cur_process, data), 'ascii')
        print(response)
        self.request.sendall(response)

class ForkingTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    HOST, PORT = "localhost", 9060

    server = ForkingTCPServer((HOST, PORT), ProcessTCPRequestHandler)
    
    with server:
        ip, port = server.server_address
        server.serve_forever()
        print("Server loop running in thread:", server.name)
