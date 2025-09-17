import itertools
import pandas as pd

# Dane wejściowe
transactions = [
    ['Chleb', 'Mleko', 'Masło'],
    ['Chleb', 'Mleko', 'Jajka'],
    ['Mleko', 'Jajka'],
    ['Chleb', 'Mleko', 'Jajka'],
    ['Chleb', 'Masło', 'Jajka']
]

minsup_percent = 0.4  # np. 0.4 to 40%

# Przetwarzanie do formatu ECLAT
def preprocess(transactions):
    data = {}
    for tid, transaction in enumerate(transactions):
        for item in transaction:
            if item not in data:
                data[item] = set()
            data[item].add(tid)
    return data

FreqItems = {}

def eclat(prefix, items, minsup_count):
    while items:
        i, itids = items.pop()
        isupp = len(itids)
        if isupp >= minsup_count:
            FreqItems[frozenset(prefix + [i])] = isupp
            suffix = []
            for j, ojtids in items:
                jtids = itids & ojtids
                if len(jtids) >= minsup_count:
                    suffix.append((j, jtids))
            eclat(prefix + [i], sorted(suffix, key=lambda item: len(item[1]), reverse=True), minsup_count)

# Główna część programu
data = preprocess(transactions)
minsup_count = int(minsup_percent * len(transactions))
total_transactions = len(transactions)

eclat([], sorted(data.items(), key=lambda item: len(item[1]), reverse=True), minsup_count)

# Przygotowanie wyników do Pandas
results = []
for itemset, supp in FreqItems.items():
    support_fraction = supp / total_transactions
    results.append({'support': support_fraction, 'itemsets': tuple(sorted(itemset))})

# Konwersja do DataFrame
df = pd.DataFrame(results)
df = df.sort_values(by='support', ascending=False).reset_index(drop=True)

print(df.to_string(index=True))
