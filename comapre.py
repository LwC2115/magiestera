import csv
import time
import tracemalloc
import os
from fim import fpgrowth, apriori, eclat
from statistics import mean

from apriori_own import apriori_own
from eclat import eclat as own_eclat, preprocess
from own import build_fptree, find_frequent_patterns

FILE_PATH = "./dane/synthetic_data/synthetic_data_bazowy.csv"

SUPPORT_THRESHOLD = 0.4

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


def run_algorithm(name, func, transactions, support):
    """Uruchamia algorytm wielokrotnie i zwraca średnie metryki."""
    times, memories, itemsets_counts = [], [], []
    try:
                tracemalloc.start()
                start_time = time.time()
                # Dostosowanie wywołania dla własnych implementacji:
                if name == "Apriori_Own":
                    result = func(transactions, support)
                    count_result = len(result)
                elif name == "Eclat_Own":
                    data=preprocess(transactions)
                    minsup_count = int(support * len(transactions))

                    result_dict = func([],sorted(data.items(), key=lambda item: len(item[1]), reverse=True), minsup_count)
                    count_result = len(result_dict)
                elif name == "FPGrowth_Own":
                    # Budujemy drzewo i znajdujemy wzorce
                    tree, header = build_fptree(transactions, support)
                    patterns = find_frequent_patterns(tree, header, support,len(transactions))
                    count_result = len(patterns)
                else:
                    result = func(transactions, supp=support * 100)
                    count_result = len(result)
                end_time = time.time()
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                times.append(end_time - start_time)
                memories.append(peak / (1024 * 1024))  # MB
                itemsets_counts.append(count_result)
    except Exception as e:
                print(f"[BŁĄD] Podczas działania {name}: {e}")
                return None
    return {
        "algorithm": name,
        "avg_time": mean(times),
        "avg_memory": mean(memories),
        "avg_itemsets": mean(itemsets_counts)
    }

def save_results_to_csv(file_name, support, results):
    """Zapisuje wyniki do pliku CSV."""
    output_path = f"result_compare_algorythm_{support:.2f}.csv"
    write_header = not os.path.exists(output_path)
    with open(output_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["Plik", "Algorytm", "Sr. czas (s)", "Sr. pamiec (MB)", "Sr. liczba zbiorow"])
        for res in results:
            if res:
                writer.writerow([
                    file_name,
                    res["algorithm"],
                    f"{res['avg_time']:.4f}",
                    f"{res['avg_memory']:.2f}",
                    f"{res['avg_itemsets']:.0f}"
                ])
        writer.writerow([])

def main():
    transactions = load_transactions_from_csv(FILE_PATH)
    if not transactions:
        print(f"[BŁĄD] Nie udało się wczytać pliku {FILE_PATH}")
        return
    
    print(f"Test na pliku: {FILE_PATH} przy progu wsparcia: {SUPPORT_THRESHOLD:.2f}")
    results = []
    results.append(run_algorithm("FPGrowth", fpgrowth, transactions, SUPPORT_THRESHOLD))
    results.append(run_algorithm("Apriori", apriori, transactions, SUPPORT_THRESHOLD))
    results.append(run_algorithm("Eclat", eclat, transactions, SUPPORT_THRESHOLD))
    
      # Twoje własne implementacje
    results.append(run_algorithm("Apriori_Own", apriori_own, transactions, SUPPORT_THRESHOLD))
    results.append(run_algorithm("Eclat_Own", own_eclat, transactions, SUPPORT_THRESHOLD))
    results.append(run_algorithm("FPGrowth_Own", build_fptree, transactions, SUPPORT_THRESHOLD))

    save_results_to_csv(os.path.basename(FILE_PATH), SUPPORT_THRESHOLD, results)
    print("Wyniki zapisane do pliku.")

if __name__ == "__main__":
    main()
