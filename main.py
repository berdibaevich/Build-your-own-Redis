import socket
from threading import Thread


def handle_command(client):
    while True:
        req = client.recv(1024)
        if not req:
            break
        client.sendall(b"+PONG\r\n")


def main():
    server_socket = socket.create_server(("localhost", 6379))
    while True:
        conn, _ = server_socket.accept() # Wait a client
        Thread(target=handle_command, args=(conn,)).start()


if __name__ == "__main__":
    main()

