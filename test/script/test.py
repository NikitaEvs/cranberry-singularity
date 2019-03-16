import ips

ips.debug_psm_file("../common/state.json")
psm = ips.init()

print(len(psm.sun))

for i in psm.sun:
    print(i.forecast.upper0)

