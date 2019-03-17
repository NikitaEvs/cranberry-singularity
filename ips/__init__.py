from ips.utils import warn_tb
from .structures import Powerstand
from .internals import *

__version__ = "1.0"
__all__ = ["init", "buffer", "enqueue", "call", "exit_with", "Powerstand",
           "send_orders", "get_launches", "get_timeout", "get_queue",
           "debug_buffer_file", "debug_buffer_json", "debug_launches",
           "debug_timeout", "debug_psm_file", "debug_psm_json",
           "set_order_trace",
           ]

preflight_check()


def init():
    data = get_psm()
    if data is None:
        warn_tb("An empty powerstand?!", cut=None)
        return None
    return Powerstand(data)


def exit_with(body):
    set_buffer(body)
    exit(0)


def call(name, body):
    error_text = call_children(name, body)
    if error_text is not None:
        raise Exception("Couldn't call script. " + error_text)
    return unlock_and_get_buffer()


# Лучше явно указать, что эти функции проброшены из ядра фреймворка

buffer = get_buffer
enqueue = enqueue
get_launches = get_launches
get_timeout = get_timeout
get_queue = get_queue
set_order_trace = set_order_trace
send_orders = send_orders

debug_psm_json = debug_psm_json
debug_psm_file = debug_psm_file
debug_buffer_json = debug_buffer_json
debug_buffer_file = debug_buffer_file
debug_launches = debug_launches
debug_timeout = debug_timeout
