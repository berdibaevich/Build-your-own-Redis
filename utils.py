import time

def parse_resp(raw: str):
    """
        $ redis-cli ECHO hey
        we receive from client like "*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n"
        https://redis.io/docs/latest/develop/reference/protocol-spec/
    """
    parts = [p for p in raw.split("\r\n") if p]

    length = int(parts[0][1:])
    args = []
    i = 1
    for _ in range(length):
        _len = int(parts[i][1:])
        value = parts[i + 1]
        args.append(value)
        i += 2
    
    return args.pop(0), args


def current_time():
    # milliseconds
    return time.time() * 1000