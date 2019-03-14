import ips

ips.debug_psm_file("../common/state.json")
psm = ips.init()

clients = psm.powersystem.get_all_clients()
consumption = 0  # прогноз суммарного потребленияш
generation = 0  # прогноз суммарной генерации

for client in clients:
    # помним, что все значения у клиентов положительные
    # нужно различать потребление и генерацию
    if client.is_generator():
        generation += client.power[-1] if client.power else 0
    else:
        consumption += client.power[-1] if client.power else 0

