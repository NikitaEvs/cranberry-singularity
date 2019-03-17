# Global import
import ips

# Global variables
mainAddress = 'M7'
systemPower = []  # Power consumption for 10 days
countOfStep = 50


# Debug
# ips.debug_psm_file("../common/state.json")

psm = ips.init()


# Try to on all lines
def pray():
    region_1 = psm.powersystem.line(mainAddress, 1)
    region_2 = psm.powersystem.line(mainAddress, 2)
    region_3 = psm.powersystem.line(mainAddress, 3)
    if not region_1.online:
        print('***LINE 1 DIED***')
        psm.orders.line_on(mainAddress, 1)
        print('Turn on')
    if not region_2.online:
        print('***LINE 2 DIED***')
        psm.orders.line_on(mainAddress, 2)
        print('Turn on')
    if not region_3.online:
        print('***LINE 3 DIED***')
        psm.orders.line_on(mainAddress, 3)
        print('Turn on')


# Momentum balance
def safe_game():
    print('Make momentum balance')
    print('Current diff:', systemPower[0])
    if systemPower[0] > 0:
        new_power = cell(systemPower[0])
        print('Power diff after cell:', new_power)
        psm.orders.trade0.sell(abs(new_power))
    elif systemPower[0] < 0:
        new_power = cell(systemPower[0])
        print('Power diff after cell:', new_power)
        psm.orders.trade0.buy(abs(new_power))


# Use cell for balance
def cell(power):
    print('One step balance with cell')
    if power > 0:
        print('Charge cell')
        available_cell_power = 25 - psm.stations[mainAddress].charge
        print('Available cell power:', available_cell_power)
        if available_cell_power > 0:
            power_to_cell = max(5, power)
            psm.orders.cell_charge(mainAddress, power_to_cell)
            print('Power to cell:', power_to_cell)
            return power - power_to_cell
    elif power < 0:
        print('Use cell')
        print('Cell power:', psm.stations[mainAddress].charge)
        if psm.stations[mainAddress].charge > 0:
            power_from_cell = min(psm.stations[mainAddress].charge, abs(power))
            psm.orders.cell_discharge(mainAddress, power_from_cell)
            print('Power from cell:', power_from_cell)
            return power + power_from_cell
    else:
        return 0


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
            print('Agent info:')
            print('Agent issued:', agent.issued)
            print('Agent exchange:', agent.exchange)
            print('Current move:', psm.get_move())
            if agent.issued + agent.exchange == psm.get_move():
                systemPower[0] += agent.amount
    print('Current system power after exchange:', systemPower[0])
    # Forecast
    for day in range(psm.get_move() + 1, psm.get_move() + 11):
        if day < countOfStep:
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
                    print('Agent info:')
                    print('Agent issued:', agent.issued)
                    print('Agent exchange:', agent.exchange)
                    print('Current move:', psm.get_move())
                    if agent.issued + agent.exchange == day:
                        power += agent.amount
            systemPower.append(power)
    print('Forecast for some days (include current day):')
    for power in systemPower:
        print(power)


# Make exchange
def make_exchange():
    print('Make exchange')
    sell_for_1_day = 1.0
    sell_for_3_day = 0.8
    sell_for_10_day = 0.7
    buy_for_1_day = 1.0
    buy_for_3_day = 0.8
    buy_for_10_day = 0.7
    for day in range(1, 11):
        if psm.get_move() + day < countOfStep:
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
            elif systemPower[day] < 0:
                # Need to buy
                if day == 1:
                    psm.orders.trade1.buy(abs(systemPower[day]*buy_for_1_day))
                    print('Make trade for 1 day (buy):', abs(systemPower[day]*buy_for_1_day))
                elif day == 3:
                    psm.orders.trade3.buy(abs(systemPower[day]*buy_for_3_day))
                    print('Make trade for 3 days (buy):', abs(systemPower[day]*buy_for_3_day))
                elif day == 10:
                    psm.orders.trade10.buy(abs(systemPower[day]*buy_for_10_day))
                    print('Make trade for 10 days (buy):', abs(systemPower[day]*buy_for_10_day))


# Stupid function
def stupid():
    sell_for_10_day = 0.9
    buy_for_10_day = 0.9
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
        print('Make stupid long exchange (sell)', abs(power)*sell_for_10_day)
    else:
        # Need to buy
        psm.orders.trade10.buy(abs(power))
        print('Make stupid long exchange (buy)', abs(power)*buy_for_10_day)


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


# pray()
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
