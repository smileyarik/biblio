import pickle
import sys
import json
from profiles import *
from make_profiles import *
from features_lib import *
import time
import os
import datetime

def getts(d):
    return int(datetime.datetime.strptime(d, "%d.%m.%Y").timestamp())


print("Loading")
users = pickle.load(open(sys.argv[1], 'rb'))
items = pickle.load(open(sys.argv[2], 'rb'))
rw = pickle.load(open(sys.argv[3], 'rb'))
poptop = int(sys.argv[4])
items_per_group = int(sys.argv[5])

#known_target = (sys.argv[3] == 'train')
start_ts = getts(sys.argv[6])
ts=start_ts

target_users = set()
target_items = defaultdict(set)
print("Read target users")
#circulationID;catalogueRecordID;barcode;startDate;finishDate;readerID;bookpointID;state;;
with open(sys.argv[7]) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    next(reader, None)
    for row in reader:
        target_items[int(row[5])].add(int(row[1]))
        target_users.add(int(row[5]))

print(len(target_users))

filter_items = defaultdict(set)
print("Read already seen items")
#circulationID;catalogueRecordID;barcode;startDate;finishDate;readerID;bookpointID;state;;
with open(sys.argv[10]) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    next(reader, None)
    for row in reader:
        filter_items[int(row[5])].add(int(row[1]))

print("Calc candidates")
book_top = []
rw_top = defaultdict(list)

for user_id in rw:
    #print('=====', user_id, len(rw[user_id]), '=====')
    for item_id in rw[user_id]:
        rw_top[user_id].append((item_id,rw[user_id][item_id]))
    rw_top[user_id] = sorted(rw_top[user_id], key=lambda x: -x[1])

for item_id,item in items.items():
    item_size = float(item.get(OT_GLOBAL, CT_BOOKING, RT_30D, '', 0))
    book_top.append((item_id, item_size))

book_top = sorted(book_top, key=lambda x:-x[1])

print("Calc global stat")
full_events = Counters()
for item_id, item in items.items():
    for rt in [RT_SUM, RT_7D, RT_30D]:
        full_events.update_from(item, OT_GLOBAL, CT_BOOKING, rt, CT_BOOKING, rt, start_ts)

print('All bookings 30d:', full_events.get(OT_GLOBAL, CT_BOOKING, RT_30D, '', start_ts))

feat_out = open(sys.argv[8], 'w')
cd_out = open(sys.argv[9], 'w')

print("Calc features")
cd = column_description()
for user_id in target_users:
    user = users[user_id]
    top = book_top[0:poptop]
    stop = set([x for x,y in top])
    for item_id,rank in rw_top[user_id]:
        if item_id not in stop and item_id not in filter_items[user_id]:
            top.append((item_id, rank))
        if len(top) == items_per_group:
            break

    stop = set([x for x,y in top])
    #print(user_id, len(top))
    ttop = book_top[poptop:]
    for item_id,rank in ttop:
        if len(top) >= items_per_group:
            break
        if item_id not in stop and item_id not in filter_items[user_id]:
            top.append((item_id,rank))

    #print(user_id, len(top))
    user_size = float(user.get(OT_GLOBAL, CT_BOOKING, RT_SUM, '', 0))
    #print(top)
    found_target = 0
    for item_id,item_size in top:
        if item_id in target_items[user_id]:
            found_target += 1
    if len(target_items[user_id]) > 0 and found_target == 0:
        continue

    user.print_debug()
    for item_id,item_size in top:
        item = items[item_id]
        #print('=======', item_id, '=======')
        #item.print_debug()
        item_size = float(item.get(OT_GLOBAL, CT_BOOKING, RT_SUM, '', 0))
        target = 1 if item_id in target_items[user_id] else 0
        f = []

        if item_id in rw[user_id]:
            f.append(rw[user_id][item_id])
        else:
            f.append(0.)
        cd.add('pagerank')

        # OT_ITEM = 0; OT_USER = 1; OT_AUTHOR = 2; OT_LIBRARY = 3; OT_RUBRIC = 4; OT_PERSON = 5; OT_SERIES = 6; OT_AGE = 7;
        for rt in [RT_SUM, RT_7D, RT_30D]:
            f.append(counter_cos(user, item, OT_AUTHOR, CT_BOOKING_BY, CT_HAS, rt, RT_SUM, ts))
            cd.add('author_cos')
            f.append(counter_cos(user, item, OT_LIBRARY, CT_BOOKING, CT_BOOKING, rt, RT_SUM, ts))
            cd.add('library_cos')
            f.append(counter_cos(user, item, OT_RUBRIC, CT_BOOKING_BY, CT_HAS, rt, RT_SUM, ts))
            cd.add('rubric_cos')
            f.append(counter_cos(user, item, OT_PERSON, CT_BOOKING_BY, CT_HAS, rt, RT_SUM, ts))
            cd.add('person_cos')
            f.append(counter_cos(user, item, OT_SERIES, CT_BOOKING_BY, CT_HAS, rt, RT_SUM, ts, dbg=True))
            cd.add('series_cos')

        for rt in [RT_SUM, RT_7D, RT_30D]:
            f.append(float(user.get(OT_GLOBAL, CT_BOOKING, rt, '', ts)))
            cd.add('user_size_rt%d'%rt)

        for rt in [RT_SUM, RT_7D, RT_30D]:
            f.append(float(item.get(OT_GLOBAL, CT_BOOKING, rt, '', ts))/full_events.get(OT_GLOBAL, CT_BOOKING, rt, '', ts))
            cd.add('item_size_rt%d'%rt)

        cd.finish()

        feat_out.write('%s\t%s\t%d\t%s\n' % (user_id, item_id, target, '\t'.join([str(ff) for ff in f])))

cd_out.write('0\tGroupId\tuser_id\n')
cd_out.write('1\tAuxiliary\titem_id\n')
cd_out.write('2\tLabel\ttarget\n')
for i in range(0,len(cd.columns)):
    cd_out.write('%d\t%s\t%s\n' % (i+3, cd.columns[i][1], cd.columns[i][0]))




