import csv
import sys
import time
import datetime

def getts(d):
    return int(datetime.datetime.strptime(d, "%d.%m.%Y").timestamp())


start_train_ts = getts(sys.argv[7])
end_train_ts = getts(sys.argv[8])
start_valid_ts = getts(sys.argv[9])
end_valid_ts = getts(sys.argv[10])

#user_id,org_id,rating,ts,aspects


#circulationID;catalogueRecordID;barcode;startDate;finishDate;readerID;bookpointID;state;;
with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    headers = next(reader, None)

    train_stat_f = open(sys.argv[2], 'w')
    train_stat_writer = csv.writer(train_stat_f, delimiter=';')
    train_stat_writer.writerow(headers)
    train_targ_f = open(sys.argv[3], 'w')
    train_targ_writer = csv.writer(train_targ_f, delimiter=';')
    train_targ_writer.writerow(headers)

    valid_stat_f = open(sys.argv[4], 'w')
    valid_stat_writer = csv.writer(valid_stat_f, delimiter=';')
    valid_stat_writer.writerow(headers)
    valid_targ_f = open(sys.argv[5], 'w')
    valid_targ_writer = csv.writer(valid_targ_f, delimiter=';')
    valid_targ_writer.writerow(headers)

    test_stat_f = open(sys.argv[6], 'w')
    test_stat_writer = csv.writer(test_stat_f, delimiter=';')
    test_stat_writer.writerow(headers)

    sortedlist = sorted(reader, key=lambda row: getts(row[3]), reverse=False)
    for row in sortedlist:
        ts = getts(row[3])

        test_stat_writer.writerow(row)
        if ts < start_train_ts:
            train_stat_writer.writerow(row)
            valid_stat_writer.writerow(row)
        elif ts < end_train_ts:
            valid_stat_writer.writerow(row)
            train_targ_writer.writerow(row)
        elif ts < start_valid_ts:
            valid_stat_writer.writerow(row)
        elif ts < end_valid_ts:
            valid_targ_writer.writerow(row)
