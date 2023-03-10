DICTFILE = "/usr/share/dict/ngerman"
DORTMUNDFILE = "/home/gottfried/HstDortmund.txt"

def normalizeEntry(inputstr: str) -> str:
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


    if not x.isascii():
        return ""
    assert x.isalnum()
    return x


def createfromname(dictfilename:str, encoding = None):
    """
    Loads dict from file
    """
    with open(dictfilename, "r", encoding=encoding) as f:
        L = f.readlines()
        out = []
        for entry in L:
            x = normalizeEntry(entry)
            if x:
                out += [x]
    return out

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
assert (len(ALPHABET) == 26)

def maketable(s: str) -> dict[str, int]:
    """
    Creates a dict letter -> number of occurences from a given string
    """
    ret = {}
    for c in ALPHABET:
        ret[c] = s.count(c)
    return ret

def filter(L:list[str], fun) -> list[str]:
    """
    filters a given list by applying the given filter fun
    """
    out = []
    for l in L:
        if fun(l):
            out += [l]
    return out

def lengthfilter(i: int):
    """
    Returns a filter that only keeps strings of a certain length
    """
    def newfilter(s:str) -> bool:
        return len(s) == i
    return newfilter

def containfilter(entries:str, allowed_errors: int = 0):
    """
    Creates a filter that only retains strings s, for which entries <= s is a substring up to permutation and at most allowed_errors.
    Useful for solving anagrams with partial imperfect knowledge
    """
    infilter = maketable(entries)
    def newfilter(s: str) -> bool:
        actual_errors = 0
        occurences = maketable(s)
        for c in ALPHABET:
            if infilter[c] > occurences[c]:
                actual_errors += infilter[c] - occurences[c]
                if actual_errors > allowed_errors:
                    return False
        return True
    return newfilter

def patternfilter(pattern:str):
    """
    creates a patternfilter: patterns "ab.bba" matches everything where all occurances of a and b stand for the same letters.
    . means ignore
    ending with a dollar means that arbitrary chars follow.
    """
    L = len(pattern)
    assert L > 0
    endsWithDollar = (pattern[-1]=="$")
    def newfilter(s: str) -> bool:
        if len(s) < L:
            return False
        if len(s) > L and (not endsWithDollar):
            return False
        symbolmap: dict[str, str] = {}
        for i in range(len(s)):
            if pattern[i] == ".":
                continue
            if pattern[i] == "$":
                return True
            if pattern[i] in symbolmap:
                if s[i] != symbolmap[pattern[i]]:
                    return False
            else:
                symbolmap[pattern[i]] = s[i]
        return True
    return newfilter

def positionfilter(position:int, options:str):
    """
    creates a filter that ensures that at a given postion, only the chars from option may occur
    NOTE: position is 1-indexed!
    """
    def newfilter(s: str) -> bool:
        if len(s) < position:
            return False
        return s[position-1] in options
    return newfilter


# USAGE example
# d = createfromname(DICTFILE)
# d = filter(d, lengthfilter(8))
# d = filter(d, containfilter("abba",1))
# print(d)

DICT = createfromname(DICTFILE)
BIGDICT = createfromname("german.dic", "latin-1")

#d = filter(BIGDICT, positionfilter(1,"a"))
#d = filter(d, positionfilter(3,"h"))
#d = filter(d, positionfilter(8,"e"))

#print(len(DICT))
#print(len(BIGDICT))
# c = filter(DICT, containfilter("agav"))