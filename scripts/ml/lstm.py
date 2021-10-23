import argparse

import tensorflow as tf
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

import sys
import numpy as np
import os
import time
from collections import defaultdict
import csv
import time
import datetime
import json


from tqdm import tqdm

from util import read_jsonl, write_jsonl

class MyLSTM:
    def __init__(self):
        self.item_to_idx = {}
        self.idx_to_item = {}
        self.max_idx = 0
        self.model = None
        self.last_week_idx = 0

    def dump(self):
        pass

    def load(self):
        pass

def make_weeked_visits(vs, current_ts, pad, max_idx):
    last_week = 1 + int(current_ts - vs[0][1])//(86400*7)
    seq = []
    if last_week < 6:
        seq.append(max_idx-1+last_week)
    for item,ts in vs:
        new_week = 1 + int(current_ts - ts)//(86400*7)
        while last_week > new_week:
            last_week -= 1
            if last_week < 6:
                seq.append(max_idx-1+last_week)
        seq.append(item)
    while last_week > 1:
        last_week -= 1
        if last_week < 6:
            seq.append(max_idx-1+last_week)
        if pad != 0:
            break

    if len(seq) > pad and pad != 0:
        print('Bad sequence', seq)
        raise Exception('Too big sequence: %d > %d' % (len(seq), pad))
    while len(seq) < pad and pad != 0:
        seq.append(0)
    return seq

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    rnn = tf.keras.layers.GRU
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
        rnn(rnn_units,
            return_sequences=True,
            recurrent_initializer='glorot_uniform',
            stateful=True,
            recurrent_dropout = 0.01), # REMOVE IT TO TURN ON CUDNN IMPLEMENTATION IF AVAILABLE
        tf.keras.layers.Dense(vocab_size)
    ])
    return model


