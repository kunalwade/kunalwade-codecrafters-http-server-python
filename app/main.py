import socket  # noqa: F401
import threading

def handle_client(client_socket):
    """Handle a single client connection."""
    # Receive the request (we'll ignore the request data for now)
    request = client_socket.recv(1024)

    # Send a basic HTTP response
    response = "HTTP/1.1 200 OK\r\n\r\n"
    client_socket.sendall(response.encode())

    # Close the client connection
    client_socket.close()

def start_server(host='localhost', port=4221):
    """Start the HTTP server and listen for incoming connections."""
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)  # Listen for up to 5 connections

    print(f"Server started on {host}:{port}")

    while True:
        # Accept a new incoming connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Handle the client connection in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
if __name__ == "__main__":
    main()
