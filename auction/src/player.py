# Player main class

# Global import
from day import Day
from load import Load
import json


# Main values:
# 1) MainStation address
# 2) Loads list
# 3) Days list (with expenses, profit, consumption, production)
class Player(object):
    configFile = '../config/map.json'
    playerFile = '../../control/common/player.json'
    daysList = []
    # TODO Set right values
    commonHouseProfit = 5
    commonSolarCost = 10
    commonExchangeCost = 3

    def __init__(self, address):
        self.address = address
        self.loadList = []
        with open(self.configFile) as data:
            map = json.load(data)
        common_house_address = map['mainStation'][address]['house']
        common_solar_address = map['mainStation'][address]['solar']
        self.loadList.append(Load(common_house_address, self.commonHouseProfit))
        self.loadList.append(Load(common_solar_address, self.commonSolarCost))

    def update_days_list(self):
        self.daysList = []
        # Get days count
        for i in range(len(self.loadList[0].pattern)):
            expenses = 0
            profit = 0
            consumption = 0
            production = 0
            for load in self.loadList:
                pattern = load.pattern
                # TODO Something smart (stupid median right now)
                if load.type == 'solar' or load.type == 'windgen':
                    production += float(pattern[i][2])
                    expenses += load.money
                else:
                    consumption += float(pattern[i][2])
                    profit += load.money*float(pattern[i][2])
            # TODO Set exchange cost?
            if production > consumption:
                profit += (production - consumption)*self.commonExchangeCost
            else:
                expenses += (consumption - production)*self.commonExchangeCost
            self.daysList.append(Day(expenses, profit, consumption, production))

    def serialize(self):
        with open(self.playerFile, "w") as json_write_file:
            json.dump(self.to_json(), json_write_file)

    def to_json(self):
        return json.dumps(self, default=vars, sort_keys=True, indent=4)
