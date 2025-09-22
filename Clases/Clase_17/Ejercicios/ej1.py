# Ejercicio 1: Servidor de Archivos Básico
# por defecto, al crear el servidor veo los directorios y subdirectorios en la raiz

from http.server import HTTPServer, SimpleHTTPRequestHandler

class MiHandler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None):
        if code == 404: 
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Archivo no encontrado (404)</h1>")
        else:
            super().send_error(code, message)

port = 8000
server = HTTPServer(("", port), MiHandler)
print(f"Servidor corriendo en http://localhost:{port}")
server.serve_forever()
