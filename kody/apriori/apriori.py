import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder

# Dane w formie listy transakcji
transactions = [
    ['Chleb', 'Mleko', 'Masło'],
    ['Chleb', 'Mleko', 'Jajka'],
    ['Mleko', 'Jajka'],
    ['Chleb', 'Mleko', 'Jajka'],
    ['Chleb', 'Masło', 'Jajka']
]

# Przekształcenie listy transakcji na format binarny
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Algorytm Apriori
frequent_itemsets = apriori(df, min_support=0.4, use_colnames=True)
print("Zbiory częste (Apriori):\n", frequent_itemsets)

