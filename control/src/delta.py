# Global import
import ips

# Global variables
mainAddress = 'M7'
systemPower = []  # Power consumption for 10 days
countOfStep = 50


# Debug
# ips.debug_psm_file("../common/state.json")

psm = ips.init()


# Very stupid function
def very_stupid():
    consumption = 0
    generation = 0
    clients = psm.powersystem.get_all_clients()
    for client in clients:
        if client.is_generator():
            generation += client.power[-1]
        else:
            consumption += client.power[-1]
        shortage = consumption - generation
        if shortage > 0:
            psm.orders.trade0.buy(shortage)
            print('Very stupid buy', shortage)
        else:
            psm.orders.trade0.sell(-shortage)
            print('Very stupid sell', -shortage)


very_stupid()
