from collections import defaultdict
import csv

class FPNode:
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None

    def increment(self, count):
        self.count += count

def print_tree(node, indent=0):
    if node.item is not None:
        print('  ' * indent + f"{node.item} ({node.count})")
    for child in node.children.values():
        print_tree(child, indent + 1)

def build_fptree(transactions, min_support):
    if not transactions or not (0 <min_support <=1):
        return None, None 
    min_count = len(transactions) * min_support
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    item_counts = {item: count for item, count in item_counts.items() if count >= min_count}
    if not item_counts:
        return None, None
    header_table = {item: [count, None] for item, count in item_counts.items()}
    root = FPNode(None, 1, None)
    for transaction in transactions:
        sorted_items = [item for item in sorted(transaction, key=lambda x: (item_counts.get(x, 0), x), reverse=True) if item in item_counts]
        if sorted_items:
            insert_tree(sorted_items, root, header_table)

    return root, header_table

def insert_tree(items, node, header_table):
    first_item = items[0]
    if first_item in node.children:
        node.children[first_item].increment(1)
    else:
        new_node = FPNode(first_item, 1, node)
        node.children[first_item] = new_node
        update_header_table(new_node, header_table[first_item])


    if len(items) > 1:
        insert_tree(items[1:], node.children[first_item], header_table)

def update_header_table(node, header_entry):
    if header_entry[1] is None:
        header_entry[1] = node
    else:
        current = header_entry[1]
        while current.link is not None:
            current = current.link
        current.link = node

def find_frequent_patterns(tree, header_table, min_support, num_transactions, prefix=set()):
    patterns = {}
    min_count = int(num_transactions * min_support)
    for item, (count, node) in sorted(header_table.items(), key=lambda x: x[1][0]):
        new_prefix = prefix | {item}
        if count >= min_count:
            patterns[frozenset(new_prefix)] = count

        conditional_patterns = []
        while node is not None:
            path = []
            parent = node.parent
            while parent is not None and parent.item is not None:
                path.append(parent.item)
                parent = parent.parent
            for _ in range(node.count):
                conditional_patterns.append(path)
            node = node.link

        subtree, sub_header = build_fptree(conditional_patterns, min_support)
        if subtree is not None:
            sub_patterns = find_frequent_patterns(subtree, sub_header, min_support, num_transactions, new_prefix)
            patterns.update(sub_patterns)
    
    return patterns
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

transactions = load_transactions_from_csv(r"E:\mgr\dane\synthetic_data\synthetic_data_bazowy.csv")

# Minimalne wsparcie
min_sup = 0.4

# Budowanie drzewa FP i znalezienie częstych wzorców
fp_tree, header_table = build_fptree(transactions, min_sup)
patterns = find_frequent_patterns(fp_tree, header_table, min_sup, len(transactions))
for itemset, count in patterns.items():
    if count < int(len(transactions) * 0.4):
        print(itemset, count)  # nie powinny się pojawić!

