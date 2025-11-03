from functools import wraps


def does_not_require_client(view_func):
    @wraps(view_func)
    def _wrapper(client_socket, args):
        return view_func(args)
    return _wrapper


def requires_client(view_func):
    @wraps(view_func)
    def _wrapper(client_socket, args):
        return view_func(client_socket, args)
    return _wrapper