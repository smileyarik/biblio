import json
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
        assert isinstance(self.object_type, OT)
        self.counter_type = counter_type
        assert isinstance(self.counter_type, CT)
        self.reducer_type = reducer_type
        assert isinstance(self.reducer_type, RT)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def as_tuple(self):
        return (self.object_type, self.counter_type, self.reducer_type)

    def __str__(self):
        return "|".join(self.as_tuple())

    def __repr__(self):
        return str(self)

    @classmethod
    def from_str(cls, st):
        ot, ct, rt = st.split("|")
        return cls(OT(ot), CT(ct), RT(rt))


class Counter:
    def __init__(self, value = 0, ts = 0):
        self.value = value
        self.ts = ts

    @staticmethod
    def _calc_decay(reducer_type, ts_delta):
        halflife = 0
        if reducer_type == RT.D7:
            halflife = 7 * ONE_DAY_SECONDS
        elif reducer_type == RT.D30:
            halflife = 30 * ONE_DAY_SECONDS
        else:
            raise 'unsupported reduce'
        return exp(-LN_2 * ts_delta / halflife)

    @staticmethod
    def _reduce_sorted(reducer_type, x, x_ts, y, y_ts):
        assert x_ts <= y_ts
        return x * Counter._calc_decay(reducer_type, float(y_ts - x_ts)) + y

    @staticmethod
    def _reduce(reducer_type, x, x_ts, y, y_ts):
        return Counter._reduce_sorted(reducer_type, x, x_ts, y, y_ts) if x_ts < y_ts else Counter._reduce_sorted(reducer_type, y, y_ts, x, x_ts)

    def add(self, delta, ts, reducer_type):
        if reducer_type == RT.SUM or self.ts == 0:
            self.value += delta
            self.ts = ts
            return
        self.value = Counter._reduce(reducer_type, self.value, self.ts, delta, ts)
        self.ts = max(self.ts, ts)

    def get(self, ts, reducer_type):
        if reducer_type == RT.SUM or self.ts == 0:
            return self.value
        assert self.ts <= ts
        return Counter._reduce(reducer_type, self.value, self.ts, 0.0, ts)

    @property
    def __dict__(self):
        return {
            "value": self.value,
            "ts": self.ts
        }


def make_counter_dd():
    return defaultdict(Counter)


class Counters:
    def __init__(self):
        self.data = defaultdict(make_counter_dd)

    def _add(self, counter_key, object_id, delta, ts):
        self.data[counter_key][object_id].add(delta, ts, counter_key.reducer_type)

    def _set(self, counter_key, object_id, value, ts):
        self.data[counter_key][object_id] = Counter(value, ts)

    def _get(self, counter_key, object_id, ts):
        return self.data[counter_key][object_id].get(ts, counter_key.reducer_type)

    def _has(self, counter_key, object_id):
        return counter_key in self.data and object_id in self.data[counter_key]

    def _slice(self, counter_key):
        return self.data[counter_key]

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
        return self.data[key][object_id].ts

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
        for c_key, counters in self.data.items():
            print("Counter:", c_key.object_type, c_key.counter_type, c_key.reducer_type)
            for object_id, counter in counters.items():
                print("\tObject: {}; Value: {}; Timestamp: {}".format(object_id, counter.value, counter.ts))

    @property
    def __dict__(self):
        result = dict()
        for counter_key, counters in self.data.items():
            objects = list()
            for object_id, counter in counters.items():
                objects.append((object_id, counter.value, counter.ts))
            result[str(counter_key)] = objects
        return result

    @classmethod
    def from_dict(cls, data):
        counters = Counters()
        for counter_key_str, objects in data.items():
            counter_key = CounterKey.from_str(counter_key_str)
            for obj in objects:
                counters.data[counter_key][obj[0]] = Counter(obj[1], obj[2])
        return counters


class Profile:
    def __init__(self, object_id, object_type):
        self.object_id = object_id
        self.object_type = object_type
        self.counters = Counters()

    @property
    def __dict__(self):
        return {
            "object_id": self.object_id,
            "object_type": self.object_type.value,
            "counters": vars(self.counters)
        }

    @classmethod
    def from_dict(cls, data):
        profile = cls(data["object_id"], OT(data["object_type"]))
        profile.counters = Counters.from_dict(data["counters"])
        return profile

    def dumps(self):
        return json.dumps(vars(self), ensure_ascii=False).strip()

    def dump(self, f):
        f.write(self.dumps() + "\n")

    @classmethod
    def loads(cls, st):
        return cls.from_dict(json.loads(st))

    def print_debug(self):
        print("===== {} {} =====".format(self.object_type.value, self.object_id))
        self.counters.print_debug()
