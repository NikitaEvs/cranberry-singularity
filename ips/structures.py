from collections import namedtuple

from ips import internals
from ips.utils import warn_tb

# FIXME: s/addr/address/g
# FIXME: profits, losses, power, influence are lists!

def try_str(value):
    if not isinstance(value, str):
        raise TypeError("Type " + value.__class__.__name__ +
                        " is not a string.")
    return value


def try_float(value):
    try:
        return float(value)
    except TypeError:
        raise TypeError("Type " + value.__class__.__name__ +
                        " is not float-compatible.")


def try_float_posi(value):
    v = try_float(value)
    if v < 0:
        raise TypeError("Non-positive number in an order.")
    return v


def simple_line(data):
    return data["host"], data["number"]


def short_fv(w):
    if w.value is None:
        return "? " + repr(w.forecast)
    else:
        return "= " + str(w.value)


def safe_last(l):
    if not l:
        return 0
    return l[-1]


class Quartile(namedtuple("Quartile", "lower0 lower50 median upper50 upper0")):
    """Описание вероятностного распределения в квартилях."""

    @staticmethod
    def from_json(data):
        return Quartile(data[3], data[1], data[0], data[2], data[4])
        # data["lower0"], data["lower50"], data["median"], data["upper50"], data["upper0"])

    @property
    def spread(self):
        return self[0], self[4]

    @property
    def spread50(self):
        return self[1], self[3]

    @property
    def quart1(self):
        return self[0], self[1]

    @property
    def quart2(self):
        return self[1], self[2]

    @property
    def quart3(self):
        return self[2], self[3]

    @property
    def quart4(self):
        return self[3], self[4]

    def __repr__(self):
        return "{} {}".format(self.median, self.spread)


class Player:
    @staticmethod
    def decode(value):
        x = tuple(value)
        if not (0 <= x[0] <= 1):
            raise TypeError("Некорректный входной индекс игрока (стенд)")
        if not (0 <= x[1] <= 3):
            raise TypeError("Некорректный входной индекс игрока (идентификатор)")
        return x


class Line:
    @staticmethod
    def encode(value):
        if not isinstance(value, int):
            raise TypeError("Incorrect line number type")
        if value == 0:
           raise TypeError("Line 0 is service-only")
        if not (1 <= value <= 3):
            raise TypeError("Incorrect line number value")
        return value

    @staticmethod
    def decode(value):
        if not (0 <= value <= 3):
            raise TypeError("Incorrect line number")
        return value


class Exchange:
    encode_values = {0: 0, 1: 1, 3: 2, 10: 3}
    decode_values = {0: 0, 1: 1, 2: 3, 3: 10}

    @staticmethod
    def encode(value):
        if not isinstance(value, int):
            raise TypeError("Incorrect exchange type")
        out = Exchange.encode_values.get(value, None)
        if out is None:
            raise TypeError("Incorrect exchange value")
        return out

    @staticmethod
    def decode(value):
        if not (0 <= value <= 3):
            raise TypeError("Некорректный входной индекс биржи")
        return Exchange.decode_values[value]


class Order:
    def __init__(self, data):
        self.__data = data

    def send(self):
        return internals.send_one_order(self)

    @property
    def data(self):
        return self.__data

    def __repr__(self):
        return f"<unknown order {self.data}>"


class CellOrder(Order):

    def __init__(self, addr, power):
        super().__init__({"type": "Cell", "target": try_str(addr),
                          "amount": try_float(power)})
        self.addr = addr
        self.power = power

    def __repr__(self):
        return f"<cell order, address {self.addr}, delta {self.power} MWh>"


class InfluenceOrder(Order):

    def __init__(self, addr, value):
        super().__init__({"type": "Influence", "target": try_str(addr),
                          "amount": try_float_posi(value)})
        self.addr = addr
        self.value = value

    def __repr__(self):
        return f"<influence order, address {self.addr}, amount {self.value}>"


