# Справка по системе управления скриптами

## Краткий принцип работы

1. Есть система управления скриптами (далее СУС).
2. СУС имеет именованные слоты для хранения **управляющих скриптов**.
3. Скрипт пишется на языке Python версии 3.6 и, помимо стандартных, использует специальную библиотеку для энергостенда.
4. Есть **назначенная очередь выполнения**, указывающая, какие скрипты и в каком порядке должны выполняться в ближайший ход.
5. В начале каждого хода помеченные на запуск скрипты перемещаются в **текущую очередь** 
и выполняются по порядку до тех пор, как очередь не закончится.
6. Скрипт может **получить данные со стенда на текущий ход и отправлять на него управляющие приказы**.
   Это основная задача управляющего скрипта и СУС в целом.
7. Скрипт может **ставить в очередь** другой скрипт (по его имени). Он выполнится после всех остальных.
8. Скрипт может **запускать** другой **как дочерний**, передавая ему на вход произвольные данные в JSON. 
   При этом родительский скрипт блокируется до завершения всех дочерних. 
   Дочерний скрипт может вернуть данные в JSON, они передаются в родительский после разблокировки. 
9. **Количество выполнений** для каждого скрипта **ограничено** в течение хода и равно **100**. 
   Запуск скрипта с синтаксической ошибкой также уменьшает счётчик.
10. **Общее время выполнения всех скриптов ограничено** глобальным таймаутом.
   При его достижении все запущенные скрипты «убиваются», а дальнейший запуск запрещается до начала нового хода.  
11. Количество вложенных дочерних скриптов тоже ограничено и равно **100**. 
    Но из-за пункта 9 это не будет проблемой.
12. Скрипт может узнать текущую очередь, количество оставшихся выполнений для любого скрипта и момент глобального таймаута (штамп времени).   


## Базовый пример

```python
import ips  # 1
psm = ips.init()  # 2

clients = psm.powersystem.get_all_clients()  # 3
consumption = 0  # прогноз суммарного потребления
generation = 0  # прогноз суммарной генерации

for client in clients:
    if client.is_generator():
        generation += client.power[-1]
    else:
        consumption += client.power[-1]

shortage = consumption - generation
if shortage > 0:
    psm.orders.trade0.buy(shortage)  # 4
else:
    psm.orders.trade0.sell(-shortage)  # 4
```

1. Импорт библиотеки API стенда.
2. Запрос на сервер и создание объекта с данными системы на текущий ход. 
3. Данные извлекаются путём вызова методов и функций, см. далее.
4. Вызываемые приказы сразу же отправляются на сервер и отражаются в интерфейсе.

## Получение данных

### Прежде всего:

```python
import ips        # импортируем библиотеку

# при работе с тестовой версией нужно задать данные вручную
# например, из файла (другие способы будут ниже)
ips.debug_psm_file("state.json") 
# убедитесь, что файл лежит рядом со скриптом

psm = ips.init()  # читаем состояние энергостенда в объект

# и продолжаем работать
```

### Погода

```python
# их структура одинакова и представляет собой список,
# каждый элемент которого соответствует своему ходу 
print(psm.sun)   # значения яркости солнца
print(psm.wind)  # значения скорости ветра

# элемент состоит из двух полей: 
# - реальное значение, которое может быть пусто (ход не наступил)
# - прогноз в виде процентилей

print(psm.wind[0])          # объект-пара для ветра за первый ход
print(psm.wind[0].value)    # либо реальное значение, либо None 
print(psm.wind[0].forecast) # прогноз в виде набора процентилей

# актуальное значение погоды берётся по номеру хода
# для извлечения номера хода можно использовать это: 
tick = psm.get_move()

# рассмотрим поля для отдельного взятого прогноза 
q = psm.wind[tick].forecast
print(q.lower0)  # 0%
print(q.lower50) # 25%
print(q.median)  # 50%
print(q.upper50) # 75%
print(q.upper0)  # 100%

# вспомогательные кортежи с парами значений
print(q.quart1)    # Q1 (0%, 25%)
print(q.quart2)    # Q2 (25%, 50%)
print(q.quart3)    # Q3 (50%, 75%)
print(q.quart4)    # Q4 (75%, 100%)
print(q.spread)    # (0%, 100%)
print(q.spread50)  # (25%, 75%)
```

### Биржа

