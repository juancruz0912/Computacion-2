
import argparse
import sys

# Arguments
parser = argparse.ArgumentParser(description="Filtra números mayores que un umbral")
parser.add_argument("--min", type=int, required=True, help="Valor mínimo")
args = parser.parse_args()

# Filter
for line in sys.stdin:
    try:
        num = int(line.strip())
        if num > args.min:
            print(num)
    except ValueError:
        continue 