def main(
    input_directory,
    profile_actions_path,
    target_actions_path,
    current_ts,
    checkpoint_path,
    output_path
):

    lstm = MyLSTM()

    # some nasty constants I'm too lazy to put into args
    last_visits = 30
    min_item_size = 100
    pad_length = 35
    batch_size = 32
    BUFFER_SIZE = 10000
    epochs = 4
    embedding_dim = 256
    rnn_units = 256

    print("Read target users")
    target_user_ids = set()
    target_action_gen = read_jsonl(os.path.join(input_directory, target_actions_path))
    for action in tqdm(target_action_gen):
        target_user_ids.add(action["user_id"])

    print("Parsing transactions")
    lstm.item_to_idx = {}
    lstm.idx_to_item = {}
    user_visits = defaultdict(list)
    item_count = defaultdict(int)
    idx = 1
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        item_id = action["item_scf"]
        item_count[item_id] += 1

    raw_user_visits = defaultdict(list)
    profile_action_gen = read_jsonl(os.path.join(input_directory, profile_actions_path))
    for action in tqdm(profile_action_gen):
        user_id = action["user_id"]
        item_id = action["item_scf"]
        ts = action["ts"]
        if item_count[item_id] >= min_item_size:
            raw_user_visits[user_id].append((item_id, ts))

    for user, visits in tqdm(raw_user_visits.items()):
        for item, ts in visits[-last_visits:]:
            if item not in lstm.item_to_idx:
                lstm.item_to_idx[item] = idx
                lstm.idx_to_item[idx] = item
                idx += 1
            user_visits[user].append((lstm.item_to_idx[item], ts))

    lstm.last_week_idx = idx
    print('last_week_idx', lstm.last_week_idx)

    print("Making training set")
    for user in tqdm(user_visits):
        user_visits[user] = sorted(user_visits[user], key=lambda x:x[1])

    train_seqs = []
    valid_seqs = []
    for user,visits in tqdm(user_visits.items()):
        seq = make_weeked_visits(visits, current_ts, pad_length, idx)
        if int(user) % 10 != 0:
            train_seqs.append(seq)
            if len(train_seqs) % 100000 == 1:
                print(seq)
        else:
            valid_seqs.append(seq)

    lstm.max_idx = 0
    uniq_ids = set()
    for seq in train_seqs:
        for item in seq:
            uniq_ids.add(item)
            lstm.max_idx = max(lstm.max_idx, item)

    for seq in valid_seqs:
        for item in seq:
            uniq_ids.add(item)
            lstm.max_idx = max(lstm.max_idx, item)

    assert lstm.max_idx == len(uniq_ids)-1
    vocab_size = lstm.max_idx+1
    print('Max id', lstm.max_idx)

    if True:
        examples_per_epoch = len(train_seqs)

        train_dataset = tf.data.Dataset.from_tensor_slices(train_seqs)
        valid_dataset = tf.data.Dataset.from_tensor_slices(valid_seqs)

        def split_input_target(chunk):
            input_seq = chunk[:-1]
            target_seq = chunk[1:]
            return input_seq, target_seq

        train_sequences = train_dataset.map(split_input_target)
        valid_sequences = valid_dataset.map(split_input_target)

        train_sequences = train_sequences.shuffle(BUFFER_SIZE).batch(batch_size, drop_remainder=True)
        valid_sequences = valid_sequences.shuffle(BUFFER_SIZE).batch(batch_size, drop_remainder=True)

        loss = tf.losses.SparseCategoricalCrossentropy(from_logits=True)

        checkpoint_prefix = os.path.join(checkpoint_path, "ckpt_{epoch}")

        checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_prefix,
            save_weights_only=True)

        model = build_model(
            vocab_size = vocab_size,
            embedding_dim=embedding_dim,
            rnn_units=rnn_units,
            batch_size=batch_size)

        model.compile(
            optimizer = 'adam',
            loss = loss,
            metrics=['accuracy'])

        print(tf.config.get_visible_devices())
        print(model.summary())

        print("Training model")
        steps_per_epoch = len(train_seqs)//batch_size
        #steps_per_epoch = 100
        history = model.fit(train_sequences.repeat(), epochs=epochs,
            steps_per_epoch=steps_per_epoch, callbacks=[checkpoint_callback],
            validation_data=valid_sequences.repeat(), validation_steps=len(valid_seqs)//batch_size)

        print(tf.train.latest_checkpoint(checkpoint_path))

        lstm.model = build_model(
            vocab_size = vocab_size,
            embedding_dim=embedding_dim,
            rnn_units=rnn_units,
            batch_size=1)
        old_weights = model.get_weights()
        lstm.model.set_weights(old_weights)
    else:
        lstm.model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
        lstm.model.load_weights(tf.train.latest_checkpoint(checkpoint_path))

    print("Applying model")
    weights = defaultdict(lambda: defaultdict(float))
    for user_id,visits in tqdm(user_visits.items()):
        if len(weights) == 500:
            break
        if user_id in target_user_ids:
            print(len(weights))
            seq = make_weeked_visits(visits, current_ts, 0, idx)
            seq = seq[:-1]
            input_eval = tf.expand_dims(seq, 0)
            lstm.model.reset_states()
            predictions = lstm.model(input_eval)
            predictions = tf.squeeze(predictions, 0)
            prob = predictions.numpy()[-1]
            toptop = sorted([(i,prob[i]) for i in range(1,lstm.last_week_idx)], key=lambda x:x[1], reverse=True)[0:1000]
            for idx,prob in toptop:
                if idx in lstm.idx_to_item:
                    item_id = lstm.idx_to_item[idx]
                    weights[user_id][item_id] = prob

    print("Dumping results")
    with open(os.path.join(input_directory, output_path), "w") as w:
        for user, items in tqdm(weights.items()):
            for item, weight in items.items():
                r = {"user": user, "item": item, "weight": float(weight)}
                w.write(json.dumps(r, ensure_ascii=False).strip() + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=str, required=True)
    parser.add_argument("--profile-actions-path", type=str, required=True)
    parser.add_argument("--target-actions-path", type=str, required=True)
    parser.add_argument("--checkpoint-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument("--current-ts", type=int, required=True)
    args = parser.parse_args()
    main(**vars(args))
