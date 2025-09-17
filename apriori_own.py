from itertools import combinations
from collections import defaultdict


def apriori_own(transactions, min_supp):
    if not transactions or not (0 <min_supp <=1):
        return {}

    transactions=[frozenset(t) for t in transactions]
    min_count = len(transactions) * min_supp
    item_counts = defaultdict(int)

    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1
    
    
    frequent_itemsets = {itemset: count for itemset, count in item_counts.items() if count >= min_count}
    if not frequent_itemsets:
        return frequent_itemsets
    
    
    k = 2
    while True:
        candidates = set()
        itemsets = list(frequent_itemsets.keys())
        
        for i in range(len(itemsets)):
            for j in range(i + 1, len(itemsets)):
                a, b = itemsets[i], itemsets[j]
                if k > 2:  
                    a_sorted = sorted(list(a))
                    b_sorted = sorted(list(b))
                    if a_sorted[:k-2] != b_sorted[:k-2]:
                        continue  
                union = a.union(b)
                if len(union) == k and all(
                    frozenset(subset) in frequent_itemsets 
                    for subset in combinations(union, k-1)
                ):
                    candidates.add(union)
        
        if not candidates: break

        # Zliczanie wsparcia
        candidate_counts = defaultdict(int)
        for transaction in transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    candidate_counts[candidate] += 1
        
        # Filtracja kandydatów
        new_frequent = {itemset: count for itemset, count in candidate_counts.items() if count >= min_count}
        if not new_frequent:
            break
        frequent_itemsets.update(new_frequent)
        k += 1

    return frequent_itemsets




