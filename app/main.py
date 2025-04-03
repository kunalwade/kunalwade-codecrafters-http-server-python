import sys
import socket
import threading

# Config
HOST = "localhost"
PORT = 4221
FILES_DIR = ""

# HTTP Statuses
HTTP_STATUS_OK = "HTTP/1.1 200 OK\r\n"
HTTP_STATUS_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n"
HTTP_STATUS_CREATED = "HTTP/1.1 201 Created\r\n"


def response(status, headers, body):
    """
    Returns a properly formatted HTTP response.

    Args:
        status (str): The HTTP status code and message.
        headers (dict): A dictionary of HTTP headers.
        body (str): The response body.

    Returns:
        bytes: The encoded HTTP response.
    """
    return (status +
            "".join(f"{k}: {v}\r\n" for k, v in headers.items()) +
            "\r\n" +
            body + "\r\n").encode()


def handle_request(request, files=None):
    """
    Handle incoming HTTP requests and generate appropriate HTTP responses.

    Args:
        request (list): A list containing the HTTP request data.
        files (str, optional): The path to the directory containing
                               files to be served. Defaults to None.

    Returns:
        response: An HTTP response object containing
        the appropriate status code, headers, and body.
    """
    method, path, _ = request[0].split(" ")

    if method == "GET" and path == "/":
        res = response(
            status=HTTP_STATUS_OK + "\r\n",
            headers={},
            body=""
        )

    elif method == "GET" and path.startswith('/echo'):
        content = path.split("/echo/")[1]
        res = response(
            status=HTTP_STATUS_OK,
            headers={"Content-Type": "text/plain",
                     "Content-Length": len(content)},
            body=content
        )

    elif method == "GET" and path.startswith('/user-agent'):
        content = request[2].split(": ")[1]
        res = response(
            status=HTTP_STATUS_OK,
            headers={"Content-Type": "text/plain",
                     "Content-Length": len(content)},
            body=content
        )

    elif path.startswith('/files'):
        file_name = path.split("/files/")[1]
        if method == "POST":
            content = request[-1]
            handle_files(
                file_name=file_name,
                file_content=content, mode="write")

            res = response(
                status=HTTP_STATUS_CREATED,
                headers={"Content-Type": "text/plain",
                         "Content-Length": len(content)},
                body=content
            )
        else:
            file_content = handle_files(
                file_name=file_name, mode="read")
            if file_content:
                res = response(
                    status=HTTP_STATUS_OK,
                    headers={"Content-Type": "application/octet-stream",
                             "Content-Length": len(file_content)},
                    body=file_content
                )
            else:
                res = response(
                    status=HTTP_STATUS_NOT_FOUND + "\r\n",
                    headers={},
                    body=""
                )

    else:
        res = response(
            status=HTTP_STATUS_NOT_FOUND + "\r\n",
            headers={},
            body=""
        )

    return res


def handle_files(file_name, file_content=None, mode="read"):
    if mode == 'write':
        with open(f"{FILES_DIR}{file_name}", "w", encoding='UTF8') as f:
            file = f.write(file_content)

    else:
        try:
            with open(f"{FILES_DIR}{file_name}", "r") as f:
                file = f.read()
        except FileNotFoundError:
            file = None

    return file


def handle_client(conn, addr):
    """
    Handle incoming client requests.

    Args:
        conn (socket): The client socket connection.
        addr (tuple): The client address.

    Returns:
        bytes: The response to send back to the client.
    """
    request = conn.recv(4096).decode(
        ).splitlines()

    conn.send(handle_request(request))
    conn.close()


def main(args):
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    if args:
        global FILES_DIR
        FILES_DIR = args[1]

    while True:
        conn, addr = server_socket.accept() # wait for client

        thread = threading.Thread(target=handle_client, args=(conn, addr))

        thread.start()



if __name__ == "__main__":
    main(sys.argv[1:])
