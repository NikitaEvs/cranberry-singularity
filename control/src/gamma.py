# Global import
import ips

# Global variables
mainAddress = 'M7'
systemPower = []  # Power consumption for 10 days


# Debug
ips.debug_psm_file("../common/state.json")

psm = ips.init()


# Stupid safe game
def stupid_safe_game():
    print('Make stupid exchange')
    clients = psm.powersystem.get_all_clients()
    generation = 0
    consumption = 0
    for client in clients:
        if client.is_generator():
            generation += client.power[-1]
        else:
            consumption += client.power[-1]
    shortage = generation - consumption
    exchange = psm.exchange
    for agent in exchange:
        if agent.owner == psm.you:
            if agent.issued + agent.exchange == psm.get_move():
                shortage += -agent.amount
    if shortage > 0:
        # Need to sell
        psm.orders.trade0.sell(abs(shortage))
        print('Make stupid fast exchange (sell)', abs(shortage))
    else:
        # Need to buy
        psm.orders.trade0.buy(abs(shortage))
        print('Make stupid fast exchange (buy)', abs(shortage))


# Stupid function
def stupid():
    power = 0
    clients = psm.powersystem.get_all_clients()
    day = psm.get_move() + 10
    for client in clients:
        if client.addr[0][0] == 's':
            forecast = psm.sun[day].forecast.median
            power += forecast
        elif client.addr[0][0] == 'a':
            forecast = psm.wind[day].forecast.median
            power += forecast
        else:
            forecast = client.preset[day].median
            power -= forecast
    if power > 0:
        # Need to sell
        psm.orders.trade10.sell(abs(power))
        print('Make stupid long exchange (sell)', abs(power))
    else:
        # Need to buy
        psm.orders.trade10.buy(abs(power))
        print('Make stupid long exchange (buy)', abs(power))


stupid_safe_game()
stupid()
