import urllib.request


def main():
    for char in [chr(c) for c in range(ord('a'), ord('z') + 1)]:
        url1 = f"http://www.placeholder.com/dictionary/{char}_all.htm" # real website url omitted from public GitHub repository
        url2 = f"http://www.placeholder.com/dictionary/{char}.htm"
        doc = None
        try:
            doc = str(urllib.request.urlopen(url1).read())
        except:
            doc = str(urllib.request.urlopen(url2).read())
        with open(f"data/{char}.txt", "w") as file:
            file.write(doc)


if __name__ == "__main__":
    main()
