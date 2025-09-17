import random
import numpy as np
import os
from collections import Counter


def generate_random_rules(num_items, num_rules, max_antecedents, max_consequents):
    # Walidacja parametrów wejściowych
    # if num_items < max_antecedents + max_consequents:
    #     raise ValueError(f"Liczba elementów ({num_items}) jest za mała, aby wygenerować reguły z maksymalnie {max_antecedents} poprzednikami i {max_consequents} następnikami.")
    
    items = [f'I{i}' for i in range(1, num_items + 1)]
    rules = []
    attempts = 0
    
    # Dynamiczny podział reguł: 40% częste, 40% umiarkowane, 20% rzadkie
    if num_rules < 10:
        frequent_count = max(1, num_rules // 3)
        moderate_count = max(1, num_rules // 3)
        rare_count = num_rules - frequent_count - moderate_count
    else:
        frequent_count = int(0.4 * num_rules)  # 40% reguł częstych
        moderate_count = int(0.4 * num_rules)  # 40% reguł umiarkowanych
        rare_count = num_rules - frequent_count - moderate_count  # 20% reguł rzadkich
    
    rule_types = [
        (0.5, 0.8, frequent_count),   # Częste
        (0.1, 0.5, moderate_count),   # Umiarkowane
        (0.01, 0.1, rare_count)       # Rzadkie
    ]

    for min_prob, max_prob, count in rule_types:
        target_count = sum(c for _, _, c in rule_types[:rule_types.index((min_prob, max_prob, count)) + 1])
        while len(rules) < target_count and attempts < 1000:
            attempts += 1
            antecedents_size = random.randint(1, max_antecedents)
            consequents_size = random.randint(1, max_consequents)
            antecedents = set(random.sample(items, antecedents_size))
            remaining_items = [item for item in items if item not in antecedents]
            if len(remaining_items) < consequents_size or not remaining_items:
                continue
            consequents = set(random.sample(remaining_items, consequents_size))
            if antecedents & consequents:
                continue
            probability = random.uniform(min_prob, max_prob)
            rules.append((tuple(antecedents), tuple(consequents), probability))
    
    if len(rules) < num_rules:
        print(f"Uwaga: Wygenerowano tylko {len(rules)} reguł zamiast {num_rules}.")
    
    return rules

def generate_zipf_noise_distribution(items, alpha=1.5):
    n = len(items)
    ranks = np.arange(1, n + 1)
    weights = 1 / ranks ** alpha
    probabilities = weights / weights.sum()
    return items, probabilities

def generate_synthetic_data(num_transactions, rules, noise_ratio=0, confidence_range=(0.3, 0.9), avg_transaction_length=5, all_items=None):
    transactions = []
    if all_items is not None:
        items = all_items
    else:
        items_set = set()
        for antecedents, consequents, _ in rules:
            items_set.update(antecedents)
            items_set.update(consequents)
        items = list(items_set)
    if noise_ratio is not 0:
        items, zipf_probs = generate_zipf_noise_distribution(items)

    adjusted_noise_ratio = noise_ratio * min(1.0, 10000 / num_transactions)
    noise_items = int(avg_transaction_length * adjusted_noise_ratio)

    item_counts = Counter()
    for antecedents, consequents, prob in rules:
        for item in antecedents:
            item_counts[item] += prob
        for item in consequents:
            item_counts[item] += prob


    for _ in range(num_transactions):
        transaction = set()
        base_prob=1
        for antecedents, consequents, prob in rules:
            if random.random() < prob:
                transaction.update(antecedents)
                base_prob=prob
                confidence = random.uniform(*confidence_range)
                if random.random() < confidence:
                    transaction.update(consequents)
        for _ in range(noise_items):
        if noise_ratio is not 0:
                transaction.add(random.choices(items, weights=zipf_probs)[0])
            else:
                transaction.add(random.choice(items))
        target_length = max(1, int(random.gauss(avg_transaction_length, 0.5)))
        # while len(transaction) < target_length:
        #     if use_zipf_noise:
        #         transaction.add(random.choices(items, weights=zipf_probs)[0])
        #     else:
        #         transaction.add(random.choice(items))
        
        # Sortowanie transakcji według numeru ID (I1, I2, ...)
        transaction = mutate_transaction(transaction, items, avg_transaction_length,base_prob)
        transactions.append(transaction)
    
    return transactions

def save_to_file(transactions, filename):
    with open(filename, 'w') as f:
        for transaction in transactions:
            f.write(','.join(transaction) + '\n')

def compute_statistics(transactions, expected_length):
    all_items = [item for t in transactions for item in t]
    unique_items = set(all_items)
    lengths = [len(t) for t in transactions]
    avg_len = sum(lengths) / len(transactions)
    print("\n--- Statystyki danych ---")
    print(f"Liczba transakcji: {len(transactions)}")
    print(f"Średnia długość transakcji: {avg_len:.2f} (oczekiwana: {expected_length})")
    print(f"Liczba unikalnych przedmiotów: {len(unique_items)}")

def validate_rules_in_data(transactions, rules):
    stats = []
    for antecedents, consequents, prob in rules:
        # Obliczanie wsparcia dla pełnej reguły (antecedents ∪ consequents)
        support_count = sum(1 for t in transactions if set(antecedents).union(set(consequents)).issubset(t))
        # Obliczanie liczby transakcji z poprzednikiem
        antecedent_count = sum(1 for t in transactions if set(antecedents).issubset(t))
        # Wsparcie reguły
        support = support_count / len(transactions) if len(transactions) > 0 else 0
        # Ufność reguły
        confidence = support_count / antecedent_count if antecedent_count > 0 else 0
        stats.append({
            "rule": f"{antecedents} -> {consequents}",
            "expected_prob": prob,
            "support": support,
            "confidence": confidence
        })
    return stats

def save_validation_stats(stats, filename):
    with open(filename, 'w') as f:
        f.write("Rule,Expected Probability,Support,Confidence\n")
        for stat in stats:
            f.write(f"{stat['rule']},{stat['expected_prob']:.2f},{stat['support']:.2f},{stat['confidence']:.2f}\n")

def save_rules_to_file(rules, filename):
    with open(filename, 'w') as f:
        for antecedents, consequents, prob in rules:
            f.write(f"{antecedents} -> {consequents} [p={prob:.2f}]\n")

def choose_rule_sizes(num_items, avg_transaction_length):
    # Zakładamy, że reguła nie może używać więcej elementów niż mamy dostępnych.
    # Maksymalnie 80% długości transakcji na poprzedniki, reszta na następniki
    max_total = min(avg_transaction_length, num_items)
    max_antecedents = max(1, int(round(max_total * 0.7)))
    max_consequents = max(1, max_total - max_antecedents)
    # Jeszcze zabezpieczenie, by suma nie przekroczyła liczby elementów
    if max_antecedents + max_consequents > num_items:
        max_consequents = num_items - max_antecedents
        if max_consequents < 1:
            max_consequents = 1
            max_antecedents = num_items - 1
    return max_antecedents, max_consequents

def generate_multiple_datasets():
    configs = [
   {"name": "bazowy", "num_items": 20, "num_rules": 10, "num_transactions": 100000, "noise_ratio": 0.0, "avg_length": 5},

    # {"name": "bardzo_maly_zbior", "num_items": 20, "num_rules": 10, "num_transactions": 1000, "noise_ratio": 0.0, "avg_length": 5},

    # {"name": "duzy_zbior", "num_items": 20, "num_rules": 10, "num_transactions": 200000, "noise_ratio": 0.0, "avg_length": 5},

    # {"name": "mala_liczba_elementow", "num_items": 10, "num_rules": 10, "num_transactions": 100000, "noise_ratio": 0.0, "avg_length": 4},

    # {"name": "duza_liczba_elementow", "num_rules": 10, "num_items": 30, "num_transactions": 100000, "noise_ratio": 0.0, "avg_length": 6},

    # {"name": "gesty_zbior", "num_items": 20, "num_rules": 15, "num_transactions": 100000, "noise_ratio": 0.0, "avg_length": 10},

    # {"name": "niski_szum", "num_items": 20, "num_rules": 10, "num_transactions": 100000, "noise_ratio": 0.05, "avg_length": 5},

    # {"name": "wysoki_szum", "num_items": 20, "num_rules": 10, "num_transactions": 100000, "noise_ratio": 0.3, "avg_length": 5},

    # {"name": "umiarkowanie_gesty", "num_items": 25, "num_rules": 12, "num_transactions": 30000, "noise_ratio": 0.1, "avg_length": 8},

    # {"name": "wieloelementowe_krotkie_transakcje", "num_items": 30, "num_rules": 15, "num_transactions": 15000, "noise_ratio": 0.05, "avg_length": 4}
]

    datasets = {}
    # Tworzenie nadrzędnych folderów dla różnych typów plików
    os.makedirs("dane/synthetic_data", exist_ok=True)
    os.makedirs("dane/rules", exist_ok=True)
    os.makedirs("dane/stats", exist_ok=True)
    
    for config in configs:
        all_possible_items = [f'I{i}' for i in range(1, config["num_items"] + 1)]
        max_antecedents, max_consequents = choose_rule_sizes(config["num_items"], config["avg_length"])
        rules = generate_random_rules(config["num_items"], config["num_rules"], max_antecedents, max_consequents)
        data = generate_synthetic_data(
            config["num_transactions"], rules, noise_ratio=config["noise_ratio"],
            confidence_range=(0.6, 0.9), avg_transaction_length=config["avg_length"],
            use_zipf_noise=True, all_items=all_possible_items
        )
        data_filename = os.path.join("dane/synthetic_data", f"synthetic_data_{config['name']}.csv")
        rules_filename = os.path.join("dane/rules", f"rules_{config['name']}.txt")
        stats_filename = os.path.join("dane/stats", f"stats_{config['name']}.csv")
        save_to_file(data, data_filename)
        save_rules_to_file(rules, rules_filename)
        compute_statistics(data, config["avg_length"])
        stats = validate_rules_in_data(data, rules)
        save_validation_stats(stats, stats_filename)
        datasets[config["name"]] = data
        print(f"\nWygenerowano zestaw danych: {config['name']} zapisany do {data_filename}")
    
    return datasets

def mutate_transaction(transaction, all_items, avg_len, base_prob):
    """
    Mutacja transakcji zależna od prawdopodobieństwa reguły.
    Im niższe prob, tym większe szanse na usunięcie/dodanie elementów.
    """
    t = set(transaction)

    # im niższe prob, tym większe szanse na mutację
    remove_chance = 0.5 * (1 - base_prob)   # np. prob=0.8 → 0.1, prob=0.2 → 0.4
    add_chance = 0.5 * (1 - base_prob)
    adjust_chance = 0.3

    # losowe usuwanie
    if len(t) > 1 and random.random() < remove_chance:
        t.remove(random.choice(list(t)))

    # losowe dodanie nowego elementu
    if random.random() < add_chance:
        t.add(random.choice(all_items))

    # # dostosowanie długości transakcji
    while len(t) < avg_len and random.random() < adjust_chance:
         t.add(random.choice(all_items))
    while len(t) > avg_len and random.random() < adjust_chance:
        t.remove(random.choice(list(t)))

    return sorted(t, key=lambda x: int(x.replace('I', '')))


# Generowanie zestawów danych
datasets = generate_multiple_datasets()