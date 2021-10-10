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
    try:
        return int(datetime.datetime.strptime(d, "%d.%m.%Y").timestamp())
    except:
        #1991-11-26 14:00:00
        try:
            return int(datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").timestamp())
        except:
            print("Bad date -%s-" % d)
            return int(datetime.datetime.strptime('12.12.2010', "%d.%m.%Y").timestamp())


def make_counters():
    return Counters()

if __name__ == '__main__':
    item_counters = defaultdict(make_counters)
    user_counters = defaultdict(make_counters)

    bookpoint_to_lib = {}
    print("Read bookpoint data")
    # id;cbs;name;adress;eisk
    with open(sys.argv[1]) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            #print(row)
            if row[4] != '' and row[0] != '':
                bookpoint_to_lib[int(row[0])] = int(row[4])

    author_to_id = {}
    with open('../data/authors.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            author_to_id[row[1]] = int(row[0])
    rubric_to_id = {}
    with open('../data/rubrics.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            rubric_to_id[row[1]] = int(row[0])
    series_to_id = {}
    with open('../data/series.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            series_to_id[row[1]] = int(row[0])
    person_to_id = {}
    with open('../data/persons.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            person_to_id[row[1]] = int(row[0])


    print("Read books data")
    # recId;aut;title;place;publ;yea;lan;rubrics;person;serial;material;biblevel;ager
    with open('../data/cat.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            item_id = int(row[0])
            item = item_counters[item_id]

            if row[1] != '':
                if row[1] in author_to_id:
                    author_id = author_to_id[row[1]]
                    if author_id != None and author_id != 0:
                        item.set(OT_AUTHOR, CT_HAS, RT_SUM, author_id, 1, 0)
            if row[7] != '':
                for f in row[7].strip().split(' : '):
                    if f in rubric_to_id:
                        rubric_id = rubric_to_id[f]
                        item.set(OT_RUBRIC, CT_HAS, RT_SUM, rubric_id, 1, 0)
            if row[8] != '':
                for f in row[8].strip().split(' : '):
                    if f in person_to_id:
                        person_id = person_to_id[f]
                        item.set(OT_PERSON, CT_HAS, RT_SUM, person_id, 1, 0)
            if row[9] != '':
                for f in row[9].strip().split(' : '):
                    if f in series_to_id:
                        series_id = series_to_id[f]
                        item.set(OT_SERIES, CT_HAS, RT_SUM, series_id, 1, 0)
            if item_id == 456976:
                print('=====', item_id, type(item_id), '=====')
                item.print_debug()


    print("Read books.jsn")
    with open(sys.argv[2]) as bookfile:
        json_data = json.load(bookfile)

        for book in json_data:
            item_id = book['id']
            item = item_counters[item_id]
            #print(book['libraryAvailability'])
            if 'libraryAvailability' in book:
                for lib in book['libraryAvailability']:
                    lib_id = lib['libraryId']
                    count = lib['totalOutCount']
                    item.set(OT_LIBRARY, CT_VALUE, RT_SUM, lib_id, count, 0)

    print("Read user data")
    with open(sys.argv[3]) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            #user_id,city
            user_id = int(row[0])
            bd = getts(row[1])

            user = user_counters[user_id]
            user.set(OT_AGE, CT_VALUE, RT_SUM, '', getts('07.10.2021')-bd, 0)

    target_users = set()
    print("Read target users")
    with open(sys.argv[4]) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            target_users.add(int(row[5]))


    print("Parsing transactions")
    # circulationID;catalogueRecordID;barcode;startDate;finishDate;readerID;bookpointID;state;;
    # OT_ITEM = 0; OT_USER = 1; OT_AUTHOR = 2; OT_LIBRARY = 3; OT_RUBRIC = 4; OT_PERSON = 5; OT_SERIES = 6; OT_AGE = 7;
    with open(sys.argv[5]) as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)

        count = 1
        for row in reader:
            if count % 100000 == 0:
                print(count)
            count += 1

            user_id = int(row[5])
            item_id = int(row[1])
            ts = getts(row[3])
            if int(row[6]) in bookpoint_to_lib:
                library_id = bookpoint_to_lib[int(row[6])]
            else:
                library_id = None

            user = user_counters[user_id]
            item = item_counters[item_id]

            for rt in [RT_SUM, RT_7D, RT_30D]:
                item.add(OT_GLOBAL, CT_BOOKING, rt, '', 1, ts)
                if library_id != None:
                    item.add(OT_LIBRARY, CT_BOOKING, rt, library_id, 1, ts)
                # TODO calc age stat for book
                # item.update_from(user, OT_AGE, CT_HAS, RT_SUM, CT_REVIEW_BY, rt, ts)

                if user_id in target_users:
                    user.add(OT_GLOBAL, CT_BOOKING, rt, '', 1, ts)

                    if library_id != None:
                        user.add(OT_LIBRARY, CT_BOOKING, rt, library_id, 1, ts)

                    user.update_from(item, OT_AUTHOR, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)
                    user.update_from(item, OT_RUBRIC, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)
                    user.update_from(item, OT_PERSON, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)
                    user.update_from(item, OT_SERIES, CT_HAS, RT_SUM, CT_BOOKING_BY, rt, ts)


    print("Dumping user profiles")
    user_counters_out = defaultdict(make_counters)
    for user_id,user in user_counters.items():
        if user_id in target_users:
            user_counters_out[user_id] = user

    with open(sys.argv[6], 'wb') as user_pickle:
        pickle.dump(user_counters_out, user_pickle)

    print("Dumping item profiles")
    with open(sys.argv[7], 'wb') as item_pickle:
        pickle.dump(item_counters, item_pickle)


