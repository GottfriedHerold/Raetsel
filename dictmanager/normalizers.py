
def normalizeToAscii(inputstr: str) -> list[str]:
    out = [inputstr]
    if "/" in inputstr:
        out += inputstr.split("/")
    if " " in inputstr:
        out += inputstr.split(" ")

    real_out = []
    for w in out:
        real_out += normalizeToAscii2(w)
    return real_out



def normalizeToAscii2(inputstr: str) -> list[str]:
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
    x = x.replace("+", "")

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

    if len(x) == 0:
        return []

    if not x.isascii():
        return ""
    if not x.isalnum():
        print(f"Failing string {x} of length {len(x)}.")
        assert False
    # assert x.isalnum()

    # for prefix in COMMONPREFIXES:
    #        x = x.removeprefix(prefix)

    return [x]

def normalizeStreets(inputstr: str) -> str | list[str]:
    inputs_normalized = normalizeToAscii(inputstr)

    if not inputstr:
        return []

    out = inputs_normalized[:]

    for normalized_input in inputs_normalized:
        # Note "X" cannot appear in normalized_input, because the latter is lower-cased.
        if normalized_input.endswith("strasse"):
            out += [(normalized_input+"X").replace("strasseX", "str")]
        if normalized_input.endswith("str"):
            out += [(normalized_input + "X").replace("strX", "strasse")]

        if normalized_input.endswith("hbf"):
            out += [(normalized_input + "X").replace("hbfX", "hauptbahnhof")]

        if normalized_input.endswith("hauptbahnhof"):
            out += [(normalized_input + "X").replace("hauptbahnhofX", "hbf")]

        if normalized_input.endswith("bf"):
            out += [(normalized_input + "X").replace("bfX", "bahnhof")]

        if normalized_input.endswith("bahnhof"):
            out += [(normalized_input + "X").replace("bahnhofX", "bf")]

    return out