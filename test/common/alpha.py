import ips

print("to jest tylko test psa", flush=True)

# получаем структуру для работы
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

generation *= 0.75  # вычитаем 25%
consumption *= 1.25  # накидываем 25%

shortage = consumption - generation
if shortage > 0:
    psm.orders.trade0.buy(shortage)
else:
    psm.orders.trade0.sell(-shortage)
