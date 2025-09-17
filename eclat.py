import itertools
import pandas as pd


def preprocess(transactions):
    data = {}
    for tid, transaction in enumerate(transactions):
        for item in transaction:
            if item not in data:
                data[item] = set()
            data[item].add(tid)
    return data

FreqItems = {}

def eclat(prefix, items, minsup_count, freq_items=None):
    if freq_items is None:
        freq_items = {}

    while items:
        i, itids = items.pop()
        isupp = len(itids)
        if isupp >= minsup_count:
            freq_items[frozenset(prefix + [i])] = isupp
            suffix = []
            for j, ojtids in items:
                jtids = itids & ojtids
                if len(jtids) >= minsup_count:
                    suffix.append((j, jtids))
            eclat(prefix + [i], sorted(suffix, key=lambda x: len(x[1]), reverse=True), minsup_count, freq_items)

    return freq_items


