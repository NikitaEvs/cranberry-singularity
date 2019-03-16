# Global import
import ips

# Global variables
mainAddress = 'M7'
systemPower = []  # Power consumption for 10 days


# Debug
ips.debug_psm_file("../common/state.json")

psm = ips.init()


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


# Momentum balance
def safe_game():
    if systemPower[0] > 0:
        psm.orders.trade0.sell(abs(systemPower[0]))
    else:
        psm.orders.trade0.buy(abs(systemPower[0]))


# Stupid safe game
def stupid_safe_game():
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
    else:
        # Need to buy
        psm.orders.trade0.buy(abs(shortage))


# Make our power system
def make_system():
    # Momentum info
    # Power production and consumption
    clients = psm.powersystem.get_all_clients()
    generation = 0
    consumption = 0
    for client in clients:
        if client.is_generator():
            generation += client.power[-1]
        else:
            consumption += client.power[-1]
    shortage = generation - consumption
    systemPower.append(shortage)
    # Check exchange
    exchange = psm.exchange
    for agent in exchange:
        if agent.owner == psm.you:
            if agent.issued + agent.exchange == psm.get_move():
                systemPower[0] += -agent.amount
    # Forecast
    for day in range(psm.get_move() + 1, psm.get_move() + 10):
        power = 0
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
        # Check exchange
        for agent in exchange:
            if agent.owner == psm.you:
                if agent.issued + agent.exchange == day:
                    power -= agent.amount
        systemPower.append(power)


# Make exchange
def make_exchange():
    sell_for_1_day = 0.9
    sell_for_3_day = 0.8
    sell_for_10_day = 0.7
    buy_for_1_day = 0.9
    buy_for_3_day = 0.8
    buy_for_10_day = 0.7
    for day in range(1, 10):
        if systemPower[day] > 0:
            # Need to sell
            if day == 1:
                psm.orders.trade1.sell(abs(systemPower[day]*sell_for_1_day))
            elif day == 3:
                psm.orders.trade3.sell(abs(systemPower[day]*sell_for_3_day))
            elif day == 10:
                psm.orders.trade10.sell(abs(systemPower[day]*sell_for_10_day))
        else:
            # Need to buy
            if day == 1:
                psm.orders.trade1.buy(abs(systemPower[day]*buy_for_1_day))
            elif day == 3:
                psm.orders.trade3.buy(abs(systemPower[day]*buy_for_3_day))
            elif day == 10:
                psm.orders.trade10.buy(abs(systemPower[day]*buy_for_10_day))


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
    else:
        # Need to buy
        psm.orders.trade10.buy(abs(power))


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
        else:
            psm.orders.trade0.sell(-shortage)


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
# info()
make_system()
safe_game()
make_exchange()

# Stupid game
# pray()
# stupid_safe_game()
# stupid()

# Very stupid game
# pray()
# very_stupid()
