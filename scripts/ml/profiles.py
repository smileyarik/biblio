from collections import defaultdict
from enum import Enum
from math import exp

ONE_DAY_SECONDS = 86400
LN_2 = 0.693147180


class OT(str, Enum):
    ITEM = "ITEM"
    USER = "USER"
    AUTHOR = "AUTHOR"
    LIBRARY= "LIBRARY"
    RUBRIC = "RUBRIC"
    SERIES = "SERIES"
    AGE = "AGE"
    GLOBAL = "GLOBAL"


class CT(str, Enum):
    HAS = "HAS"
    VALUE = "VALUE"
    BOOKING = "BOOKING"
    BOOKING_NORM = "BOOKING_NORM"
    BOOKING_BY = "BOOKING_BY"


class RT(str, Enum):
    SUM = "SUM"
    D7 = "D7"
    D30 = "D30"
    D180 = "D180"


class CounterKey:
    def __init__(self, object_type, counter_type, reducer_type):
        self.object_type = object_type
        self.counter_type = counter_type
        self.reducer_type = reducer_type

    def as_tuple(self):
        return (self.object_type, self.counter_type, self.reducer_type)

    def __hash__(self):
        return hash(self.as_tuple())

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()


class Counter:
    def __init__(self, value = 0, ts = 0):
        self.value = value
        self.ts = ts

    def _calc_decay(self, reducer_type, ts_delta):
        halflife = 0
        if reducer_type == RT.D7:
            halflife = 7 * ONE_DAY_SECONDS
        elif reducer_type ==  RT.D30:
            halflife = 30 * ONE_DAY_SECONDS
        return exp(-LN_2 * ts_delta / halflife)

    def add(self, delta, ts, reducer_type):
        if reducer_type == RT.SUM or self.ts == 0:
            self.value += delta
            self.ts = ts
            return
        decay = self._calc_decay(reducer_type, float(ts - self.ts))
        self.value = self.value * decay + delta
        self.ts = ts

    def get(self, ts, reducer_type):
        if reducer_type == RT.SUM or self.ts == 0:
            return self.value
        decay = self._calc_decay(reducer_type, float(ts - self.ts))
        return self.value * decay


def make_counter_dd():
    return defaultdict(Counter)


class Counters:
    def __init__(self):
        self.counter_dict = defaultdict(make_counter_dd)

    def _add(self, counter_key, object_id, delta, ts):
        self.counter_dict[counter_key][object_id].add(delta, ts, counter_key.reducer_type)

    def _set(self, counter_key, object_id, value, ts):
        self.counter_dict[counter_key][object_id] = Counter(value, ts)

    def _get(self, counter_key, object_id, ts):
        return self.counter_dict[counter_key][object_id].get(ts, counter_key.reducer_type)

    def _has(self, counter_key, object_id):
        return counter_key in self.counter_dict and object_id in self.counter_dict[counter_key]

    def _slice(self, counter_key):
        return self.counter_dict[counter_key]

    def add(self, object_type, counter_type, reducer_type, object_id, delta, ts):
        key = CounterKey(object_type, counter_type, reducer_type)
        self._add(key, object_id, delta, ts)

    def set(self, object_type, counter_type, reducer_type, object_id, value, ts):
        key = CounterKey(object_type, counter_type, reducer_type)
        self._set(key, object_id, value, ts)

    def get(self, object_type, counter_type, reducer_type, object_id, ts):
        key = CounterKey(object_type, counter_type, reducer_type)
        return self._get(key, object_id, ts)

    def getts(self, object_type, counter_type, reducer_type, object_id):
        key = CounterKey(object_type, counter_type, reducer_type)
        return self.counter_dict[key][object_id].ts

    def has(self, object_type, counter_type, reducer_type, object_id):
        key = CounterKey(object_type, counter_type, reducer_type)
        return self._has(key, object_id)

    def slice(self, object_type, counter_type, reducer_type):
        return self._slice(CounterKey(object_type, counter_type, reducer_type))

    def update_from(
        self,
        other,
        object_type,
        counter_type,
        reducer_type,
        to_counter_type,
        to_reducer_type,
        ts,
        weight=1.0
    ):
        for object_id, counter in other.slice(object_type, counter_type, reducer_type).items():
            self.add(
                object_type,
                to_counter_type,
                to_reducer_type,
                object_id,
                counter.get(ts, reducer_type) * weight,
                ts
            )

    def print_debug(self):
        for c_key, counters in self.counter_dict.items():
            print("Counter:", c_key.object_type, c_key.counter_type, c_key.reducer_type)
            for object_id, counter in counters.items():
                print("\tObject: {}; Value: {}; Timestamp: {}".format(object_id, counter.value, counter.ts))
