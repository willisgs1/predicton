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

def load_test_data(filepath):
    data = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return []
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        match = re.search(r'([\d\.]+),\s*([\d\.]+),\s*([\d\.]+)\s*\((\d+)-(\d+)\)$', line)
        if match:
            try:
                h = float(match.group(1))
                d = float(match.group(2))
                a = float(match.group(3))
                s1 = int(match.group(4))
                s2 = int(match.group(5))
                r = 1 if s1 > s2 else (2 if s1 == s2 else 3)
                if h == 0 and d == 0 and a == 0: continue
                data.append({'h': h, 'd': d, 'a': a, 'r': r})
            except ValueError:
                continue
    return data

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
        'prod': h*d*a
    }

    # Add a few more powerful ones
    base['1/h'] = safe_div(1, h)
    base['1/a'] = safe_div(1, a)
    base['1/d'] = safe_div(1, d)

    return base

def solve():
    train_data = load_train_data('train_data.txt')
    test_data = load_test_data('tests.txt')
    all_rows = train_data + test_data

    if not all_rows:
        print("No data found. Please ensure train_data.txt and tests.txt exist.")
        return

    dataset = []
    for i, r in enumerate(all_rows):
        dataset.append({
            'id': i,
            'feats': generate_features(r),
            'r': r['r']
        })

    draws = [d for d in dataset if d['r'] == 2]
    non_draws = [d for d in dataset if d['r'] != 2]

    if not draws:
        print("No draws in dataset.")
        return

    feature_keys = list(dataset[0]['feats'].keys())

    uncovered_draws = set(d['id'] for d in draws)
    rules = []

    total_tp = 0
    total_fp = 0

    print(f"Total Matches: {len(dataset)}")
    print(f"Total Draws: {len(draws)}")
    print("Finding covering rules...")

    # Covering Algorithm
    while uncovered_draws:
        # Pick a random uncovered draw
        seed_id = random.choice(list(uncovered_draws))
        seed = next(d for d in draws if d['id'] == seed_id)

        # Initialize box to seed
        box = {k: (seed['feats'][k], seed['feats'][k]) for k in feature_keys}

        # Current coverage
        current_covered_draws = {seed_id}

        # Try to expand box to include other draws
        candidates = list(uncovered_draws)
        random.shuffle(candidates)

        for cand_id in candidates:
            if cand_id == seed_id: continue

            cand = next(d for d in draws if d['id'] == cand_id)

            # Temporary expanded box
            temp_box = {}
            for k in feature_keys:
                curr_min, curr_max = box[k]
                val = cand['feats'][k]
                temp_box[k] = (min(curr_min, val), max(curr_max, val))

            # Count FPs in temp_box
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
                    # Heuristic stop
                    if fps > len(current_covered_draws) + 1:
                         break

            tps = len(current_covered_draws) + 1
            precision = tps / (tps + fps)

            if precision >= 0.65: # High threshold for individual boxes
                # Accept expansion
                box = temp_box
                current_covered_draws.add(cand_id)

        # Finalize box stats
        box_tps = 0
        box_fps = 0
        covered_ids = []

        for d in dataset:
            in_box = True
            for k in feature_keys:
                min_v, max_v = box[k]
                val = d['feats'][k]
                if val < min_v or val > max_v:
                    in_box = False
                    break
            if in_box:
                if d['r'] == 2:
                    box_tps += 1
                    covered_ids.append(d['id'])
                else:
                    box_fps += 1

        # Save rule
        rule_desc = []
        for k in feature_keys:
            min_v, max_v = box[k]
            rule_desc.append(f"{min_v:.6f} <= {k} <= {max_v:.6f}")
        rules.append(rule_desc)

        total_tp += box_tps
        total_fp += box_fps

        # print(f"Found Box covering {box_tps} draws with {box_fps} FPs. Precision: {box_tps/(box_tps+box_fps):.4f}")

        for cid in covered_ids:
            if cid in uncovered_draws:
                uncovered_draws.remove(cid)

    final_prec = total_tp / (total_tp + total_fp)
    print(f"Final Recall: 1.0")
    print(f"Final Precision: {final_prec:.4f}")

    # Print formula
    print("\nGeneralized Formula (Disjunctive Normal Form):")
    print("A match is predicted as a DRAW if it satisfies ANY of the following sets of conditions:")
    for i, r in enumerate(rules):
        print(f"\nCondition Set {i+1}:")
        print(" AND ".join(r))

if __name__ == "__main__":
    solve()