class LineOrder(Order):

    def __init__(self, addr, line, value):
        super().__init__({"type": "Line", "target": try_str(addr),
                          "line": Line.encode(line), "state": bool(value)})
        self.addr = addr
        self.line = line
        self.value = value

    def __repr__(self):
        state = "turn on" if self.value else "turn off"
        return f"<line order, address {self.addr}, line {self.line}, {state}>"


class TradeOrder(Order):

    def __init__(self, exchange, value):
        super().__init__({"type": "Trade", "exchange": Exchange.encode(exchange), "amount": try_float(value)})
        self.exchange = exchange
        self.value = value

    def __repr__(self):
        return f"<exchange order, {self.value} MWh in {self.exchange} move(s)>"


class TradeOrderFactory:

    MAX_AMOUNT = 45

    def __init__(self, exchange, lazy):
        self.__exchange = exchange
        self.__lazy = lazy

    def __send(self, order):
        return order if self.__lazy else order.send()

    def buy(self, amount):
        amount = try_float_posi(amount)
        if amount > TradeOrderFactory.MAX_AMOUNT:
            warn_tb(f"Request for power value more than {self.MAX_AMOUNT} MWh. Ignoring...", cut=None)
            return
        return self.__send(TradeOrder(self.__exchange, amount))

    def sell(self, amount):
        amount = try_float_posi(amount)
        if amount > TradeOrderFactory.MAX_AMOUNT:
            warn_tb(f"Request for power value more than {self.MAX_AMOUNT} MWh. Ignoring...", cut=None)
            return
        return self.__send(TradeOrder(self.__exchange, -amount))

    def contract(self, amount):
        # поздравляем, вы только что открыли антисахар на биржу
        amount = try_float(amount)
        if abs(amount) > TradeOrderFactory.MAX_AMOUNT:
            warn_tb(f"Request for power value more than {self.MAX_AMOUNT} MWh. Ignoring...", cut=None)
            return
        return self.__send(TradeOrder(self.__exchange, amount))


class ZeroTradeOrderStub:
    
    def buy(self, amount):
        warn_tb("Zero exchange orders are useless! Ignoring...", cut = None)

    def sell(self, amount):
        warn_tb("Zero exchange orders are useless! Ignoring...", cut = None)

    def contract(self, amount):
        warn_tb("Zero exchange orders are useless! Ignoring...", cut = None)


class OrderFactory:

    def __init__(self, lazy=False):
        self.__lazy = lazy
        self.trade0 = ZeroTradeOrderStub()
        self.trade1 = TradeOrderFactory(1, lazy)
        self.trade3 = TradeOrderFactory(3, lazy)
        self.trade10 = TradeOrderFactory(10, lazy)

    def __send(self, order):
        return order if self.__lazy else order.send()

    def cell_charge(self, addr, amount):
        return self.__send(CellOrder(addr, -try_float_posi(amount)))

    def cell_discharge(self, addr, amount):
        return self.__send(CellOrder(addr, try_float_posi(amount)))

    def cell_delta(self, addr, amount):
        # поздравляем, вы открыли антисахар на аккумулятор
        return self.__send(CellOrder(addr, amount))

    def influence(self, addr, amount):
        return self.__send(InfluenceOrder(addr, amount))

    def line_on(self, addr, line):
        return self.__send(LineOrder(addr, line, True))

    def line_off(self, addr, line):
        return self.__send(LineOrder(addr, line, False))

    def line_set(self, addr, line, value):
        # поздравляем, вы открыли антисахар на линию
        return self.__send(LineOrder(addr, line, value))


class TradeEntry(namedtuple("TradeEntry", ["amount", "exchange", "issued", "owner"])):

    @staticmethod
    def from_json(data):
        return TradeEntry(amount=data["amount"], issued=data["issued"],
                          exchange=Exchange.decode(data["exchange"]),
                          owner=Player.decode(data["owner"]))

    def __repr__(self):
        return "<contract for {} MWh in {} move(s) from player {}>".format(
            self.amount, self.exchange, self.owner
        )


ForecastedValue = namedtuple("ForecastedValue", ["value", "forecast"])


