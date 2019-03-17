# Auction engine

# Global import
import matplotlib.pyplot as plt
from graphviz import Digraph
import json
import csv
import glob
import copy
from load import Load
from player import Player

# Global variable
configFile = '../config/map.json'
path = '../csv/*.csv'
newPath = '../csv/fc9.csv'
playersList = []
with open(configFile) as json_file:
    loads_map = json.load(json_file)


# Parse CSV probability files (Zachem CSV, NTI? Zachem?)
def parse_csv():
    files = glob.glob(path)
    for name in files:
        with open(name) as csv_file:
            line_reader = list(csv.reader(csv_file, delimiter=';'))
            load_address = line_reader[0][0]
            if load_address == 'sun':
                sun_pattern = []
                wind_pattern = []
                line_reader = line_reader[2:]
                for line in line_reader:
                    sun_pattern.append(line[:5])
                    wind_pattern.append(line[5:])
                loads_map['weather']['wind'] = wind_pattern
                loads_map['weather']['sun'] = sun_pattern
            else:
                load_type = loads_map["loadList"][load_address][0]
                load_city = loads_map["loadList"][load_address][1]
                load_pattern = line_reader[2:]
                loads_map[load_type][load_city][load_address] = load_pattern
        with open(configFile, "w") as json_write_file:
            json.dump(loads_map, json_write_file)


# New function for parse CSV probability files (Zachem CSV, NTI? Zachem?)
def parse_csv_new():
    with open(newPath) as csv_file:
        line_reader = list(csv.reader(csv_file, delimiter=','))
        index = 0
        while index < 154:
            # Scan for one consumer
            if index % 5 == 0:
                load_address = line_reader[0][index]
                clear_load_address = ''
                for c in load_address:
                    if c == ':':
                        break
                    elif c != '-':
                        clear_load_address += c
                if clear_load_address == 'sun':
                    sun_pattern = []
                    for i in range(1, len(line_reader)):
                        sun_pattern.append(line_reader[i][index:index + 5])
                    loads_map['weather']['sun'] = sun_pattern
                elif clear_load_address == 'wind':
                    wind_pattern = []
                    for i in range(1, len(line_reader)):
                        wind_pattern.append(line_reader[i][index:index + 5])
                    loads_map['weather']['wind'] = wind_pattern
                else:
                    load_type = loads_map["loadList"][clear_load_address][0]
                    load_city = loads_map["loadList"][clear_load_address][1]
                    load_pattern = []
                    for i in range(1, len(line_reader)):
                        load_pattern.append(line_reader[i][index:index + 5])
                    loads_map[load_type][load_city][clear_load_address] = load_pattern
                index += 1
            index += 1
        with open(configFile, "w") as json_write_file:
            json.dump(loads_map, json_write_file)


# Creating all players
def start_init():
    # Stupid address generation
    for i in range(1, 9):
        addr = 'M' + str(i)
        playersList.append(Player(addr))
    # First graph
    plt.ion()
    plt.show()
    generate_plots()


# Generate all plots for all player
def generate_plots():
    index = 1
    number = 1
    for player in playersList:
        player.update_days_list()
        expenses = []
        profit = []
        consumption = []
        production = []
        for day in player.daysList:
            expenses.append(day.expenses)
            profit.append(day.profit)
            consumption.append(day.consumption)
            production.append(day.production)
        plt.subplot(4, 4, index)
        index += 1
        plt.plot(expenses, label='Expenses '+str(number))
        plt.plot(profit, label='Profit '+str(number))
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        plt.subplot(4, 4, index)
        index += 1
        plt.plot(consumption, label='Consumption '+str(number))
        plt.plot(production, label='Production '+str(number))
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        number += 1

    plt.draw()
    plt.pause(0.1)


# Generate theoretical and current plot for currentPlayer
def generate_current_plot(player_old, player_new):
    player_new.update_days_list()
    player_old.update_days_list()
    expenses_old = []
    profit_old = []
    consumption_old = []
    production_old = []
    expenses_new = []
    profit_new = []
    consumption_new = []
    production_new = []
    for day in player_old.daysList:
        expenses_old.append(day.expenses)
        profit_old.append(day.profit)
        consumption_old.append(day.consumption)
        production_old.append(day.production)
    for day in player_new.daysList:
        expenses_new.append(day.expenses)
        profit_new.append(day.profit)
        consumption_new.append(day.consumption)
        production_new.append(day.production)
    plt.subplot(2, 2, 1)
    plt.plot(expenses_old, label='Expenses old')
    plt.plot(profit_old, label='Profit old')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.subplot(2, 2, 2)
    plt.plot(consumption_old, label='Consumption old')
    plt.plot(production_old, label='Production old')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.subplot(2, 2, 3)
    plt.plot(expenses_new, label='Expenses new')
    plt.plot(profit_new, label='Profit new')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.subplot(2, 2, 4)
    plt.plot(consumption_new, label='Consumption new')
    plt.plot(production_new, label='Production new')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.draw()
    plt.pause(0.1)


