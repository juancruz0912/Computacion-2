from http.server import HTTPServer, BaseHTTPRequestHandler

class MiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Construir la respuesta
        self.send_response(200)               # Código HTTP 200 OK
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hola Mundo")       # <- Acá va tu lógica

# Servidor escucha en el puerto 8080
server = HTTPServer(("localhost", 8080), MiHandler)
print("Servidor corriendo en http://localhost:8080")
server.serve_forever()
