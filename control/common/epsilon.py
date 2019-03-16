import ips
ips.set_order_trace(True)

psm = ips.init()
psm.orders_lazy.line_on("m0", 1).send()
launches = ips.get_launches("blinker")
if launches > 95:
    psm.orders.trade0.buy(5)
    ips.enqueue("blinker")
