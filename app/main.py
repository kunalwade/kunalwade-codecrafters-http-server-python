import socket  # noqa: F401
import threading
# Parse the request data to extract method, path, and version from the request
def parse_request(request_data):
    decoded_data = request_data.decode()
    lines = decoded_data.split("\r\n")
    # Get values from start line
    method, path, version = lines[0].split(" ")
    host = ""
    user_agent = ""
    # Iterate over the headers
    for line in lines[1:]:
        if line.startswith("Host: "):
            host = line[len("Host: ") :]
        elif line.startswith("User-Agent: "):
            user_agent = line[len("User-Agent: ") :]
    print(method, path, version, host, user_agent)
    return method, path, version, host, user_agent
# Return the HTTP response for a given path
def get_response(method, path, version, host, user_agent):
    if path == "/":
        return "HTTP/1.1 200 OK\r\n\r\n"
    if "echo" in path:
        string = path.strip("/echo/")
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string)}\r\n\r\n{string}"
    if "user-agent" in path:
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
    return "HTTP/1.1 404 Not Found\r\n\r\n"
def handle_request(client_socket):
    # Read data from client
    data = client_socket.recv(1024)
    # Parse the requestk
    method, path, version, host, user_agent = parse_request(data)
    # Get and send response based on path
    response = get_response(method, path, version, host, user_agent)
    client_socket.send(response.encode())
def main():
    # Create TCP/IP Socket
    port = 4221
    server_socket = socket.create_server(("localhost", port), reuse_port=True)
    print(f"Server is running on port {port}...")
    try:
        while True:
            # Wait for a connection
            print("Waiting for a connection...")
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_request, args=(client_socket, addr)).start()
            print(f"Connection from {addr} has been established")
            # Handle request from client
            handle_request(client_socket)
            # Close the connection to client
            client_socket.close()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        # Clean up server socket
        server_socket.close()
        print("Server has been shut down.")

if __name__ == "__main__":
    main()
