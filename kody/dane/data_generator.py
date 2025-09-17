import random
import numpy as np
import os
from collections import Counter

def generate_random_itemsets(num_items, num_itemsets, avg_length, zipf_alpha=1.1):
    items = [f"I{i}" for i in range(1,num_items+1)]
    itemsets = []

    avg_itemset_length=int(min(avg_length*0.6,5))
    # if num_itemsets <= 0 or num_items <= 0 or avg_itemset_length == num_items:
    #     print("Liczba elementów, liczba zbiorów lub średnia długość zbioru jest nieprawidłowa.")
    #     return []

    # Losowanie długości itemsetów z rozkładu normalnego
    lengths = [max(1, int(np.random.normal(loc=avg_itemset_length, scale=1))) for _ in range(num_itemsets)]
    lengths.sort()  # Najkrótsze będą najczęstsze

    # Losowanie supportów: najkrótsze mają najwyższy, najdłuższe najniższy
    min_sup, max_sup = 0.01, 0.2
    supports = np.linspace(max_sup, min_sup, num_itemsets)



    generated_sets = set()
    for i in range(num_itemsets):
        length = lengths[i]
        attempts = 0
        while attempts < 20:
            zipf_indices = []
            while len(zipf_indices) < length:
                item = draw_zipf_item(items, zipf_alpha)
                if item not in zipf_indices:
                    zipf_indices.append(item)
            itemset = tuple(sorted(zipf_indices, key=lambda x: int(x[1:])))
            if itemset in generated_sets:
                attempts += 1
                continue
            support = float(round(supports[i], 2))
            itemsets.append((itemset, support))
            generated_sets.add(itemset)
            break  # przejdź do kolejnego itemsetu

    itemsets.sort(key=lambda x: (len(x[0]), [int(i[1:]) for i in x[0]]))
    return itemsets

def draw_zipf_item(items, zipf_alpha):
    """
    Losuje jeden item z listy 'items' zgodnie z rozkładem Zipfa o parametrze zipf_alpha.
    """
    ranks = np.arange(1, len(items) + 1)
    weights = 1 / np.power(ranks, zipf_alpha)
    weights = weights / weights.sum()  # normalizacja do sumy 1
    return random.choices(items, weights=weights, k=1)[0]

def add_item(transaction, all_items, zipf_alpha):
    for _ in range(50):  # żeby nie ryzykować nieskończonej pętli
        item = draw_zipf_item(all_items, zipf_alpha)
        if item not in transaction:
            transaction.add(item)
            return

def remove_item(transaction, all_items, zipf_alpha):
    """
    Usuwa jeden element z transaction na podstawie odwrotnego rozkładu Zipfa.
    """
    if len(transaction) <= 1:
        return  # nie usuwaj jeśli tylko jeden element

    ranks = np.arange(1, len(all_items) + 1)
    weights = np.power(ranks, zipf_alpha)  # odwrotny rozkład - większe wagi mają rzadkie elementy
    weights /= weights.sum()  # normalizacja do 1

    for _ in range(50):
        item = random.choices(all_items, weights=weights, k=1)[0]
        if item in transaction:
            transaction.remove(item)
            return

def generate_data(num_transactions ,itemsets,num_items, zipf_alpha=1.1, avg_len=5):
    transactions = []
    all_items = [f"I{i}" for i in range(1,num_items+1)]

  
    for _ in range(num_transactions):
        transaction = set()
        for iset, sup in reversed(itemsets):
            if random.random() < sup:# and len(transaction) + len(iset) <= avg_len:
                transaction.update(iset)
                break

        remove_or_add_chance = 0.0001
        if len(transaction) > 1 and random.random() < remove_or_add_chance:
            #usuwanie losowego elementu
            if random.random()<0.3:
                for _ in range(10):
                    item=random.choice(all_items)
                    #item = draw_zipf_item(all_items, zipf_alpha)
                    if item  in transaction:
                        transaction.remove(item)
                        break
            else: #dodawanie losowego elementu
                for _ in range(10):
                    item = draw_zipf_item(all_items, zipf_alpha)
                    if item not in transaction:
                        transaction.add(item)
                        break
    

        target_len = int(np.random.normal(loc=avg_len, scale=1))
        target_len = max(1, target_len)

        if len(transaction) < target_len:
            while len(transaction) < target_len:
                item=random.choice(all_items)
                transaction.add(item)
                #transaction.add(draw_zipf_item(all_items, zipf_alpha))
        elif len(transaction) > target_len:
            while len(transaction) > target_len and len(transaction) > 1:
                transaction.remove(random.choice(list(transaction)))


        if not transaction:
            item = draw_zipf_item(all_items, zipf_alpha)
            transaction.add(item)

        transactions.append(sorted(transaction, key=lambda x: int(x[1:])))

    return transactions

