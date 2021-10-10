from collections import defaultdict
import math

OT_ITEM = 0;
OT_USER = 1;
OT_AUTHOR = 2;
OT_LIBRARY= 3;
OT_RUBRIC = 4;
OT_PERSON = 5;
OT_SERIES = 6;
OT_AGE = 7;
OT_GLOBAL = 8;

CT_HAS = 0;
CT_VALUE = 1;
CT_BOOKING = 2;
CT_BOOKING_NORM = 4;
CT_BOOKING_BY = 5;

RT_SUM = 0;
RT_7D = 1;
RT_30D = 2;
RT_180D = 3;

class CounterKey:
    def __init__(self, obj_type, cnt_type, red_type):
        self.obj_type = obj_type
        self.cnt_type = cnt_type
        self.red_type = red_type

    def __hash__(self):
        return hash((self.obj_type, self.cnt_type, self.red_type))

    def __eq__(self, other):
        return (self.obj_type, self.cnt_type, self.red_type) == (other.obj_type, other.cnt_type, self.red_type)

class Counter:
    def __init__(self, value = 0, ts = 0):
        self.value = value
        self.ts = ts

    def add(self, delta, ts, red_type):
        if red_type == RT_SUM or self.ts == 0:
            self.value += delta
            self.ts = ts
            return
        halflife = 0;
        if red_type == RT_7D:
            halflife = 7 * 86400
        elif red_type == RT_30D:
            halflife = 30 * 86400
        self.value *= math.exp(-0.693147180 * float(ts - self.ts)/halflife)
        self.value += delta
        self.ts = ts

    def get(self, ts, red_type):
        if red_type == RT_SUM or self.ts == 0:
            return self.value
        halflife = 0;
        if red_type == RT_7D:
            halflife = 7 * 86400
        elif red_type == RT_30D:
            halflife = 30 * 86400
        return self.value * math.exp(-0.693147180 * float(ts - self.ts)/halflife)


def make_counter():
    return Counter()

def make_counter_dd():
    return defaultdict(make_counter)

class Counters:
    def __init__(self):
        self.counter_dict = defaultdict(make_counter_dd)

    def _add(self, counter_key, obj_id, delta, ts):
        self.counter_dict[counter_key][obj_id].add(delta, ts, counter_key.red_type)

    def _set(self, counter_key, obj_id, value, ts):
        self.counter_dict[counter_key][obj_id] = Counter(value, ts)

    def _get(self, counter_key, obj_id, ts):
        return self.counter_dict[counter_key][obj_id].get(ts, counter_key.red_type)

    def _has(self, counter_key, obj_id):
        return counter_key in self.counter_dict and obj_id in self.counter_dict[counter_key]

    def _slice(self, counter_key):
        return self.counter_dict[counter_key]

    def add(self, obj_type, cnt_type, red_type, obj_id, delta, ts):
        self._add(CounterKey(obj_type, cnt_type, red_type), obj_id, delta, ts)

    def set(self, obj_type, cnt_type, red_type, obj_id, value, ts):
        self._set(CounterKey(obj_type, cnt_type, red_type), obj_id, value, ts)

    def get(self, obj_type, cnt_type, red_type, obj_id, ts):
        return self._get(CounterKey(obj_type, cnt_type, red_type), obj_id, ts)

    def getts(self, obj_type, cnt_type, red_type, obj_id):
        return self.counter_dict[CounterKey(obj_type, cnt_type, red_type)][obj_id].ts

    def has(self, obj_type, cnt_type, red_type, obj_id):
        return self._has(CounterKey(obj_type, cnt_type, red_type), obj_id)

    def slice(self, obj_type, cnt_type, red_type):
        return self._slice(CounterKey(obj_type, cnt_type, red_type))

    def update_from(self, other, obj_type, cnt_type, red_type, to_cnt_type, to_red_type, ts, weight=1.):
        for obj_id,counter in other.slice(obj_type, cnt_type, red_type).items():
            self.add(obj_type, to_cnt_type, to_red_type, obj_id, counter.get(ts, red_type) * weight, ts)

    def setnorm(self, obj_type_from, cnt_type_from, obj_type_by, cnt_type_by, obj_type_to, cnt_type_to):
        #ts = self.getts(obj_type_by, cnt_type_by, red_type, '')
        n = self.get(obj_type_by, cnt_type_by, RT_SUM, '', 0)

        for obj_id,counter in self.slice(obj_type_from, cnt_type_from, RT_SUM).items():
            if n <= 0:
                print("WTF", obj_type_from, cnt_type_from, obj_type_by, cnt_type_by, obj_type_to, cnt_type_to, obj_id, n)
                exit()
            v = counter.get(0, RT_SUM)
            self.set(obj_type_to, cnt_type_to, RT_SUM, obj_id, float(v)/n, 0)

    def print_debug(self):
        for c_key in self.counter_dict:
            print("Counter:", c_key.obj_type, c_key.cnt_type, c_key.red_type)
            for obj_id in self.counter_dict[c_key]:
                print("    Object:", obj_id)
