from storage import KEY_VALUE


def cmd_ping(_) -> bytes:
    return b"+PONG\r\n"


def cmd_echo(args: list[str]) -> bytes:
    if not args or len(args) != 1:
        return b"-ERR wrong number of arguments for 'echo' command\r\n"
    return f"${len(args[0])}\r\n{args[0]}\r\n".encode()


def cmd_set(args: list[str]) -> bytes:
    if not args or len(args) != 2:
        return b"-ERR wrong number of arguments for 'set' command\r\n"

    KEY_VALUE[args[0]] = args[-1]
    return b"+OK\r\n"


def cmd_get(args: list[str]) -> bytes:
    """
        https://redis.io/docs/latest/develop/reference/protocol-spec/#null-bulk-strings
    """
    if not args or len(args) != 1:
        return b"-ERR wrong number of arguments for 'get' command\r\n"

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

