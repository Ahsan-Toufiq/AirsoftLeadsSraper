import csv

INPUT_FILE = "all.csv"
OUTPUT_FILE = "final.csv"

seen = set()

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header)  # write header to output

    for row in reader:
        first_column = row[0].strip()
        if first_column not in seen:
            seen.add(first_column)
            writer.writerow(row)

print(f"✅ Deduplicated file saved as: {OUTPUT_FILE}")
