
def cmd_ping(_) -> bytes:
    return b"+PONG\r\n"

def cmd_echo(args: list[str]) -> bytes:
    if not args or len(args) != 1:
        return b"-ERR wrong number of arguments for 'echo' command\r\n"
    return f"${len(args[0])}\r\n{args[0]}\r\n".encode()


COMMANDS = {
    "PING": cmd_ping,
    "ECHO": cmd_echo
}

def handle_command(command: str, args):
    func = COMMANDS.get(command.upper())
    if func:
        return func(args)
    return f"-ERR unknown command '{command}'\r\n".encode()

