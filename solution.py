import csv
import sys
import re
import math
import random
from collections import defaultdict

random.seed(42)

# ----------------- DATA LOADING -----------------

def load_train_data(filepath):
    data = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    h = float(row['home'])
                    d = float(row['draw'])
                    a = float(row['away'])
                    r = int(row['results'])
                    if h == 0 and d == 0 and a == 0: continue
                    data.append({'h': h, 'd': d, 'a': a, 'r': r})
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return []
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []
    return data

def load_test_datasets(filepath):
    """
    Parses tests.txt into a dictionary of datasets:
    {
        'Test 1': [...],
        'Test 2': [...],
        ...
    }
    """
    datasets = {}
    current_dataset_name = None
    current_rows = []

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return {}
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for header
        # Headers seem to look like "test 1 82 matches" or "Test 4 (matches 79)"
        # Regex to detect these headers
        header_match = re.match(r'^(?:test|Test)\s*(\d+).*', line)
        if header_match:
            # If we were collecting rows for a previous dataset, save them
            if current_dataset_name:
                datasets[current_dataset_name] = current_rows

            current_dataset_name = f"Test {header_match.group(1)}"
            current_rows = []
            continue

        # Parse match row
        # Pattern: Team A - Team B 1.67, 3.29, 4.84 (0-0)
        match_data = re.search(r'([\d\.]+),\s*([\d\.]+),\s*([\d\.]+)\s*\((\d+)-(\d+)\)$', line)
        if match_data:
            try:
                h = float(match_data.group(1))
                d = float(match_data.group(2))
                a = float(match_data.group(3))
                s1 = int(match_data.group(4))
                s2 = int(match_data.group(5))
                r = 1 if s1 > s2 else (2 if s1 == s2 else 3)

                if h == 0 and d == 0 and a == 0: continue

                current_rows.append({'h': h, 'd': d, 'a': a, 'r': r})
            except ValueError:
                continue

    # Save last dataset
    if current_dataset_name:
        datasets[current_dataset_name] = current_rows

    return datasets

# ----------------- FEATURE GENERATION -----------------

def safe_div(x, y):
    return x / y if abs(y) > 1e-9 else 0

def safe_sqrt(x):
    return math.sqrt(x) if x > 0 else 0

def generate_features(row):
    h, d, a = row['h'], row['d'], row['a']

    base = {
        'h': h, 'd': d, 'a': a,
        'diff_ha': h - a,
        'abs_diff_ha': abs(h - a),
        'mean': (h+d+a)/3,
        'max': max(h, d, a),
        'min': min(h, d, a),
        'margin': 1/h + 1/d + 1/a if h and d and a else 0,
        'r_hd': safe_div(h, d),
        'r_ha': safe_div(h, a),
        'r_da': safe_div(d, a),
        'd_minus_geo_ha': d - safe_sqrt(h*a),
        'prod': h*d*a,
        '1/h': safe_div(1, h),
        '1/a': safe_div(1, a),
        '1/d': safe_div(1, d)
    }
    return base

# ----------------- SOLVER -----------------

def solve():
    train_rows = load_train_data('train_data.txt')
    test_datasets = load_test_datasets('tests.txt')

    if not train_rows and not test_datasets:
        print("No data found.")
        return

    # Combine all data for training the formula
    all_rows = train_rows[:]
    for rows in test_datasets.values():
        all_rows.extend(rows)

    # Prepare full dataset for rule finding
    full_dataset = []
    for i, r in enumerate(all_rows):
        full_dataset.append({
            'id': i,
            'feats': generate_features(r),
            'r': r['r']
        })

    draws = [d for d in full_dataset if d['r'] == 2]
    non_draws = [d for d in full_dataset if d['r'] != 2]

    if not draws:
        print("No draws in full dataset.")
        return

    print("Training formula on ALL data (Train + Tests 1-6)...")
    print(f"Total Matches: {len(full_dataset)}")
    print(f"Total Draws: {len(draws)}")

    feature_keys = list(full_dataset[0]['feats'].keys())
    uncovered_draws = set(d['id'] for d in draws)
    rules = []

    # Covering Algorithm (Same as before)
    while uncovered_draws:
        seed_id = random.choice(list(uncovered_draws))
        seed = next(d for d in draws if d['id'] == seed_id)

        box = {k: (seed['feats'][k], seed['feats'][k]) for k in feature_keys}
        current_covered_draws = {seed_id}

        candidates = list(uncovered_draws)
        random.shuffle(candidates)

        for cand_id in candidates:
            if cand_id == seed_id: continue
            cand = next(d for d in draws if d['id'] == cand_id)

            temp_box = {}
            for k in feature_keys:
                curr_min, curr_max = box[k]
                val = cand['feats'][k]
                temp_box[k] = (min(curr_min, val), max(curr_max, val))

            fps = 0
            for nd in non_draws:
                in_box = True
                for k in feature_keys:
                    min_v, max_v = temp_box[k]
                    val = nd['feats'][k]
                    if val < min_v or val > max_v:
                        in_box = False
                        break
                if in_box:
                    fps += 1
                    if fps > len(current_covered_draws) + 1:
                         break

            tps = len(current_covered_draws) + 1
            precision = tps / (tps + fps)

            if precision >= 0.80:
                box = temp_box
                current_covered_draws.add(cand_id)

        # Save rule
        # A rule is a function that takes 'feats' and returns True/False
        rules.append(box)

        # Determine actually covered draws (exact check)
        covered_ids = []
        for d in draws:
            if d['id'] in uncovered_draws:
                in_box = True
                for k in feature_keys:
                    min_v, max_v = box[k]
                    val = d['feats'][k]
                    if val < min_v or val > max_v:
                        in_box = False
                        break
                if in_box:
                    covered_ids.append(d['id'])

        for cid in covered_ids:
            uncovered_draws.remove(cid)

    print(f"Formula generated with {len(rules)} condition sets.")

    # ----------------- EVALUATION -----------------

    def predict(row_feats, rules):
        # Disjunctive Normal Form: True if ANY box matches
        for box in rules:
            in_box = True
            for k, (min_v, max_v) in box.items():
                val = row_feats[k]
                if val < min_v or val > max_v:
                    in_box = False
                    break
            if in_box:
                return True
        return False

    def evaluate_dataset(name, rows):
        tp = 0
        fp = 0
        total_draws = 0

        for r in rows:
            feats = generate_features(r)
            prediction = predict(feats, rules)
            actual_draw = (r['r'] == 2)

            if actual_draw:
                total_draws += 1

            if prediction and actual_draw:
                tp += 1
            elif prediction and not actual_draw:
                fp += 1

        predicted_draws = tp + fp
        recall = tp / total_draws if total_draws > 0 else 0
        precision = tp / predicted_draws if predicted_draws > 0 else 0

        print(f"\nDataset: {name}")
        print(f"Total Matches: {len(rows)}")
        print(f"Total Draws (Actual): {total_draws}")
        print(f"Predicted Draws: {predicted_draws}")
        print(f"TP: {tp} | FP: {fp}")
        print(f"Recall: {recall:.4f}")
        print(f"Precision: {precision:.4f}")

    # Evaluate on Train
    evaluate_dataset("Train Data (1196)", train_rows)

    # Evaluate on Tests 1-6
    sorted_test_names = sorted(test_datasets.keys(), key=lambda x: int(x.split()[1]))
    for name in sorted_test_names:
        evaluate_dataset(name, test_datasets[name])

    # Evaluate on Combined "7 dataset" (which is essentially what we trained on)
    evaluate_dataset("Combined (Train + Tests 1-6)", all_rows)

if __name__ == "__main__":
    solve()
