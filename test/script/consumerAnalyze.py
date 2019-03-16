# Important konst #
konst = 1
konst1 = 1

# Script for analyze perfect count of consumers
# Global import
import json

# Global variable
fileName = '../pattern/patternConsumer.json'


# Read pattern for consumers
def read_pattern(_filename):
    with open(_filename) as data:
        pattern = json.load(data)
    return pattern


# Analyze best consumer
def analyze():
    pattern = read_pattern(fileName)
    hospitalPattern = pattern["hospitalPattern"]
    factoryPattern = pattern["factoryPattern"]
    housePattern = pattern["housePattern"]

    # Final values of power
    hospitalVal = 0
    factoryVal = 0
    houseVal = 0

    # Count of choices
    hospitalCount = 0
    factoryCount = 0
    houseCount = 0

    for i in range(len(hospitalPattern)):
        hospitalPower = hospitalPattern[i]*pattern["hospitalCost"]*3
        factoryPower = factoryPattern[i]*pattern["factoryCost"]*2
        housePower = hospitalPattern[i]*pattern["houseCost"]

        if hospitalPower > factoryPower:
            if hospitalPower > housePower:
                hospitalCount += 1
            else:
                houseCount += 1
        else:
            if factoryPower > housePower:
                factoryCount += 1
            else:
                houseCount += 1

        hospitalVal += hospitalPower
        factoryVal += factoryPower
        houseVal += housePower

    print('*** Final power ***')
    print('Hospital: ', hospitalVal)
    print('Factory: ', factoryVal)
    print('House: ', houseVal)
    print('*** Final count ***')
    print('Hospital: ', hospitalCount)
    print('Factory: ', factoryCount)
    print('House: ', hospitalCount)


analyze()
