import json
from os import get_terminal_size


def main() -> None:
    data_dict = None
    with open('data.json', 'r') as file:
        data_dict = json.load(file)
    ref_keys = set(data_dict.keys())
    queries = get_dream_queries("Tell me your dream")
    matches = get_query_matches(queries, ref_keys)
    if len(matches[0]) == 0 and len(matches[1]) == 0:
        print("No matches found!", end="\n\n")
        return
    divider = get_terminal_size().columns * "~"
    while True:
        print_matches(matches)
        symbol = input("Which symbol would you like to hear more about?\n\t").lower().lstrip().rstrip()
        print(f"\n{divider}")
        if len(symbol) == 0:
            print(f"Goodbye!\n{divider}", end="\n\n")
            break
        if symbol in data_dict:
            print(f"{symbol.capitalize()} Description\n{divider}\n{data_dict[symbol]}\n{divider}", end="\n\n")
        else:
            nearest_matches = get_nearest_matches(symbol, data_dict)
            print(f"Symbol \"{symbol}\" couldn't be found, but here are the nearest matches\n\t{nearest_matches}\n{divider}", end="\n\n")
    return


def get_dream_queries(prompt: str) -> set:
    query = input(f"\n{prompt}\n\t").lower()
    print()
    dream_queries = set(query.lower().replace("'", "").split())
    add_queries = set()
    for query in dream_queries:
        if query[-1] == "s":
            add_queries.add(query[0:-1])
        else:
            add_queries.add(f"{query}s")
        if len(query) > 3 and query[-3:] == "ies":
            add_queries.add(f"{query[0:-3]}y")
        if len(query) > 3 and query[-3:] == "ing":
            add_queries.add(query[0:-3])
    dream_queries.update(add_queries)
    return dream_queries


def get_query_matches(queries: set, ref_keys: set) -> dict:
    matches = {0: set(), 1: set()}
    min_substring_length = 4
    for query in queries:
        for key in ref_keys:
            if query == key:
                if len(query) > 1:
                    matches[0].add(key)
                else:
                    matches[1].add(key)
            elif query in key and len(query) >= min_substring_length:
                matches[1].add(key)
    matches[0] = sorted(matches[0])
    matches[1] = sorted(matches[1])
    return matches


def print_matches(matches: dict) -> None:
    print(f"I found the following symbols in your dream!\n\t{matches[0]}", end="\n\n")
    print(f"These symbols may also be relevant\n\t{matches[1]}", end="\n\n")
    return


def get_nearest_matches(symbol: str, data_dict: dict) -> list:
    limited_keys = [key for key in data_dict.keys() if key[0] == symbol[0]]
    n = len(limited_keys)
    max_sub_size = 3
    k = min(len(symbol), max_sub_size)
    sub = symbol[0:k]
    i = 0
    while i < n:
        if sub in limited_keys[i][0:k]:
            break
        i += 1
    num_nearest_matches = 10
    end = min(i + num_nearest_matches, n)
    nearest_matches = limited_keys[i:end]
    return nearest_matches


if __name__ == "__main__":
    main()