# Simulation of auction step by step (loop function)
def simulation():
    step = 0
    print('Start auction ^_^')
    print('Print your command number:')
    current_player = int(input())
    print('Press enter to start simulation')
    input()
    while True:
        print('Step #', step)
        print('Print lot address')
        current_lot = input()
        # Stupid try-catch
        try:
            int(current_lot)
            print('Invalid input')
        except ValueError:
            if current_lot == 'oh':
                break
            print('Print desired cost')
            try:
                current_cost_str = input()
                if current_cost_str != 'oh':
                    current_cost = float(current_cost_str)
                    player_old = copy.deepcopy(playersList[current_player - 1])
                    player_new = copy.deepcopy(playersList[current_player - 1])
                    player_new.loadList.append(Load(current_lot, current_cost))
                    generate_current_plot(player_old, player_new)
                    print('Theoretical/real plots on screen')
                else:
                    # FIXME It's really necessary to generate new useless plots for working from console
                    player_old = copy.deepcopy(playersList[current_player - 1])
                    generate_current_plot(player_old, player_old)
                print('Print customer number')
                customer = int(input())
                print('Print real price')
                price = float(input())
                playersList[customer - 1].loadList.append(Load(current_lot, price))
                print('All real plots on screen')
                generate_plots()
                step += 1
            except ValueError:
                print('Invalid input')
    our_player = playersList[current_player-1]
    our_player.serialize()
    schema = [[], [], []]
    schema_power = [0.0, 0.0, 0.0]
    print('YOUR LOAD LIST')
    for load in our_player.loadList:
        print('Load type:', load.type, 'load address:', load.address, 'load max power', load.max_power)
        # TODO arrr. It's not error because we have new rule for hospital
        if load.type == 'hospitals':
            new_power_0 = schema_power[0] + load.max_power/2
            new_power_1 = schema_power[1] + load.max_power/2
            new_power_2 = schema_power[2] + load.max_power/2
            if new_power_0 < 35 and new_power_1 < 20:
                schema[0].append(load)
                schema_power[0] += load.max_power/2
            elif new_power_1 < 35 and new_power_2 < 20:
                schema[1].append(load)
                schema_power[1] += load.max_power/2
            elif new_power_0 < 35 and new_power_2 < 20:
                schema[2].append(load)
                schema_power[2] += load.max_power/2
            else:
                max_power = max(new_power_0, new_power_1, new_power_2)
                if max_power == new_power_0:
                    schema[1].append(load)
                    schema_power[1] += load.max_power/2
                    schema[2].append(load)
                    schema_power[2] += load.max_power/2
                elif max_power == new_power_1:
                    schema[0].append(load)
                    schema_power[0] += load.max_power/2
                    schema[2].append(load)
                    schema_power[2] += load.max_power/2
                else:
                    schema[0].append(load)
                    schema_power[0] += load.max_power/2
                    schema[1].append(load)
                    schema_power[1] += load.max_power/2
                print('Big problem with balance, idiots')
        else:
            new_power_0 = schema_power[0] + load.max_power
            new_power_1 = schema_power[1] + load.max_power
            new_power_2 = schema_power[2] + load.max_power
            if new_power_0 < 20:
                schema[0].append(load)
                schema_power[0] += load.max_power
            elif new_power_1 < 20:
                schema[1].append(load)
                schema_power[1] += load.max_power
            elif new_power_2 < 20:
                schema[2].append(load)
                schema_power[2] += load.max_power
            else:
                min_power = min(new_power_0, new_power_1, new_power_2)
                print('Big problem with balance, idiots: ', min_power)
                if min_power == new_power_0:
                    schema[0].append(load)
                    schema_power[0] += load.max_power
                elif min_power == new_power_1:
                    schema[1].append(load)
                    schema_power[1] += load.max_power
                else:
                    schema[2].append(load)
                    schema_power[2] += load.max_power

    print('Schema example:')
    dot = Digraph(comment='The Round Table ')
    dot.node('main', 'Main station')
    for line in schema:
        print('New line:')
        if len(line) > 0:
            last_client = line[0]
            dot.node(last_client.address, last_client.type + ' ' + last_client.address)
            dot.edge('main', last_client.address, constraint='false')
            print(last_client.type, last_client.address)
            for i in range(1, len(line)):
                print(line[i].type, line[i].address)
                dot.node(line[i].address, line[i].type + ' ' + line[i].address)
                dot.edge(last_client.address, line[i].address, constraint='false')
                last_client = line[i]
    dot.render('../graph/auction.gv', view=True)



parse_csv_new()
start_init()
simulation()
input()
