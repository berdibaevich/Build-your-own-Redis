from storage import KEY_VALUE, EXPIRY, LIST
from utils import current_time, encode_array

def cmd_ping(_) -> bytes:
    return b"+PONG\r\n"


def cmd_echo(args: list[str]) -> bytes:
    if not args or len(args) != 1:
        return b"-ERR wrong number of arguments for 'echo' command\r\n"
    return f"${len(args[0])}\r\n{args[0]}\r\n".encode()


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


def cmd_rpush(args: list[str]) -> bytes:
    if len(args) == 1:
        return b"-ERR wrong number of arguments for 'rpush' command\r\n"
    
    key = args.pop(0)
    if not key in LIST:
        LIST[key] = []

    LIST[key].extend(args)
    return f":{len(LIST[key])}\r\n".encode()


def cmd_lrange(args: list[str]) -> bytes:
    if len(args) != 3:
        return b"-ERR wrong number of arguments for 'lrange' command\r\n" 

    key = args.pop(0)
    if not key in LIST:
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


def cmd_lpush(args: list[str]) -> bytes:
    if len(args) == 1:
        return b"-ERR wrong number of arguments for 'lpush' command\r\n"
    
    key = args.pop(0)
    if not key in LIST:
        LIST[key] = []

    for arg in args:
        LIST[key].insert(0, arg)
    
    return f":{len(LIST[key])}\r\n".encode()


def cmd_llen(args: list[str]) -> bytes:
    if len(args) != 1:
        return b"-ERR wrong number of arguments for 'llen' command\r\n"
    
    return f":{len(LIST.get(args[0], []))}\r\n".encode()


COMMANDS = {
    "PING": cmd_ping,
    "ECHO": cmd_echo,
    "SET": cmd_set,
    "GET": cmd_get,
    "RPUSH": cmd_rpush,
    "LRANGE": cmd_lrange,
    "LPUSH": cmd_lpush,
    "LLEN": cmd_llen
}


def handle_command(command: str, args):
    func = COMMANDS.get(command.upper())
    if func:
        return func(args)
    return f"-ERR unknown command '{command}'\r\n".encode()

