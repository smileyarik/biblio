import sys
import json
from collections import defaultdict
import csv
import pickle
from profiles import *
from make_profiles import *

users = pickle.load(open(sys.argv[1], 'rb'))

# split ground truth
out = {}
out_writer = {}
ground_users = set()
for i in range(-1,11):
    out[i] = open(sys.argv[5] + '%d.txt' % i, 'w')
    out_writer[i] = csv.writer(out[i], delimiter=',')
    out_writer[i].writerow(['user_id', 'target'])

answers = defaultdict(set)
with open(sys.argv[4]) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    head = next(reader, None)
    for row in reader:
        user_id = int(row[5])
        item_id = int(row[1])
        answers[user_id].add(item_id)
        ground_users.add(user_id)

warn = False
for user_id,ans in answers.items():
    #if user_id not in done_users:
    #    if not warn:
    #        print("Failed to find user", user_id)
    #        warn = True
    #    continue

    user_size = int(users[user_id].get(OT_GLOBAL, CT_BOOKING, RT_SUM, '', 0))
    #print(user_id, user_size, users[user_id].has(OT_GLOBAL, CT_BOOKING, RT_SUM, ''))
    #users[user_id].print_debug()
    if user_size > 10:
        user_size = 10

    row = [user_id, ' '.join([str(x) for x in ans])]
    out_writer[user_size].writerow(row)
    out_writer[-1].writerow(row)

out = {}
out_writer = {}
done_users = set()

# split submission
for i in range(-1,11):
    out[i] = open(sys.argv[3] + '%d.txt' % i, 'w')
    out_writer[i] = csv.writer(out[i], delimiter=',')
    out_writer[i].writerow(['user_id', 'target'])

with open(sys.argv[2]) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    head = next(reader, None)
    for row in reader:
        user_id = int(row[0])
        done_users.add(user_id)
        user_size = int(users[user_id].get(OT_GLOBAL, CT_BOOKING, RT_SUM, '', 0))
        if user_size > 10:
            user_size = 10

        out_writer[user_size].writerow(row)
        out_writer[-1].writerow(row)

for user_id in ground_users:
    if user_id not in done_users:
        user_size = int(users[user_id].get(OT_GLOBAL, CT_BOOKING, RT_SUM, '', 0))
        if user_size > 10:
            user_size = 10

        row = [user_id, ' '.join([str(x) for x in range(100000000,100000020)])]
        out_writer[user_size].writerow(row)
        out_writer[-1].writerow(row)

