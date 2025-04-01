import threading
import socket


class TCPServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self) -> None:
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)
        print(f"Server started on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            threading.Thread(target=self.handle_request, args=(client_socket,)).start()

    def handle_request(self, client_socket: socket.socket) -> None:
        data = client_socket.recv(1024).decode("utf-8")
        lines = data.split("\r\n")
        path = lines[0].split()[1]
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}"
        elif path.startswith("/user-agent"):
            user_agent = lines[2].split(": ")[1]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client_socket.send(response.encode("utf-8"))
        client_socket.close()