import math

from ml.profiles import Counters


def try_div(a, b, default):
    return float(a) / b if b > 0 else default


def counter_cos(user, item, ot_type, user_ct_type, item_ct_type, user_rt_type, item_rt_type, ts):
    user_slice = user.slice(ot_type, user_ct_type, user_rt_type)
    item_slice = item.slice(ot_type, item_ct_type, item_rt_type)

    user_mod = 0.0
    for _, counter in user_slice.items():
        v = counter.get(ts, user_rt_type)
        user_mod += v*v

    prod = 0.0
    item_mod = 0.0
    for key, counter in item_slice.items():
        item_value = counter.get(ts, item_rt_type)
        item_mod += item_value * item_value
        if key not in user_slice:
            continue
        user_value = user_slice[key].get(ts, user_rt_type)
        prod += item_value * user_value

    if user_mod == 0.0 or item_mod == 0.0:
        return -100.0

    if prod > 0:
        prod = prod / (math.sqrt(user_mod) * math.sqrt(item_mod))
    return prod


class ColumnDescription:
    def __init__(self):
        self.done = False
        self.columns = []

    def add(self, fname, ftype='Num'):
        if not self.done:
            self.columns.append((fname, ftype))

    def finish(self):
        self.done = True


