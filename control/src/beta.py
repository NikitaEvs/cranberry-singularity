# Global import
import ips

# Global variables
mainAddress = 'M7'
systemPower = []  # Power consumption for 10 days


# Debug
ips.debug_psm_file("../common/state.json")

psm = ips.init()


# Make our power system
def make_system():
    print('Make your system:')
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
    print('Shortage:', shortage)
    systemPower.append(shortage)
    # Check exchange
    exchange = psm.exchange
    for agent in exchange:
        if agent.owner == psm.you:
            if agent.issued + agent.exchange == psm.get_move():
                systemPower[0] += -agent.amount
    print('Current system power after exchange:', systemPower[0])
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
    print('Forecast for some days (include current day):')
    for power in systemPower:
        print(power)


# Momentum balance
def safe_game():
    print('Make momentum balance')
    print('Current power:', systemPower[0])
    if systemPower[0] > 0:
        psm.orders.trade0.sell(abs(systemPower[0]))
    else:
        psm.orders.trade0.buy(abs(systemPower[0]))


# Make exchange
def make_exchange():
    print('Make exchange')
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
                print('Make trade for 1 day (sell):', abs(systemPower[day]*sell_for_1_day))
            elif day == 3:
                psm.orders.trade3.sell(abs(systemPower[day]*sell_for_3_day))
                print('Make trade for 3 days (sell):', abs(systemPower[day]*sell_for_3_day))
            elif day == 10:
                psm.orders.trade10.sell(abs(systemPower[day]*sell_for_10_day))
                print('Make trade for 10 day (sell):', abs(systemPower[day]*sell_for_10_day))
        else:
            # Need to buy
            if day == 1:
                psm.orders.trade1.buy(abs(systemPower[day]*buy_for_1_day))
                print('Make trade for 1 day (buy):', abs(systemPower[day]*buy_for_1_day))
            elif day == 3:
                psm.orders.trade3.buy(abs(systemPower[day]*buy_for_3_day))
                print('Make trade for 3 days (buy):', abs(systemPower[day]*sell_for_1_day))
            elif day == 10:
                psm.orders.trade10.buy(abs(systemPower[day]*buy_for_10_day))
                print('Make trade for 10 days (buy):', abs(systemPower[day]*sell_for_1_day))


make_system()
safe_game()
make_exchange()