```python
print(psm.exchange)     # все предложения на всех биржах 
print(psm.exchange[0])  # конкретное предложение 

# для отдельно взятого предложения
print(psm.exchange[0].exchange) # тип биржи (через сколько ходов)
print(psm.exchange[0].amount)   # объём заявки
print(psm.exchange[0].issued)   # номер хода, на котором она создано
print(psm.exchange[0].owner)    # контрагент 
```

### Подстанции

```python
print(psm.stations)  # все подстанции в виде dict
print(list(psm.stations.keys()))  # адреса подстанций

# возьмём главную подстанцию М0 (у вас будет другой адрес)
print(psm.stations["M0"])              # объект главной подстанции
print(psm.stations["M0"].addr)         # адрес
print(psm.stations["M0"].cells)        # кол-во аккумуляторов
print(psm.stations["M0"].transformers) # кол-во трансформаторов
print(psm.stations["M0"].charge)       # общий заряд аккумуляторов 
print(psm.stations["M0"].modules)      # список модулей как объектов

print(psm.stations["M0"].modules[0].is_cell) # проверка типа модуля

# для аккумулятора можно получить 
# динамический список со значениями заряда за этот и предыдущие ходы
print(psm.stations["M0"].modules[0].charge) 
# аналогичный формат значений используется и ниже

# ВНИМАНИЕ! значение за последний ход — конец списка (charge[-1])
# в начале игры некоторые дин. списки пусты, это эквивалент нуля 

# возьмём произвольную миниподстанцию m5 (у вас их может и не быть)
print(psm.stations["m5"])       # миниподстанция 
print(psm.stations["m5"].addr)  # адрес миниподстанции
```

### Энергосеть

```python
print(psm.powersystem)                    # объект энергосети  

print(psm.powersystem.get_all_lines())    # извлечь все имеющиеся линии  
print(psm.powersystem.get_all_clients())  # всех имеющихся клиентов
print(psm.powersystem.get_all_regions())  # все имеющиеся энергорайоны

print(psm.powersystem.line("M0", 1))   # энергорайон на первой линии M0
# в системе линия представлена парой (адрес_подстанции, номер)

print(psm.powersystem.lines())         # получить все энергорайоны 
key_list = [("M0", 1), ("M0", 2)]
print(psm.powersystem.lines(key_list)) # энергорайоны по ключам в списке
# эти две функции возвращают массив пар линия-район 

# возьмём отдельный энергорайон
region = psm.powersystem.line("M0", 1)  
print(region.get_all_lines())    # аналогичны функциям выше, но выдаются
print(region.get_all_clients())  # элементы из себя и соседних районов
print(region.get_all_regions())  # 
print(region.online)   # 
print(region.lines)    # линии к соседним энергорайонам (список)
print(region.clients)  # клиенты в данном энергорайоне (список)

# возьмём отдельного клиента
client = region.clients[0]
print(client.is_consumer())   # ответ на вопрос "это потребитель?"
print(client.is_generator())  # или "это генератор?"
print(client.addr)            # адрес объекта
print(client.contract)        # тариф по контракту
print(client.profits)         # доход за каждый ход (дин. список)
print(client.losses)          # расход за каждый ход (дин. список)
print(client.power)           # текущая мощность (дин. список)
                              # она же реальное потребление-генерация
print(client.influence)       # влияние на объект (дин. список)
# если клиент — потребитель
print(client.preset)  # список значений и прогнозов аналогично погоде
# это необходимо в основном для работы с прогнозами, 
# для чтения текущих значений удобнее применять power 
```

### Прочая информация

```python
print(psm.you)  # ваш индекс игрока, пара чисел стенд-терминал
                # не путать с адресом своей подстанции!

print(psm.score)  # счёт на текущий момент (динамческий список)

print(psm.get_move())  # определить номер текущего хода (первый ход = 1) 

print(psm.humanize())  # полное описание состояния стенда (отладка)
```

## Приказы

Существуют в двух форматах:

 * `psm.orders` — строгие приказы, отправляются сразу
 * `psm.orders_lazy` — ленивые приказы, сохраняются в виде просматриваемого объекта

Есть два способа отправки ленивых приказов:

 * `lazy_order.send()` (вызов метода от объекта приказа)
 * `ips.send_orders([order1, order2])` (пакетная отправка нескольких приказов)

