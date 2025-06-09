import re
import csv

INPUT_RAW  = "divina_commedia_raw.csv"
OUTPUT_CSV = "divina_commedia.csv"

def split_orig_terzets(raw_orig: str):
    """
    Split the raw Original for a canto into (N, block) pairs.

    1. Find all standalone integers (\b\d{1,3}\b). Let matches = [m0, m1, ..., mK].
    2. The text before m0.start() is Terzetto N0 (where N0=int(m0.group(1))).
    3. For i in 1..K-1, slice from matches[i-1].end() to matches[i].start(); that text is Terzetto Ni.
    4. If the final match mK has no text after mK.end(), merge it into the previous block instead of creating an empty block.
    """
    s = raw_orig
    matches = list(re.finditer(r"\b(\d{1,3})\b", s))
    result = {}

    if not matches:
        return result

    # First terzetto: text before matches[0]
    first_num = int(matches[0].group(1))
    block0 = s[: matches[0].start() ].strip()
    if block0:
        result[first_num] = block0

    # Middle terzetti
    for i in range(1, len(matches)):
        N = int(matches[i].group(1))
        prev_end = matches[i-1].end()
        this_start = matches[i].start()
        blk = s[prev_end:this_start].strip()
        if blk:
            result[N] = blk

    # Check final match: if it has text after it, capture that too; otherwise merge with its predecessor
    final_index = len(matches) - 1
    final_num = int(matches[final_index].group(1))
    final_end = matches[final_index].end()
    tail = s[final_end:].strip()
    if tail:
        # Normal case: there is text after final number → treat as its block
        result[final_num] = tail
    else:
        # Hanging final number: merge into the previous block if any
        if final_index > 0:
            prev_num = int(matches[final_index - 1].group(1))
            prev_text = result.get(prev_num, "")
            # Append nothing (no extra text), so effectively no change
            result[prev_num] = prev_text
        # If it's the only number and nothing after, drop it entirely.

    return result

def split_trans_terzets(raw_trans: str):
    """
    Split the raw Translation for a canto into (N, block) pairs.

    1. Find all markers (\b\d{1,3}\.\s) via re.finditer.
    2. For each i from 0..K-2, N_i = int(matches[i].group(1)), block_i = text from matches[i].end() to matches[i+1].start().
    3. For the final match mK-1, slice from mK-1.end() to end of string. If empty, merge into previous.
    """
    s = raw_trans
    matches = list(re.finditer(r"\b(\d{1,3})\.\s", s))
    result = {}

    if not matches:
        return result

    # Middle and first terzetti
    for i in range(len(matches) - 1):
        N = int(matches[i].group(1))
        start_idx = matches[i].end()
        end_idx = matches[i+1].start()
        blk = s[start_idx:end_idx].strip()
        if blk:
            result[N] = blk

    # Final match
    final_index = len(matches) - 1
    final_num = int(matches[final_index].group(1))
    final_start = matches[final_index].end()
    tail = s[final_start:].strip()
    if tail:
        result[final_num] = tail
    else:
        # Merge into previous if it exists
        if final_index > 0:
            prev_num = int(matches[final_index - 1].group(1))
            prev_text = result.get(prev_num, "")
            result[prev_num] = prev_text
        # Else drop it.

    return result

def clean_block_text(text: str) -> str:
    """
    Clean a single block (Original or Translation):
     - Remove parentheses and their contents: r"\([^)]*\)"
     - Fix hyphen+newline: r"-\s*\n\s*" → ""
     - Convert newlines to spaces
     - Collapse whitespace to single space
    """
    t = re.sub(r"\([^)]*\)", "", text)
    t = re.sub(r"-\s*\n\s*", "", t)
    t = t.replace("\r", "\n").replace("\n", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t

def process_canto(book: str, canto: str, raw_orig: str, raw_trans: str):
    """
    1) Split raw_orig into orig_map: {N: raw_verses}
    2) Split raw_trans into trans_map: {N: raw_prose}
    3) Clean each block
    4) Yield (book, canto, N, cleaned_orig, cleaned_trans) for each N in sorted(orig_map) if also in trans_map
    """
    orig_map = split_orig_terzets(raw_orig)
    trans_map = split_trans_terzets(raw_trans)

    for N in sorted(orig_map.keys()):
        if N not in trans_map:
            continue
        o_blk = clean_block_text(orig_map[N])
        t_blk = clean_block_text(trans_map[N])
        yield (book, canto, N, o_blk, t_blk)

def main():
    with open(INPUT_RAW, encoding="utf-8") as inf:
        reader = csv.DictReader(inf)

        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as outf:
            writer = csv.writer(outf)
            writer.writerow(["Cantico", "Canto", "Terzetto", "Original", "Translation"])

            count = 0
            for row in reader:
                book      = row["Cantico"].strip()
                canto     = row["Canto"].strip()
                raw_orig  = row["Original"]
                raw_trans = row["Translation"]

                for rec in process_canto(book, canto, raw_orig, raw_trans):
                    writer.writerow(rec)
                    count += 1

            print(f"Written {count - 1} rows")

    print(f"\nCompleted. Output written to “{OUTPUT_CSV}”.\n")

if __name__ == "__main__":
    main()
