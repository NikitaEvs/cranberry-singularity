import sys
import time
import json

from ips.utils import warn_tb

__all__ = [
    "preflight_check", "get_psm", "get_buffer", "set_buffer", "call_children",
    "send_one_order", "send_orders", "get_launches", "get_timeout",
    "get_queue", "enqueue", "debug_psm_file", "debug_psm_json",
    "debug_buffer_file", "debug_buffer_json", "set_order_trace",
    "debug_launches", "debug_timeout", "unlock_and_get_buffer"
]


def preflight_check():
    if sys.version_info < (3, 6):
        raise EnvironmentError("Слишком старый интерпретатор. Ожидается версия не младше 3.6.")

    global __powerstand_data
    __powerstand_data = None
    global __buffer_data
    __buffer_data = None
    global __queue
    __queue = []

    global __launches
    __launches = 99
    global __timeout
    __timeout = time.time() + 10

    global __trace_orders
    __trace_orders = True


def set_order_trace(value):
    global __trace_orders
    __trace_orders = bool(value)


def get_psm():
    global __powerstand_data
    return __powerstand_data


def get_buffer():
    global __buffer_data
    return __buffer_data


def get_launches(name):
    global __launches
    return __launches


def get_timeout():
    global __timeout
    return __timeout


def get_queue():
    # TODO: кому нужно, тот пусть и реализует
    # очередь представлена списком строк
    global __queue
    return __queue


def set_buffer(body):
    print("<ОТПРАВКА ДАННЫХ>", json.dumps(body), flush=True)


def enqueue(name):
    global __queue
    print("<ПОСТАНОВКА В ОЧЕРЕДЬ>", name, flush=True)
    __queue.append(name)
    return True


def call_children(name, data):
    print("<ЗАПУСК ДОЧЕРНЕГО СКРИПТА>", name, json.dumps(data), flush=True)


def unlock_and_get_buffer():
    global __buffer_data
    time.sleep(0.2)
    return __buffer_data


def send_one_order(data):
    return send_orders([data])


def send_orders(orders):
    if __trace_orders:
        print("<ОТПРАВКА ПРИКАЗОВ>", orders)


def debug_psm_json(string):
    global __powerstand_data
    __powerstand_data = json.loads(string)


def debug_psm_file(filename):
    global __powerstand_data
    with open(filename, "r") as fin:
        __powerstand_data = json.load(fin)


def debug_buffer_json(string):
    global __buffer_data
    __buffer_data = json.loads(string)


def debug_buffer_file(filename):
    global __buffer_data
    with open(filename, "r") as fin:
        __buffer_data = json.load(fin)


def debug_launches(value):
    global __launches
    __launches = 99


def debug_timeout(value):
    global __timeout
    __timeout = time.time() + 10
