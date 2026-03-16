import re
import csv

def parse_line(line):
    # Match: [Optional *] Team A - Team B Odds1, OddsX, Odds2 (Score)
    # Example: Racing Club - Tigre 1.67, 3.29, 4.84 (0-0)
    # Example: * FC Kaiserslautern - Dynamo Dresden 1.95, 3.50, 3.40 (3-1)
    # Use \s* to handle potential extra spaces and commas optional or space-separated
    match = re.search(r'(?:[*]\s*)?(.*?)\s+([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)\s+\((\d+)-(\d+)\)', line)
    if match:
        teams = match.group(1).strip()
        try:
            odds1 = float(match.group(2))
            oddsX = float(match.group(3))
            odds2 = float(match.group(4))
            score1 = int(match.group(5))
            score2 = int(match.group(6))
        except ValueError:
            return None

        # Filter out invalid odds
        if odds1 <= 0 or oddsX <= 0 or odds2 <= 0:
            return None

        is_draw = 1 if score1 == score2 else 0
        return [teams, odds1, oddsX, odds2, score1, score2, is_draw]
    return None

def main():
    with open('tests.txt', 'r') as f:
        lines = f.readlines()

    data = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('test') or line.startswith('Test'):
            continue
        parsed = parse_line(line)
        if parsed:
            data.append(parsed)

    with open('data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['teams', 'odds1', 'oddsX', 'odds2', 'score1', 'score2', 'is_draw'])
        writer.writerows(data)

    print(f"Parsed {len(data)} matches.")

if __name__ == "__main__":
    main()
