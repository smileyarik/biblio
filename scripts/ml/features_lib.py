import math

from ml.profiles import Counters, RT, OT, CT


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


class FeaturesCalcer:
    def __init__(self, full_events, rw_graph=None, lstm_graph=None):
        self.full_events = full_events
        self.rw_graph = rw_graph
        self.lstm_graph = lstm_graph

    def __call__(self, user, item, ts):
        ucnt = user.counters
        icnt = item.counters

        f = list()
        if self.rw_graph:
            f.append(self.rw_graph.get(user.object_id, {}).get(item.object_id, 0.0))
        if self.lstm_graph:
            f.append(self.lstm_graph.get(user.object_id, {}).get(item.object_id, 0.0))
        for rt in [RT.SUM, RT.D7, RT.D30]:
            f.append(counter_cos(ucnt, icnt, OT.AUTHOR, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.LIBRARY, CT.BOOKING, CT.BOOKING, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.RUBRIC, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.SERIES, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.AGE_RESTRICTION, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.LANGUAGE, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.READER_AGE, CT.BOOKING_BY, CT.BOOKING, rt, RT.SUM, ts))
            f.append(counter_cos(ucnt, icnt, OT.BBK_PREFIX, CT.BOOKING_BY, CT.HAS, rt, RT.SUM, ts))
            f.append(float(ucnt.get(OT.GLOBAL, CT.BOOKING, rt, '', ts)))
            item_size = float(icnt.get(OT.GLOBAL, CT.BOOKING, rt, '', ts))
            full_size = float(self.full_events.get(OT.GLOBAL, CT.BOOKING, rt, '', ts))
            f.append(item_size / full_size)
        return f

    def get_cd(self):
        cd = ColumnDescription()
        if self.rw_graph:
            cd.add('random_walk')
        if self.lstm_graph:
            cd.add('lstm_score')
        for rt in [RT.SUM, RT.D7, RT.D30]:
            cd.add('author_cos_rt_' + rt)
            cd.add('library_cos_rt_' + rt)
            cd.add('rubric_cos_rt_' + rt)
            cd.add('series_cos_rt_' + rt)
            cd.add('age_restriction_cos_rt_' + rt)
            cd.add('language_cos_rt_' + rt)
            cd.add('reader_age_cos_rt_' + rt)
            cd.add('bbk_cos_rt_' + rt)
            cd.add('user_size_rt_' +  rt)
            cd.add('item_size_rt_' + rt)
        cd.finish()
        return cd
