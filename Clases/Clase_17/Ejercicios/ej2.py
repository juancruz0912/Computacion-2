import http.server
import json
from urllib.parse import urlparse, parse_qs

# Datos en memoria
usuarios = {}
ultimo_id = 0

class MiHandler(http.server.BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def _parse_id(self):
        partes = self.path.strip('/').split('/') #strip('/'): quita los / del principio y final y split('/'): divide la ruta en partes, por ejemplo /users/3 → ["users", "3"].
        if len(partes) == 2 and partes[0] == "users" and partes[1].isdigit():
            return int(partes[1])
        return None

    def do_GET(self):
        if self.path == "/users":
            self._set_headers()
            self.wfile.write(json.dumps(list(usuarios.values())).encode()) # stream de salida, por donde se le envian los datos al cliente.
        else:
            user_id = self._parse_id()
            if user_id is not None and user_id in usuarios:
                self._set_headers()
                self.wfile.write(json.dumps(usuarios[user_id]).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Usuario no encontrado"}).encode())

    def do_POST(self):
        if self.path == "/users":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                global ultimo_id
                ultimo_id += 1
                usuario = {"id": ultimo_id, **data}
                usuarios[ultimo_id] = usuario
                self._set_headers(201)
                self.wfile.write(json.dumps(usuario).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "JSON inválido"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode())

    def do_PUT(self):
        user_id = self._parse_id()
        if user_id is not None and user_id in usuarios:
            content_length = int(self.headers.get('Content-Length', 0))
            put_data = self.rfile.read(content_length)
            try:
                data = json.loads(put_data)
                usuarios[user_id].update(data)
                self._set_headers()
                self.wfile.write(json.dumps(usuarios[user_id]).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "JSON inválido"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Usuario no encontrado"}).encode())

    def do_DELETE(self):
        user_id = self._parse_id()
        if user_id is not None and user_id in usuarios:
            del usuarios[user_id]
            self._set_headers(204)  # Sin contenido
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Usuario no encontrado"}).encode())

if __name__ == "__main__":
    from http.server import HTTPServer
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, MiHandler)
    print("Servidor corriendo en http://localhost:8000")
    httpd.serve_forever()
