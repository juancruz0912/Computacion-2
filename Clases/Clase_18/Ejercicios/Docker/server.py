import socketserver
import datetime

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        command = data.decode("utf-8")
        print(f"[SERVER] Recibido: {command}")

        if command.lower() == "now":
            response = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            response = "Comando no reconocido"

        self.request.sendall(response.encode("utf-8"))

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 5000  # Escuchar en todas las interfaces
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("[SERVER] Servidor escuchando en puerto 5000...")
        server.serve_forever()
