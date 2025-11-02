import time
from socket import socket

# Client Manager
ACTIVE_CLIENTS = {} # {client_id: socket_object}
SOCKET_TO_ID = {} # {socket_object: client_id}

CURRENT_ID: int = 0

def _add_client(client_socket: socket):
    global CURRENT_ID
    CURRENT_ID += 1

    ACTIVE_CLIENTS[CURRENT_ID] = client_socket
    SOCKET_TO_ID[client_socket] = CURRENT_ID


def _remove_client(client_socket: socket):
    global ACTIVE_CLIENTS, SOCKET_TO_ID
    
    client_id = SOCKET_TO_ID.get(client_socket)
    if not client_id:
        return
    
    del SOCKET_TO_ID[client_socket]
    del ACTIVE_CLIENTS[client_id]

