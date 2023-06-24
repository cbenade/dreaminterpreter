from bs4 import BeautifulSoup
import re
import json


def main() -> None:
    start_char, end_char = 'a', 'z'
    chars = [chr(c) for c in range(ord(start_char), ord(end_char) + 1)]
    raw_char_data = get_raw_char_data(chars)
    scrubbed_char_data = scrub_raw_char_data(raw_char_data)
    amended_char_data = amend_scrubbed_char_data(chars, scrubbed_char_data)
    verify_amended_char_data(chars, amended_char_data)
    data_dict = build_data_dictionary(chars, amended_char_data)
    json_object = json.dumps(data_dict, indent=4)
    with open("data.json", "w") as file:
        file.write(json_object)
    return


def get_raw_char_data(chars: list[str]) -> list:
    raw_char_data = []
    for char in chars:
        soup = None
        with open(f"data/{char}.txt", "r") as file:
            soup = BeautifulSoup(file, "html.parser")
        html_data_table = soup.find(attrs={"width": "750", "valign": "top"}) # attrs={"height": "2340"}
        soup = BeautifulSoup(str(html_data_table), "html.parser")
        html_data_table_entries = soup.find_all("font") # attrs={"face": "Arial"}
        raw_char_data.append([str(e) for e in html_data_table_entries])
    return raw_char_data


def scrub_raw_char_data(raw_char_data: list) -> list:
    scrubbed_data = []
    for char_data_list in raw_char_data:
        clean_data = []
        for entry in char_data_list:
            entry = scrub_entry(entry)
            if len(entry) == 0: continue
            clean_data.append(entry) # duplicates should be added due to fragmented entries
        scrubbed_data.append(clean_data)
    return scrubbed_data


def scrub_entry(entry: str) -> str:
    entry = re.sub("\<.*?\>", "", entry)
    entry = entry.replace("\\n", " ")
    for repl in ["&nbsp;", "TOP", "\\"]:
        entry = entry.replace(repl, "")
    entry = ' '.join(entry.split()) # remove duplicated whitespace
    if any([entry.find(s) != -1 for s in ["function()", "googletag", "A B C D E"]]):
        return ""
    return entry


def amend_scrubbed_char_data(chars: list[str], scrubbed_char_data: list) -> list:
    amended_char_data = []
    for char_index in range(len(chars)):
        char = chars[char_index]
        scrubbed_entries = scrubbed_char_data[char_index]

        # first pass for keys
        i, j = 0, 1
        while j < len(scrubbed_entries):
            curr = scrubbed_entries[i]
            next = scrubbed_entries[j]
            if is_potential_key(curr) and is_potential_key(next):
                if next in curr: # duplicated string or substring
                    del scrubbed_entries[j]
                elif next[0].islower() or next.isupper(): # second part merges acronyms
                    scrubbed_entries[i] = f"{curr}{next}"
                    del scrubbed_entries[j]
                elif next[0].isupper():
                    scrubbed_entries[i] = f"{curr} {next}"
                    del scrubbed_entries[j]
                elif is_key(char, curr): # jalapeno fix
                    scrubbed_entries[i] = f"{curr}{next}"
                    del scrubbed_entries[j]
                else:
                    raise Exception(f"Back-to-back keys found but without solution:\n\t1: ({curr})\n\t2: ({next})")
                continue
            elif not is_potential_key(next):
                if next in curr:
                    del scrubbed_entries[j]
                    continue
            i, j = j, j + 1

        # second pass for substrings
        i, j = 0, 1
        while j < len(scrubbed_entries):
            curr = scrubbed_entries[i]
            next = scrubbed_entries[j]
            if not is_key(char, curr) and not is_key(char, next):
                if next in curr:
                    del scrubbed_entries[j]
                    continue
            i, j = j, j + 1

        # final cleanup
        while "To see" not in scrubbed_entries[1]:
            del scrubbed_entries[0]
        scrubbed_entries[0] = char.upper()
        i = 0
        while i < len(scrubbed_entries):
            if "Page 1" not in scrubbed_entries[i]:
                i += 1
                continue
            scrubbed_entries = scrubbed_entries[0:i]
            break
        i = 0
        for i in range(len(scrubbed_entries)):
            if not is_key(char, scrubbed_entries[i]) and scrubbed_entries[i][-1] != ".":
                scrubbed_entries[i] = f"{scrubbed_entries[i]}."

        amended_char_data.append(scrubbed_entries)

    return amended_char_data


def is_potential_key(entry: str) -> bool: # includes key fragments, depends on previous
    max_key_len = 5
    key_len = len(entry.split())
    first_letter = entry[0]
    return not (not first_letter.isalpha() or "To see" in entry) and (key_len <= max_key_len) # reject first_letters "*" and "." specifically


def is_key(char: str, entry: str) -> bool:
    max_key_len = 5
    key_len = len(entry.split())
    first_letter = entry[0]
    return key_len <= max_key_len and first_letter.isupper() and first_letter.lower() == char


def verify_amended_char_data(chars: list[str], amended_char_data: list) -> None:
    for char_index in range(len(chars)):
        char = chars[char_index]
        amended_entries = amended_char_data[char_index]
        i, j = 0, 1
        while j < len(amended_entries):
            curr = amended_entries[i]
            next = amended_entries[j]
            if is_key(char, curr) and is_key(char, next):
                raise Exception(f"Back-to-back keys found during verification:\n\t1: ({curr})\n\t2: ({next})")
            if is_key(char, curr) and curr[0].lower() != char:
                raise Exception(f"Key ({curr}) doesn't start with correct character ({char}), next is ({next})")
            i, j = j, j + 1
        if not is_key(char, amended_entries[0]):
                raise Exception(f"Amended data for character ({char}) begins with a value: ({amended_entries[0]})")
        if is_key(char, amended_entries[-1]):
                raise Exception(f"Amended data for character ({char}) ends with a key: ({amended_entries[-1]})")
    return


def build_data_dictionary(chars: list[str], amended_char_data: list) -> dict:
    dict = {}
    for char_index in range(len(chars)):
        char = chars[char_index]
        amended_entries = amended_char_data[char_index]
        i, j = 0, 1
        while i < len(amended_entries) - 1:
            curr = amended_entries[i]
            if not is_key(char, curr):
                i += 1
                continue
            j = i + 1
            while j < len(amended_entries) and not is_key(char, amended_entries[j]):
                j += 1
            key = curr.lower().replace("'", "") # all keys entered as lowercase for now
            value = ""
            for k in range(i+1, j):
                value += f"- {amended_entries[k]}\n\n" # values currently stitched together by dual newline characters
            value = value.rstrip("\n\n")
            dict[key] = value
            i = j
    return dict


if __name__ == "__main__":
    main()
