import datetime
import sys
import csv
import json
from profiles import *
from collections import defaultdict
import pickle
import time
import datetime

def getts(d):
    return int(datetime.datetime.strptime(d, "%d.%m.%Y").timestamp())


if __name__ == '__main__':
    target_users = set()

    start_ts = getts(sys.argv[1])

    print("Read target users")
    with open(sys.argv[2]) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            target_users.add(int(row[5]))

    print("Parsing transactions")
    user_links = defaultdict(list)
    item_links = defaultdict(list)

    with open(sys.argv[3]) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)

        count = 1
        for row in reader:
            user_id = int(row[5])
            item_id = int(row[1])
            ts = getts(row[3])
            if ts >= start_ts:
                if count % 100000 == 0:
                    print(count)
                count += 1

                user_links[user_id].append(item_id)
                item_links[item_id].append(user_id)

    pagerank = defaultdict(dict)
    count = 0
    for user_id in target_users:
        user2item = defaultdict(float)
        user2user = defaultdict(float)

        links = user_links[user_id]

        for item_id in links:
            w = 1./len(links)
            i_links = item_links[item_id]
            for user_id_2 in i_links:
                user2user[user_id_2] += w/len(i_links)

        for user_id_2,w in user2user.items():
            u_links = user_links[user_id_2]
            n = 0
            for item_id in u_links:
                if item_id not in pagerank[user_id]:
                    pagerank[user_id][item_id] = w/len(u_links)
                else:
                    pagerank[user_id][item_id] += w/len(u_links)

        count += 1
        if count % 100 == 0:
            print(count, 'of', len(target_users))

    print("Dumping rw")
    with open(sys.argv[4], 'wb') as rw_pickle:
        pickle.dump(pagerank, rw_pickle)


