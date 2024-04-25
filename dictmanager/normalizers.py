def normalizeToAscii(inputstr: str) -> str:
    """
    normalizes input string by lowercasing, replacing certain umlauts and removing punctuation.
    """
    x = inputstr.casefold()
    x = x.replace("ö", "oe")
    x = x.replace("ä", "ae")
    x = x.replace("ü", "ue")
    x = x.replace("ß", "ss")
    x = x.replace("\n", "")
    x = x.replace("-", "")
    x = x.replace(" ", "")
    x = x.replace(".", "")
    x = x.replace(":", "")
    x = x.replace(",", "")

    x = x.replace("â", "a")
    x = x.replace("à", "a")
    x = x.replace("á", "a")

    x = x.replace("é", "e")
    x = x.replace("ê", "e")
    x = x.replace("è", "e")
    x = x.replace("ë", "e")

    x = x.replace("í", "i")
    x = x.replace("ì", "i")
    x = x.replace("î", "i")

    x = x.replace("ó", "o")
    x = x.replace("ò", "o")
    x = x.replace("ô", "o")

    x = x.replace("ù", "u")
    x = x.replace("ú", "u")
    x = x.replace("û", "u")

    x = x.replace("ñ", "n")
    x = x.replace("ã", "a")

    x = x.replace("ç", "c")

    x = x.replace("ç", "c")
    x = x.replace("å", "a")
    x = x.replace("ï", "i")
    x = x.replace("ø", "o")
    x = x.replace("æ", "ae")
    x = x.replace(")", "")
    x = x.replace("(", "")
    x = x.replace("/", "")

    if not x.isascii():
        return ""
    if not x.isalnum():
        print(x)
        assert False
    # assert x.isalnum()

    # for prefix in COMMONPREFIXES:
    #        x = x.removeprefix(prefix)

    return x
