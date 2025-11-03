from socket import socket
from storage import KEY_VALUE, EXPIRY, LIST
from utils import current_time, encode_array
from decorators import does_not_require_client, requires_client
from manager import (
    _block_client, 
    _get_client_id, 
    _check_blocked_client,
    ACTIVE_CLIENTS, BLOCKED_CLIENTS
)
from constants import BLOCKED, RedisResponse


@does_not_require_client
def cmd_ping(_) -> bytes:
    print("ACTIVE_CLIENTS: ", ACTIVE_CLIENTS)
    print("BLOCKED_CLIENTS: ", BLOCKED_CLIENTS)
    return b"+PONG\r\n"


@does_not_require_client
def cmd_echo(args: list[str]) -> bytes:
    if not args or len(args) != 1:
        return b"-ERR wrong number of arguments for 'echo' command\r\n"
    return f"${len(args[0])}\r\n{args[0]}\r\n".encode()


@does_not_require_client
def cmd_set(args: list[str]) -> bytes:
    _len = len(args)
    if _len not in (2, 4):
        return b"-ERR wrong number of arguments for 'set' command\r\n"

    if _len == 2:
        KEY_VALUE[args[0]] = args[-1]
        return b"+OK\r\n"

    if _len == 4:
        if args[-2].lower() != "px" or not args[-1].isdigit():
            return b"-ERR syntax error\r\n"
        KEY_VALUE[args[0]] = args[1]
        EXPIRY[args[0]] = current_time() + int(args[-1])

    return b"+OK\r\n"
    

@does_not_require_client
def cmd_get(args: list[str]) -> bytes:
    """
        https://redis.io/docs/latest/develop/reference/protocol-spec/#null-bulk-strings
    """
    if len(args) != 1:
        return b"-ERR wrong number of arguments for 'get' command\r\n"

    expire_at = EXPIRY.get(args[0])
    if expire_at and current_time() >= expire_at:
        KEY_VALUE.pop(args[0], None)
        EXPIRY.pop(args[0], None)

    data = KEY_VALUE.get(args[0])
    
    if data:
        return f"${len(data)}\r\n{data}\r\n".encode()
    return b"$-1\r\n"


@does_not_require_client
def cmd_rpush(args: list[str]) -> bytes:
    if len(args) == 1:
        return b"-ERR wrong number of arguments for 'rpush' command\r\n"
    
    key = args.pop(0)
    if key not in LIST:
        LIST[key] = []

    LIST[key].extend(args)

    # If someone waiting for that "key" we need to unblocking...
    _check_blocked_client(key)

    return f":{len(LIST[key])}\r\n".encode()


@does_not_require_client
def cmd_lrange(args: list[str]) -> bytes:
    if len(args) != 3:
        return b"-ERR wrong number of arguments for 'lrange' command\r\n" 

    key = args.pop(0)
    if key not in LIST:
        return b"*0\r\n"
    
    try:
        start = int(args[0])
        stop = int(args[-1])
        if stop >= 0:
            end = stop if stop <= len(LIST[key]) else len(LIST[key])
            items = LIST[key][start:end+1]
        else:
            items = LIST[key][start:stop+1] if stop != -1 else LIST[key][start:]
    except:
        return b"-ERR value is not an integer or out of range\r\n"
    
    return encode_array(items)


@does_not_require_client
def cmd_lpush(args: list[str]) -> bytes:
    if len(args) == 1:
        return b"-ERR wrong number of arguments for 'lpush' command\r\n"
    
    key = args.pop(0)
    if key not in LIST:
        LIST[key] = []

    for arg in args:
        LIST[key].insert(0, arg)

    # If someone waiting for that "key" we need to unblocking...
    _check_blocked_client(key)

    return f":{len(LIST[key])}\r\n".encode()


@does_not_require_client
def cmd_llen(args: list[str]) -> bytes:
    if len(args) != 1:
        return b"-ERR wrong number of arguments for 'llen' command\r\n"
    
    return f":{len(LIST.get(args[0], []))}\r\n".encode()


@does_not_require_client
def cmd_lpop(args: list[str]) -> bytes:
    if len(args) == 0 or len(args) > 2:
        return b"-ERR wrong number of arguments for 'lpop' command\r\n"

    key = args.pop(0)
    if key not in LIST or not LIST[key]:
        return b"$-1\r\n"

    how_many = len(args) # how many elements
    try:
        i = 0 if how_many == 0 else int(args[0])
        which = min(i, len(LIST[key])) if i > 0 else 0 
        
        items = [LIST[key].pop(0) for _ in range(1 if which == 0 else which)]
    except ValueError:
        return b"-ERR value is out of range, must be positive\r\n"
    
    if len(items) > 1:
        return encode_array(items=items)

    return f"${len(items[0])}\r\n{items[0]}\r\n".encode()


@requires_client
def cmd_blpop(client: socket, args: list[str]):
    if not args or len(args) < 2:
        return b"-ERR wrong number of arguments for 'blpop' command\r\n"
    
    timeout_str = args.pop()
    try:
        timeout = float(timeout_str)
    except ValueError:
        return b"-ERR timeout is not a float or out of range\r\n"

    key = args[0]

    if key not in LIST and timeout == 0.0:
        _id = _get_client_id(client)
        _block_client(key, timeout, _id)
        return BLOCKED
    


COMMANDS = {
    "PING": cmd_ping,
    "ECHO": cmd_echo,
    "SET": cmd_set,
    "GET": cmd_get,
    "RPUSH": cmd_rpush,
    "LRANGE": cmd_lrange,
    "LPUSH": cmd_lpush,
    "LLEN": cmd_llen,
    "LPOP": cmd_lpop,
    "BLPOP": cmd_blpop
}


def handle_command(client_socket: socket, command: str, args: list[str]) -> bytes | RedisResponse:
    func = COMMANDS.get(command.upper())
    if func:
        return func(client_socket, args)
    return f"-ERR unknown command '{command}'\r\n".encode()

