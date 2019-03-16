# Global import
import ips

# Global variables
mainAddress = 'M7'


# Debug
ips.debug_psm_file("../common/state.json")

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


pray()