def save_to_file(transactions, filename):
    """
    Zapisuje transakcje do pliku tekstowego, każda transakcja w osobnej linii.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for transaction in transactions:
            f.write(','.join(transaction) + '\n')

def compute_statistics(transactions, expected_length):
    """
    Wyświetla statystyki dotyczące transakcji: liczba, średnia długość, liczba unikalnych itemów.
    """
    all_items = [item for t in transactions for item in t]
    unique_items = set(all_items)
    lengths = [len(t) for t in transactions]
    avg_len = sum(lengths) / len(transactions) if transactions else 0
    print("\n--- Statystyki danych ---")
    print(f"Liczba transakcji: {len(transactions)}")
    print(f"Średnia długość transakcji: {avg_len:.2f} (oczekiwana: {expected_length})")
    print(f"Liczba unikalnych przedmiotów: {len(unique_items)}")

def save_validation_stats(stats, filename):
    """
    Zapisuje statystyki walidacji itemsetów do pliku CSV.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Itemset,Expected Probability,Support\n")
        for stat in stats:
            itemset_str = ','.join(sorted(stat['itemset'], key=lambda x: int(x[1:])))
            f.write(f"{itemset_str},{stat['expected_prob']:.2f},{stat['support']:.2f}\n")

def validate_itemsets_in_data(transactions, itemsets):
    """
    Waliduje itemsety na podstawie transakcji.
    Zwraca listę statystyk dla każdego itemsetu.
    """
    stats = []
    for itemset, prob in itemsets:
        itemset_set = set(itemset)
        support_count = sum(1 for t in transactions if itemset_set.issubset(t))
        support = support_count / len(transactions) if transactions else 0
        stats.append({
            "itemset": itemset,
            "expected_prob": prob,
            "support": support
        })
   

    all_items = [item for itemset, _ in itemsets for item in itemset]  # wypakowanie wszystkich itemów z krotek
    unique_items = set(all_items)
    #print(f"Liczba unikalnych przedmiotów w  itemsets: {len(unique_items)}")

    return stats

def save_itemsets_to_file(itemsets, filename):
    """
    Zapisuje itemsety do pliku tekstowego.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for itemset, support in itemsets:
            f.write(f"{tuple(sorted(itemset, key=lambda x: int(x[1:])))} [support={support:.2f}]\n")

def generate_multiple_datasets():
    configs = [
        # {"name": "bazowy", "num_items": 20, "num_itemsets": 10,
        # "num_transactions": 1000000, "avg_length": 7, "zipf_alpha": 1.1},

        # {"name": "maly", "num_items": 20, "num_itemsets": 10,
        # "num_transactions": 50000, "avg_length": 5, "zipf_alpha": 1.1},

        # {"name": "sredni", "num_items": 20, "num_itemsets": 10,
        # "num_transactions": 200000, "avg_length": 7, "zipf_alpha": 1.1},

        # {"name": "duzy", "num_items": 20, "num_itemsets": 10,
        # "num_transactions": 1000000, "avg_length": 7, "zipf_alpha": 1.1},

        # {"name": "bardzo_duzy", "num_items": 20, "num_itemsets": 10,
        # "num_transactions": 3000000, "avg_length": 9, "zipf_alpha": 1.1},

        # {"name": "rowny", "num_items": 10000, "num_itemsets": 10,
        # "num_transactions": 1000000, "avg_length": 6, "zipf_alpha": 2},

        {"name": "test", "num_items": 50, "num_itemsets":30,
        "num_transactions": 50000, "avg_length": 5, "zipf_alpha": 1.1},
        
        {"name": "test_0itemsets", "num_items": 50, "num_itemsets":0,
        "num_transactions": 50000, "avg_length": 5, "zipf_alpha": 1.1},
    ]

    os.makedirs("dane/synthetic_data", exist_ok=True)
    os.makedirs("dane/itemsets", exist_ok=True)
    os.makedirs("dane/stats", exist_ok=True)

    datasets = {}
    for config in configs:
        itemsets = generate_random_itemsets(
            config["num_items"],
            config["num_itemsets"],
            config["avg_length"],
            zipf_alpha=config.get("zipf_alpha")
        )
        transactions = generate_data(
            config["num_transactions"],
            itemsets,
            config["num_items"],
            zipf_alpha=config.get("zipf_alpha"),
            avg_len=config["avg_length"]
        )

        data_filename = os.path.join("dane/synthetic_data", f"synthetic_data_{config['name']}.csv")
        itemsets_filename = os.path.join("dane/itemsets", f"itemsets_{config['name']}.txt")
        stats_filename = os.path.join("dane/stats", f"stats_{config['name']}.csv")

        save_to_file(transactions, data_filename)
        save_itemsets_to_file(itemsets, itemsets_filename)
        compute_statistics(transactions, config["avg_length"])
        stats = validate_itemsets_in_data(transactions, itemsets)
        save_validation_stats(stats, stats_filename)

        datasets[config["name"]] = transactions
        print(f"\nWygenerowano zestaw danych: {config['name']} zapisany do {data_filename}")

    return datasets

datasets = generate_multiple_datasets()