class Sun(ForecastedValue):

    @staticmethod
    def from_json(data):
        return Sun(data[5], Quartile.from_json(data[:5]))

    def __repr__(self):
        return "<{}, forecast {} lux>".format(
            "none" if self.value is None else (str(self.value) + " lux"),
            self.forecast,
        )


class Wind(ForecastedValue):

    @staticmethod
    def from_json(data):
        return Wind(data[5], Quartile.from_json(data[:5]))

    def __repr__(self):
        return "<{}, forecast {} m/s>".format(
            "none" if self.value is None else (str(self.value) + " m/s"),
            self.forecast,
        )


class Power(ForecastedValue):

    @staticmethod
    def from_json(data):
        return Power(data[5], Quartile.from_json(data[:5]))

    def __repr__(self):
        return "<{}, forecast {} MWh>".format(
            "none" if self.value is None else (str(self.value) + " MWh"),
            self.forecast,
        )


Consumer = namedtuple("Consumer", ["addr", "contract", "profits", "losses", "power", "influence", "preset"])
Generator = namedtuple("Generator", ["addr", "contract", "profits", "losses", "power", "influence"])


# noinspection PyUnresolvedReferences
class TypicalClient:

    def is_consumer(self):
        return isinstance(self, Consumer)

    def is_generator(self):
        return isinstance(self, Generator)

    def describe(self):
        if self.is_consumer():
            return (f"<{self.cls} {' '.join(self.addr)}, -{safe_last(self.power)} MWh, "
                    f"+{safe_last(self.profits)} R, -{safe_last(self.losses)} R>")
        else:
            return (f"<{self.cls} {' '.join(self.addr)}, +{safe_last(self.power)} MWh, "
                    f"+{safe_last(self.profits)} R, -{safe_last(self.losses)} R>")

    def short(self):
        return f"<{self.cls} {' '.join(self.addr)}>"

    def __repr__(self):
        return self.describe()

    def __eq__(self, other):
        if isinstance(other, TypicalClient):
            return self.addr == other.addr
        return False

    def __hash__(self):
        return hash(self.addr)


class Solar(TypicalClient, Generator):
    cls = "solar"


class Winder(TypicalClient, Generator):
    cls = "winder"


class House(TypicalClient, Consumer):
    cls = "house"


class Factory(TypicalClient, Consumer):
    cls = "factory"


class Hospital(TypicalClient, Consumer):
    cls = "hospital"


class ClientFactory:
    constructors = {
        "Solar": (Solar, False), "Winder": (Winder, False),
        "House": (House, True), "Factory": (Factory, True),
        "Hospital": (Hospital, True),
    }

    @staticmethod
    def from_json(data):
        cls, cons = ClientFactory.constructors[data["type"]]
        if cons:
            return cls(tuple(data["addr"]), data["contract"], data["profits"],
                       data["losses"], data["power"], data["influence"],
                       [Quartile.from_json(x) for x in data["preset"]])
        else:
            return cls(tuple(data["addr"]), data["contract"], data["profits"],
                       data["losses"], data["power"], data["influence"])


class Module:
    @staticmethod
    def decode(value):
        type_ = value["module"]
        if type_ == "cell":
            return Cell(value["charge"])
        elif type_ == "transformer":
            return Transformer()
        else:
            raise TypeError("Некорректное входное значение модуля подстанции")


class Cell(Module):
    def __init__(self, charge):
        self.charge = charge
        self.is_cell = True

    def __repr__(self):
        return f"<cell, charged to {self.charge} MWh>"


class Transformer(Module):
    def __init__(self):
        self.is_cell = False

    def __repr__(self):
        return "<transformer>"


class Station:
    @staticmethod
    def from_json(data):
        type_ = data["station"]
        if type_ == "main_v0":
            return MainStation(data["addr"], data["modules"])
        elif type_ == "mini_v0":
            return MiniStation(data["addr"])
        else:
            raise TypeError("unknown station type " + type_)


class MainStation(Station):

    def __init__(self, addr, modules_raw):
        super(MainStation, self).__init__()
        self.addr = addr
        self.modules = [Module.decode(x) for x in modules_raw]
        self.cells = sum(1 for x in self.modules if isinstance(x, Cell))
        self.transformers = sum(1 for x in self.modules if isinstance(x, Transformer))
        self.charge = sum(x.charge[-1] for x in self.modules if isinstance(x, Cell) and x.charge)

    def __repr__(self):
        return f"<main station {self.addr} {self.modules}>"


