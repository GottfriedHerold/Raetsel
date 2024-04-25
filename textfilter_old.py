from dictmanager import DictSpecification, UnfilteredDict, normalizeToAscii

NGERMAN = DictSpecification("/usr/share/dict/ngerman", normalizer=normalizeToAscii)

DEFAULTDICTS = [NGERMAN]

DICTFILE = "/usr/share/dict/ngerman"
# DORTMUNDFILE = "/home/gottfried/HstDortmund.txt"
NUERNBERGDICT = "Nuernberg/Haltestellen_VGN.txt"


COMMONPREFIXES = ["fuerth", "nuernberg"]



def createfromname(dictfilename:str, encoding = None) -> list[str]:
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

def apply_filter(L:list[str], fun) -> list[str]:
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
    creates a patternfilter: patterns "ab.bba" matches everything where all occurrences of a and b stand for the same letters.
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

#VGN = createfromname(NUERNBERGDICT)

# DICT = createfromname(DICTFILE)
# BIGDICT = createfromname("german.dic", "latin-1")

#d = filter(BIGDICT, positionfilter(1,"a"))
#d = filter(d, positionfilter(3,"h"))
#d = filter(d, positionfilter(8,"e"))

#print(len(DICT))
#print(len(BIGDICT))
# c = filter(DICT, containfilter("agav"))