<u>**Приказы обрабатываются в порядке их отправки в систему!**</u>

<u>**Все приказы на биржу учитываются и применяются отдельно!**</u>

<u>**Для остальных приказов приоритет — у последнего вызванного!**</u>

```python
### Линии (выполняется последний отправленный)
psm.orders.line_on("M0", 1)   # включение линии 1 подстанции M0
psm.orders.line_off("M0", 1)  # выключение этой же линии

print(psm.orders_lazy.line_on("M0", 1).addr)   # адрес подстанции
print(psm.orders_lazy.line_on("M0", 1).line)   # линия
print(psm.orders_lazy.line_on("M0", 1).value)  # устанавливаемое значение

#### Биржа (накапливается)
psm.orders.trade1.buy(5)   # купить 5 МВт-ч на следующий ход
psm.orders.trade1.sell(5)  # продать 5 МВт-ч на следующий ход

psm.orders_lazy.trade3.buy(5)   # ... через 3 хода
psm.orders_lazy.trade10.buy(5)  # ... через 10 ходов

print(psm.orders_lazy.trade0.buy(5).exchange)  # тип биржи (число ходов)
print(psm.orders_lazy.trade0.buy(5).value)     # объём купли-продажи

### Аккумуляторы (выполняется последний отправленный)
# В качестве адреса указывается адрес подстанции!
psm.orders.cell_charge("M0", 1)    # зарядить на 1 МВт-ч
psm.orders.cell_discharge("M0", 1) # разрядить на 1 МВт-ч

print(psm.orders_lazy.cell_charge("M0", 1).addr)   # адрес
print(psm.orders_lazy.cell_charge("M0", 1).power)  # мощность

### Влияние на объекты (выполняется последний отправленный)
# В качестве адреса указывается адрес объекта!
psm.orders.influence("h0", 1)  # установить влияние на h0 в значение 1

print(psm.orders_lazy.influence("h0", 1).addr)   # адрес объекта
print(psm.orders_lazy.influence("h0", 1).value)  # значение
```

## Запуск других скриптов

Есть два способа вызвать другой скрипт (или самого себя).

Команда `enqueue` добавляет скрипт в конец очереди, т.е.
он будет выполнен после завершения остальных скриптов. 

```python
ips.enqueue("eta")   
```

Также можно выполнять скрипты как функции с входными и выходными данными:

```python
####### РОДИТЕЛЬСКИЙ СКРИПТ #######

# Пусть у нас есть набор данных для передачи.
data = ["horse", "chair", 28] 

# В дочерний скрипт передаётся data,
# скрипт блокируется до завершения дочернего.
# Вывод дочернего скрипта запишется в output
output = ips.call("beta", data) 
 
####### ДОЧЕРНИЙ СКРИПТ #######
 
# Чтобы записать выходные данные, в дочернем скрипте пишется команда: 
ips.exit_with(["horse", "chair", 28])
# После её выполнения скрипт завершится, вернув управление родителю. 
```

## Вспомогательные команды

```python
ips.send_orders(lazy_order_list) # массовая отправка ленивых приказов 

ips.get_launches("alpha")  # получить число оставшихся запусков для скрипта
ips.get_timeout()  # получить UNIX-timestamp полного завершения выполнения
ips.get_queue()  # получить текущую очередь выполнения

ips.set_order_trace(True)  # включить/выключить вывод приказов в консоль
```

## Отладка

В целях упрощения отладки представлены функции для установки заглушек.
Они работают исключительно в тестовой версии фреймворка, при выполнении в СУС данные 
вызовы лишь пишут предупреждение в поток ошибок и пропускаются.

```python
# установка данных энергостенда, перед ips.init()
ips.debug_psm_file("state.json")  # из файла
ips.debug_psm_file("<...>")       # из строкового объекта

# установка входных данных, перед ips.buffer()
ips.debug_buffer_file("buffer.json")  # аналогично
ips.debug_buffer_json("<...>")        #

ips.debug_launches(99)  # число запусков для get_launches
ips.debug_timeout(time.time() + 10)  # таймстамп для get_timeout 

# О, привет. Раз уж ты здесь, рекомендую почитать исходники библиотеки. 
# В них есть полезные вещи для боевого применения и, возможно, ошибки.
# Найдёшь последние — дай знать преподавателям, они передадут.
```

