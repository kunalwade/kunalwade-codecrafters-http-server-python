import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # server_socket.accept() # wait for client

    server_socket.listen()
    client, addr = server_socket.accept()
    client_msg = client.recv(4096).decode().split(" ")
    if client_msg[1] == "/":
        client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    else:
        client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
if __name__ == "__main__":
    main()
