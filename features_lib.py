import pickle
import sys
import json
from profiles import *
from make_profiles import *
import time
import os
import datetime


def make_counters():
    return Counters()

def try_div(a, b, default):
    if b > 0:
        return float(a)/b
    else:
        return default

def cos_prob(user, item, ot_type, user_ct_type, event_ct_type, show_ct_type, rt_type, ts):
    user_mod = 0.
    item_mod = 0.
    prod = 0.

    user_slice = user.slice(ot_type, user_ct_type, rt_type)

    event_slice = item.slice(ot_type, event_ct_type, rt_type)
    show_slice = item.slice(ot_type, show_ct_type, rt_type)

    for key,c in user_slice.items():
        v = c.get(ts, rt_type)

        user_mod += v

    for key,c in show_slice.items():
        v = c.get(ts, rt_type)

        item_mod += v*v
        if key in user_slice and key in event_slice:
            prod += (user_slice[key].get(ts, rt_type) * event_slice[key].get(ts, rt_type) / float(v) if v > 0 else 0.)

    if user_mod == 0 or item_mod == 0:
        return -100.

    if prod > 0:
        prod = prod / user_mod

    return prod

def counter_cos(user, item, ot_type, user_ct_type, item_ct_type, user_rt_type, item_rt_type, ts, dbg=False):
    user_mod = 0.
    item_mod = 0.
    prod = 0.

    user_slice = user.slice(ot_type, user_ct_type, user_rt_type)
    item_slice = item.slice(ot_type, item_ct_type, item_rt_type)

    if dbg:
        print("=========")
        print("User:)")
    for key,c in user_slice.items():
        v = c.get(ts, user_rt_type)
        if dbg:
            print(key, v)

        user_mod += v*v

    if dbg:
        print("Item:")
    for key,c in item_slice.items():
        v = c.get(ts, item_rt_type)
        if dbg:
            print(key, v)

        item_mod += v*v
        if key in user_slice:
            v2 = user_slice[key].get(ts, user_rt_type)
            prod += v * v2

    if user_mod == 0 or item_mod == 0:
        return -100.

    if prod > 0:
        prod = prod / (math.sqrt(user_mod) * math.sqrt(item_mod))

    if dbg:
        print("Cos:", prod)

    return prod

class column_description:
    def __init__(self):
        self.done = False
        self.columns = []

    def add(self, fname, ftype='Num'):
        if not self.done:
            self.columns.append((fname,ftype))

    def finish(self):
        self.done = True


