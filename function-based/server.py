from socket import socket, create_server
from threading import Thread
from utils import parse_resp
from commands import handle_command
from manager import (
    _add_client,
    _remove_client
)
from constants import RedisResponse


def handle_client(client: socket):
    while True:
        req = client.recv(1024)
        if not req:
            _remove_client(client_socket=client) # Remove client
            print("Client disconnected...")
            break

        data = req.decode()
        command, args = parse_resp(data)
        response = handle_command(client_socket=client, command=command, args=args)
        
        if isinstance(response, RedisResponse):
            continue
        
        client.sendall(response)


def redis_server():
    server_socket = create_server(("localhost", 6379), reuse_port = True)
    while True:
        client, _ = server_socket.accept()
        _add_client(client)
        Thread(target=handle_client, args=(client, )).start()



if __name__ == "__main__":
    redis_server()