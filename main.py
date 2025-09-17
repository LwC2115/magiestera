import csv
import time
import tracemalloc
import os
from fim import fpgrowth, apriori, eclat
from statistics import mean

# Parametry globalne
FOLDER_PATH = "./dane/synthetic_data/"
SUPPORT_THRESHOLDS =[0.05,0.3]#[0.01, 0.05, 0.1, 0.2, 0.3, 0.4] # Lista progów wsparcia
NUM_RUNS = 10  # Ile razy uruchamiamy każdy algorytm (średnia z pomiarów)


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


def run_algorithm_multiple_times(name, func, transactions, support, runs=10):
    """Uruchamia algorytm wielokrotnie i zwraca średnie metryki."""
    times, memories, itemsets_counts = [], [], []

    for _ in range(runs):
        try:
            tracemalloc.start()
            start_time = time.time()

            result = func(transactions, supp=support * 100)

            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            times.append(end_time - start_time)
            memories.append(peak / (1024 * 1024))  # MB
            itemsets_counts.append(len(result))
        except Exception as e:
            print(f"[BŁĄD] Podczas działania {name}: {e}")
            return None

    return {
        "algorithm": name,
        "avg_time": mean(times),
        "avg_memory": mean(memories),
        "avg_itemsets": mean(itemsets_counts)
    }


def save_results_to_csv(support, results, file_name):
    """Zapisuje wyniki do pliku CSV."""
    output_path = f"results_support_{support:.2f}.csv"
    write_header = not os.path.exists(output_path)

    with open(output_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["Plik", "Algorytm", "Sr. czas (s)", "Sr. pamięć (MB)", "Sr. liczba zbiorów"])

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
    """Główna pętla testująca pliki dla różnych progów wsparcia."""
    for support in SUPPORT_THRESHOLDS:
        print(f"\n===== TEST DLA PROGU WSPARCIA: {support:.2f} =====\n")

        for file_name in os.listdir(FOLDER_PATH):
            if not file_name.endswith('.csv'):
                continue

            file_path = os.path.join(FOLDER_PATH, file_name)
            transactions = load_transactions_from_csv(file_path)

            if not transactions:
                print(f"[POMINIĘTO] {file_name} — błąd odczytu.")
                continue

            print(f"Plik: {file_name}")

            results = []
            results.append(run_algorithm_multiple_times("FPGrowth", fpgrowth, transactions, support, NUM_RUNS))
            results.append(run_algorithm_multiple_times("Apriori", apriori, transactions, support, NUM_RUNS))
            results.append(run_algorithm_multiple_times("Eclat", eclat, transactions, support, NUM_RUNS))

            save_results_to_csv(support, results, file_name)


if __name__ == "__main__":
    main()
