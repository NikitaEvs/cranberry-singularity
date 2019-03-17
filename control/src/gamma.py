# Global import
import ips

# Global variables
mainAddress = 'M7'
systemPower = []  # Power consumption for 10 days
countOfStep = 50


# Debug
# ips.debug_psm_file("../common/state.json")

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
                shortage += agent.amount
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
    sell_for_10_day = 0.9
    buy_for_10_day = 0.9
    sell_for_1_day = 1.0
    buy_for_1_day = 1.0
    power = 0
    power_1 = 0
    clients = psm.powersystem.get_all_clients()
    day = psm.get_move() + 10
    day_1 = psm.get_move() + 1
    for client in clients:
        if client.addr[0][0] == 's':
            forecast = psm.sun[day].forecast.median
            forecast_1 = psm.sun[day_1].forecast.median
            power += forecast
            power_1 += forecast_1
        elif client.addr[0][0] == 'a':
            forecast = psm.wind[day].forecast.median
            forecast_1 = psm.wind[day_1].forecast.median
            power += forecast
            power_1 += forecast_1
        else:
            forecast = client.preset[day].median
            forecast_1 = client.preset[day_1].median
            power -= forecast
            power_1 -= forecast_1
    if power > 0:
        # Need to sell
        psm.orders.trade10.sell(abs(power))
        print('Make stupid long exchange (sell)', abs(power)*sell_for_10_day)
    elif power < 0:
        # Need to buy
        psm.orders.trade10.buy(abs(power))
        print('Make stupid long exchange (buy)', abs(power)*buy_for_10_day)
    if power_1 > 0:
        # Need to sell
        psm.orders.trade1.sell(abs(power_1))
        print('Make stupid long exchange (sell)', abs(power_1)*sell_for_1_day)
    elif power_1 < 0:
        # Need to buy
        psm.orders.trade1.buy(abs(power_1))
        print('Make stupid long exchange (buy)', abs(power)*buy_for_1_day)


stupid_safe_game()
stupid()
