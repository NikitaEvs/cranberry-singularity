import ips # 1
psm = ips.init()
# 2
clients = psm.powersystem.get_all_clients()
consumption = 0 # прогноз суммарного потребления
generation = 0 # прогноз суммарной генерации
mainAddress = 'M7'


# Try to on all lines
def pray():
    region_1 = psm.powersystem.line(mainAddress, 1)
    region_2 = psm.powersystem.line(mainAddress, 2)
    region_3 = psm.powersystem.line(mainAddress, 3)
    if not region_1.online:
        psm.orders.line_on(mainAddress, 1)
    if not region_2.online:
        psm.orders.line_on(mainAddress, 2)
    if not region_3.online:
        psm.orders.line_on(mainAddress, 3)


# Debug info
def info():
    ips.set_order_trace(True)
    print('***INFO***')
    print('Our index: ')
    print(psm.you)
    print('Our score: ')
    print(psm.score)
    print('Step:')
    print(psm.get_move())
    print('Our lines info:')
    region_1 = psm.powersystem.line(mainAddress, 1)
    region_2 = psm.powersystem.line(mainAddress, 2)
    region_3 = psm.powersystem.line(mainAddress, 3)
    print("Status 1: ", region_1.online)
    print("Status 2: ", region_2.online)
    print("Status 3: ", region_3.online)
    print('All')
    print(psm.humanize())


pray()
info()

for client in clients:
    if client.is_generator():
        generation += client.power[-1]
    else:
        consumption += client.power[-1]
    shortage = consumption - generation
    if shortage > 0:
        psm.orders.trade0.buy(shortage)
    else:
        psm.orders.trade0.sell(-shortage)


