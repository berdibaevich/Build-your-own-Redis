import time
from socket import socket
from utils import encode_array
from storage import LIST

# Client Manager
ACTIVE_CLIENTS = {} # {client_id: socket_object}
SOCKET_TO_ID = {} # {socket_object: client_id}

CURRENT_ID: int = 0

BLOCKED_CLIENTS = {} # {key: [(client_id, timeout), ()]}


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


def _get_client_id(client_socket: socket) -> int:
    return SOCKET_TO_ID[client_socket]


def _get_current_client_id():
    return CURRENT_ID


def _block_client(key: str, timeout: float, client_id: int):
    if key not in BLOCKED_CLIENTS:
        BLOCKED_CLIENTS[key] = []

    BLOCKED_CLIENTS[key].append((client_id, time.time() + timeout))


def _unblock_client(key: str, client_id: int, timeout: float):
    BLOCKED_CLIENTS[key].remove((client_id, timeout))


def _check_blocked_client(key: str):
    if key in BLOCKED_CLIENTS:
        for client_id, timeout in BLOCKED_CLIENTS[key]:
            client_socket = ACTIVE_CLIENTS[client_id]
            value = LIST[key].pop(0)

            response = encode_array([key, value])
            client_socket.sendall(response)

            _unblock_client(key, client_id, timeout)
        
        # If key's value is empty so we remove key..
        if not BLOCKED_CLIENTS[key]:
            del BLOCKED_CLIENTS[key]

