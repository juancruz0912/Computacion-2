import socketserver
import datetime

class MyUDPHandler(socketserver.BaseRequestHandler):  # protocolo capa 7
    def handle(self):
        data = self.request[0].strip()  # El mensaje recibido
        socket = self.request[1]        # El socket asociado
        command = data.decode("utf-8")

        print(f"[SERVER] Recibido de {self.client_address}: {command}")

        if command.lower() == "now":
            response = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            response = "Comando no reconocido"

        socket.sendto(response.encode("utf-8"), self.client_address)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 5000  # Escuchar en todas las interfaces
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        print("[SERVER] Servidor UDP escuchando en puerto 5000...")
        server.serve_forever()
