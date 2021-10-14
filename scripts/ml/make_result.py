import sys
from collections import defaultdict

path = sys.argv[1]
score_idx = int(sys.argv[2])

tops = defaultdict(list)
for line in open(path, 'r'):
    row = line.strip().split('\t')
    tops[row[0]].append((row[1], float(row[score_idx])))

print('user_id,target')
for user_id in tops:
    top = sorted(tops[user_id], key=lambda x:-x[1])
    print('%s,%s' % (user_id, ' '.join([x for x,r in top[0:20]])))
