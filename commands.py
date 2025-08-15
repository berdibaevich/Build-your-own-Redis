from storage import KEY_VALUE, EXPIRY
from utils import current_time

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



COMMANDS = {
    "PING": cmd_ping,
    "ECHO": cmd_echo,
    "SET": cmd_set,
    "GET": cmd_get
}

def handle_command(command: str, args):
    func = COMMANDS.get(command.upper())
    if func:
        return func(args)
    return f"-ERR unknown command '{command}'\r\n".encode()

