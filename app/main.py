import socket  # noqa: F401
from threading import Thread


def reply(req, code, body="", headers={}):
    b_reply = b""
    match code:
        case 200:
            b_reply += b"HTTP/1.1 200 OK\r\n"
        case 404:
            b_reply += b"HTTP/1.1 404 Not Found\r\n"
        case 500:
            b_reply += b"HTTP/1.1 500 No\r\n"
    if not "Content-Type" in headers:
        headers["Content-Type"] = "text/plain"
    if body != "":
        headers["Content-Length"] = str(len(body))
    for key, val in headers.items():
        b_reply += bytes(key, "utf-8") + b": " + bytes(val, "utf-8") + b"\r\n"
    b_reply += b"\r\n" + bytes(body, "utf-8")
    return b_reply

def handle_request(conn, req):
    if req["path"] == "/":
        return reply(req, 200)
    if req["path"].startswith("/echo/"):
        return reply(req, 200, req["path"][6:])
    if req["path"] == "/user-agent":
        ua = req["headers"]["User-Agent"]
        return reply(req, 200, ua)
    return reply(req, 404)

def parse_request(bytes):
    output = {"method": "", "path": "", "headers": {}, "body": ""}
    lines = bytes.decode("utf-8").split("\r\n")
    if len(lines) < 3:
        return None
    reqLine = lines[0].split(" ")
    if (not reqLine[0]) or reqLine[0] not in ["GET", "POST", "PUT", "HEAD"]:
        return None
    if (not reqLine[1]) or reqLine[1][0] != "/":
        return None
    output["method"] = reqLine[0]
    output["path"] = reqLine[1]
    # Ignore HTTP version
    lines = lines[1:]
    c = 0
    for l in lines:
        if l == "":
            break
        headLine = l.split(":")
        output["headers"][headLine[0]] = headLine[1].lstrip()
        c += 1
    output["body"] = lines[c + 1]
    return output

def handle_client(conn):
    byte = []
    try:
        while (byte := conn.recv(1024)) != b"":
            parsed_req = parse_request(byte)
            if parsed_req == None:
                conn.send(str.encode("HTTP/1.1 500 No\r\n\r\n"))
                return conn.close()
            # Recv & parsed request
            conn.send(handle_request(conn, parsed_req))
            return conn.close()
    except Exception as e:
        print("handle_client err", e)
        
def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    threads = []
    while 1:
        conn, addr = server_socket.accept()  # wait for client
        t = Thread(target=handle_client, args=[conn])
        threads.append(t)
        t.run()

if __name__ == "__main__":
    main()
