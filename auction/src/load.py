# Load main class

# Global import
import json


# Main values:
# 1) address
# 2) type (house, hospital, solar, factory, windgen)
# 3) pattern (real pattern)
# 4) city (Irkutsk, Moscow, Our)
# 5) money (for solar and windgen - cost, for other - profit)
class Load(object):
    configFile = '../config/map.json'

    # Init main values and read pattern
    def __init__(self, address, money):
        self.address = address
        with open(self.configFile) as data:
            patterns = json.load(data)
        self.type = patterns['loadList'][address][0]
        self.city = patterns['loadList'][address][1]
        self.money = money
        if self.type != 'solar' and self.type != 'windgen':
            self.pattern = patterns[self.type][self.city][address]
        elif self.type == 'solar':
            self.pattern = patterns['weather']['sun']
        else:
            self.pattern = patterns['weather']['wind']
        self.max_power = 0
        for line in self.pattern:
            if float(line[2]) > self.max_power:
                self.max_power = float(line[2])

