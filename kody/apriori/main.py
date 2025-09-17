import random
from itertools import combinations
from collections import defaultdict
import time

def generate_transactions(num_transactions=10000, num_items=20, max_items_per_transaction=5):
    """Generuje syntetyczne transakcje z częstszymi parami produktów"""
    items = [f'item_{i}' for i in range(1, num_items + 1)]
    
    # Celowo tworzymy kilka częstych par
    frequent_pairs = [frozenset(random.sample(items, 2)) for _ in range(5)]
    
    transactions = []
    for _ in range(num_transactions):
        # Bazowa transakcja
        transaction = set(random.choices(
            items,
            weights=[random.randint(1, 10) for _ in items],
            k=random.randint(1, max_items_per_transaction)
        ))
        
        # Dodajemy częste pary z 30% prawdopodobieństwem
        if random.random() < 0.3 and frequent_pairs:
            transaction.update(random.choice(frequent_pairs))
            
        transactions.append(transaction)
    
    return transactions

def apriori_optimized(transactions, min_supp):
    """Poprawna implementacja algorytmu Apriori"""
    transactions = [frozenset(t) for t in transactions]
    min_count = len(transactions) * min_supp
    
    # Krok 1: Zbiory 1-elementowe
    item_counts = defaultdict(int)
    for trans in transactions:
        for item in trans:
            item_counts[frozenset([item])] += 1
    
    frequent_items = {itemset: count for itemset, count in item_counts.items() if count >= min_count}
    all_frequent = dict(frequent_items)
    
    k = 2
    while True:
        # Generowanie kandydatów
        prev_items = list(all_frequent.keys())
        candidates = set()
        
        # Łączenie w pary
        for i in range(len(prev_items)):
            for j in range(i+1, len(prev_items)):
                new_candidate = prev_items[i].union(prev_items[j])
                if len(new_candidate) == k:
                    candidates.add(new_candidate)
        
        # Przycinanie
        valid_candidates = []
        for candidate in candidates:
            if k == 2:
                subsets = [frozenset([item]) for item in candidate]
            else:
                subsets = combinations(candidate, k-1)
                
            if all(frozenset(sub) in all_frequent for sub in subsets):
                valid_candidates.append(candidate)
        
        # Zliczanie wsparcia
        candidate_counts = defaultdict(int)
        for trans in transactions:
            for candidate in valid_candidates:
                if candidate.issubset(trans):
                    candidate_counts[candidate] += 1
        
        new_frequent = {itemset: count for itemset, count in candidate_counts.items() if count >= min_count}
        if not new_frequent:
            break
            
        all_frequent.update(new_frequent)
        k += 1
    
    return all_frequent

# Generowanie danych
transactions = generate_transactions()

# Testowanie
start = time.time()
results = apriori_optimized(transactions, min_supp=0.01)  # Zmniejsz min_supp dla wiecej wynikow
end = time.time()

# Analiza
print(f"\nCzas wykonania: {end - start:.2f}s")
print(f"Znalezionych zbiorów: {len(results)}")
print("\nTop 10 najczęstszych:")
for itemset, count in sorted(results.items(), key=lambda x: -x[1])[:100]:
    print(f"{set(itemset)} -> {count} wystąpień ({count/len(transactions):.2%})")