class MiniStation(Station):

    def __init__(self, addr):
        super(MiniStation, self).__init__()
        self.addr = addr

    def __repr__(self):
        return f"<mini station {self.addr}>"


class Region:

    def __init__(self, data, parent):
        self.__parent = parent
        self.online = data["online"]
        self.lines = [simple_line(l) for l in data["lines"]]
        self.clients = [ClientFactory.from_json(l) for l in data["clients"]]

    def get_all_lines(self, exclude_self=False):
        ans = set()
        if not exclude_self:
            ans.update(self.lines)
        for (a, l) in self.lines:
            line = self.__parent.line(a, l)
            if line is not None:
                ans.update(line.get_all_lines(False))
        return list(ans)

    def get_all_regions(self, exclude_self=False):
        ans = self.__parent.lines(self.get_all_lines())
        if not exclude_self:
            ans.append(self)
        return ans

    def get_all_clients(self, exclude_self=False):
        ans = set()
        if not exclude_self:
            ans.update(self.clients)
        for (a, l) in self.lines:
            line = self.__parent.line(a, l)
            if line is not None:
                ans.update(line.get_all_lines(False))
        return list(ans)

    def __repr__(self):
        return "<region {} {}>".format([x.short() for x in self.clients], self.lines)


class Powersystem:

    def __init__(self, data):
        # сюрприз-сюрприз, никто не запрещает вам работать с районами напрямую
        # только помните, что ключ - кортеж из адреса и лини
        self.data = ({simple_line(l): Region(r, self) for (l, r) in data})

    def line(self, addr, line):
        return self.data.get((addr, line), None)

    def lines(self, lines_list=None):
        if lines_list is None:
            return list(self.data.items())
        else:
            return [(l, self.data[l]) for l in lines_list if l in self.data]

    def get_all_lines(self):
        # самое рациональное решение
        return list(self.data.keys())

    def get_all_regions(self):
        # самое рациональное решение
        return list(self.data.values())

    def get_all_clients(self):
        ans = set()
        for l in self.data.values():
            ans.update(l.clients)
        return ans

    def __repr__(self):
        return repr(self.data)


class Powerstand:

    def __init__(self, data):
        weather = data["weather"]
        self.sun = [Sun.from_json(x) for x in weather["sun"]]
        self.wind = [Wind.from_json(x) for x in weather["wind"]]

        you_raw, powersystem = data["networks"][0]
        self.you = Player.decode(you_raw)
        self.powersystem = Powersystem(powersystem["regions"])
        self.score = powersystem["score"]
        self.stations = {x["addr"]: Station.from_json(x) for x in powersystem["stations"]}

        self.exchange = [TradeEntry.from_json(te) for te in data["exchange"]]

        self.orders = OrderFactory()
        self.orders_lazy = OrderFactory(True)

    def get_move(self):
        try:
            return next(i-1 for i,v in enumerate(self.sun)
                        if v.value is None)
        except StopIteration:
            return len(self.sun)-1

    def humanize(self):
        return "\n".join([
            "Weather:",
            "\n".join(f"{i+1: >3} : sun {short_fv(s)} lux, wind {short_fv(w)} m/s"
                      for i, (s, w) in enumerate(zip(self.sun, self.wind))),
            "Exchange:",
            "\n".join(map(repr, self.exchange)),
            "Regions:",
            "\n".join(map(repr, self.powersystem.data.items()))
        ])

    def __repr__(self):
        return "<powerstand data>"

# TODO: больше сахара на биржу (фильтрация по типам?)
# FIXME: надеюсь, никто не додумается менять поля в приказах. это ничего не изменит
# TODO? добавить get и set для параметров приказа?!
# TODO? учитывать LineVariant
# TODO? сахарок на текущий ход?
# TODO: номер хода
# TODO: счёт игрока
# TODO: модули на подстанциях
