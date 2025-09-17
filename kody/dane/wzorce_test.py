from itertools import combinations
from collections import defaultdict
import csv

def apriori_own(transactions, min_supp, min_length=2):
    if not transactions or not (0 < min_supp <= 1):
        return {}

    transactions = [frozenset(t) for t in transactions]
    min_count = len(transactions) * min_supp
    item_counts = defaultdict(int)

    # Liczenie pojedynczych itemów
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
                    if a_sorted[:k - 2] != b_sorted[:k - 2]:
                        continue
                union = a.union(b)
                if len(union) == k and all(
                    frozenset(subset) in frequent_itemsets
                    for subset in combinations(union, k - 1)
                ):
                    candidates.add(union)

        if not candidates:
            break

        candidate_counts = defaultdict(int)
        for transaction in transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    candidate_counts[candidate] += 1

        new_frequent = {itemset: count for itemset, count in candidate_counts.items() if count >= min_count}
        if not new_frequent:
            break
        frequent_itemsets.update(new_frequent)
        k += 1

    # Filtracja itemsetów po minimalnej długości
    filtered_itemsets = {itemset: count for itemset, count in frequent_itemsets.items() if len(itemset) >= min_length}

    return filtered_itemsets


def load_transactions_from_csv(file_path):
    """Wczytuje transakcje z pliku CSV."""
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            return [
                [item.strip() for item in row if item.strip()]
                for row in reader if row
            ]
    except Exception as e:
        print(f"[BŁĄD] Wczytywanie pliku {file_path}: {e}")
        return None


FOLDER_PATH = "./dane/synthetic_data/"


def main():
    import os

    def process_file(filename, min_supp, min_length=2):
        transactions = load_transactions_from_csv(filename)
        if transactions is None:
            print(f"[ERROR] Nie udało się wczytać plik: {filename}")
            return
        frequent_itemsets = apriori_own(transactions, min_supp, min_length)
        if frequent_itemsets:
            print(f"Wyniki dla pliku: {os.path.basename(filename)}")
            print(f"Liczba znalezionych częstych itemsetów o długości >= {min_length}: {len(frequent_itemsets)}")
            # Pokazujemy do 10 itemsetów posortowanych po wsparciu malejąco
            for idx, (itemset, count) in enumerate(sorted(frequent_itemsets.items(), key=lambda x: x[1], reverse=True)):
                if idx >= 10:
                    break
                items_str = ",".join(sorted(list(itemset)))
                print(f"{items_str} [count={count}]")
            print("\n")
        else:
            print(f"Brak częstych itemsetów dla minimalnego wsparcia {min_supp} i długości >= {min_length} w pliku {os.path.basename(filename)}.\n")

    # Parametry
    min_supp = 0.01  # Proponuję podnieść z 0.005 do 0.01
    min_length = 2   # Minimalna długość itemsetów do pokazania

    file_with_itemsets = os.path.join(FOLDER_PATH, "synthetic_data_test.csv")
    file_no_itemsets = os.path.join(FOLDER_PATH, "synthetic_data_test_0itemsets.csv")

    process_file(file_with_itemsets, min_supp, min_length)
    process_file(file_no_itemsets, min_supp, min_length)


if __name__ == "__main__":
    main()
