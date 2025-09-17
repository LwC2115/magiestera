import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules, apriori
import csv

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

transactions = load_transactions_from_csv(r"E:\mgr\dane\data\bazowy_transactions.csv")


# Kodowanie transakcji na macierz 0-1
encoder = TransactionEncoder()
encoded_data = encoder.fit_transform(transactions)
df = pd.DataFrame(encoded_data, columns=encoder.columns_)

# Generowanie częstych zestawów przedmiotów z minimalnym wsparciem 0.4
frequent_itemsets = fpgrowth(df, min_support=0.4, use_colnames=True)

# Wyświetl częste zestawy
print("Częste zestawy przedmiotów:")
print(len(frequent_itemsets))

from fim import fpgrowth

patterns_fim = fpgrowth(transactions, supp=40)  # 40% support
print("# fim:", len(patterns_fim))

