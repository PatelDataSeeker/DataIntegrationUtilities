# Author: Dipen Patel
# Date: 5/3/2023
# Split a large file by a repeating delimiter (e.g. HL7 MSH segment).
# Generic: set DELIMITER, INBOUND/OUTPUT folders, CHUNK_SIZE, and FILE_EXTENSIONS.

import os

# === Configure for your environment ===
INBOUND = os.environ.get("SPLIT_INBOUND", r"C:\DP-Temp\Split Test\Inbound")
OUTPUT = os.environ.get("SPLIT_OUTPUT", r"C:\DP-Temp\Split Test\Processed")
DELIMITER = "MSH|^~\\&|"   # HL7 MSH; change to any repeating string for other formats
CHUNK_SIZE = 1000          # number of segments per output file
FILE_EXTENSIONS = (".txt", ".hl7")

os.makedirs(OUTPUT, exist_ok=True)

for filename in os.listdir(INBOUND):
    if not filename.endswith(FILE_EXTENSIONS):
        continue
    input_path = os.path.join(INBOUND, filename)
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    parts = content.split(DELIMITER)
    count = 0
    batch = []

    for part in parts:
        batch.append(part)
        count += 1
        if count >= CHUNK_SIZE:
            out_path = os.path.join(OUTPUT, f"{filename}_{len(batch)}.txt")
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(DELIMITER.join(batch))
            count = 0
            batch = []

    if batch:
        out_path = os.path.join(OUTPUT, f"{filename}_{len(batch)}.txt")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(DELIMITER.join(batch))
