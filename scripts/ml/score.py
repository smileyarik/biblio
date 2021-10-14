# encoding=utf-8

import sys
import numpy as np
import pandas as pd
import json

from collections import Counter


def MNAP(size=20):

    assert size >= 1, "Size must be greater than zero!"

    def metric(y_true, predictions, size=size):
        '''
        Score for all users
        '''

        y_true = y_true.rename({'target': 'y_true'}, axis='columns')
        predictions = predictions.rename({'target': 'predictions'}, axis='columns')

        merged = y_true.merge(predictions, left_on='user_id', right_on='user_id')

        def score(x, size=size):
            '''
            Score for single user
            '''

            y_true = x[1][1]
            predictions = x[1][2]

            test_unique = Counter(predictions[0:size])
            if test_unique.most_common(1)[0][1] != 1:
                print('Keys in each prediction in ../data/temp.csv must be unique! %s' % (str(predictions)))
                #print('Keys in each prediction in ../data/temp.csv must be unique!')

            weight = 0

            inner_weights = [0]
            for n, item in enumerate(predictions[0:size]):
                inner_weight = inner_weights[-1] + (1 if item in y_true else 0)
                inner_weights.append(inner_weight)

            for n, item in enumerate(predictions):
                if item in y_true:
                    weight += inner_weights[n + 1] / (n + 1)

            return weight / min(len(y_true), size)

        #print([score(row) for row in merged.iterrows()])
        return np.mean([score(row) for row in merged.iterrows()])


    return metric


if __name__ == '__main__':
    public_path = sys.argv[2]

    submitted_path = sys.argv[1]

    y_public = pd.read_csv(public_path)

    y_public['target'] = y_public['target'].apply(lambda x: x.split(' '))
    metric = MNAP()

    try:
        y_pred = pd.read_csv(submitted_path)
        y_pred['target'] = y_pred['target'].apply(lambda x: x.split(' '))
    except Exception as e:
        print("$Error while reading answer file: {str(e)}$", file=open("../data/temp.csv", "w"))
        sys.exit(0)

    try:
        how_many = len(y_public)

        if y_pred.shape != (how_many, 2):
            print('Incorrect shape: {y_pred.shape} instead of {(how_many, 2)}')

        public_len = len(y_pred.merge(y_public, on='user_id', validate='one_to_one'))

        if public_len != how_many:
            print('Missing keys in ../data/temp.csv!')

    except ValueError as e:
        print("$Error while validating .csv file: {str(e)}$", file=open("../data/temp.csv", "w"))
        sys.exit(0)

    try:
        score_public = metric(y_public, y_pred)

    except ValueError as e:
        print("$Error while scoring .csv file: {str(e)}$", file=open("../data/temp.csv", "w"))
        sys.exit(0)

    score = {
        'public': float(score_public),
    }

    print(score_public, len(y_public))

