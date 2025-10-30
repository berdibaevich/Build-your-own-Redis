from socket import socket, create_server
from threading import Thread
from utils import parse_resp
from commands import handle_command


def handle_client(client: socket):
    while True:
        req = client.recv(1024)
        if not req:
            print("Client disconnected...")
            break

        data = req.decode()
        command, args = parse_resp(data)
        response = handle_command(command, args)

        client.sendall(response)


def redis_server():
    server_socket = create_server(("localhost", 6379), reuse_port = True)
    while True:
        client, _ = server_socket.accept()
        Thread(target=handle_client, args=(client, )).start()



if __name__ == "__main__":
    redis_server()