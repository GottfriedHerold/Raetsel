import re

MORSECODE: dict[str,str] = {"a": ".-",
                            "b": "-...",
                            "c": "-.-.",
                            "d": "-..",
                            "e": ".",
                            "f": "..-.",
                            "g": "--.",
                            "h": "....",
                            "i": "..",
                            "j": ".---",
                            "k": "-.-",
                            "l": ".-..",
                            "m": "--",
                            "n": "-.",
                            "o": "---",
                            "p": ".--.",
                            "q": "--.-",
                            "r": ".-.",
                            "s": "...",
                            "t": "-",
                            "u": "..-",
                            "v": "...-",
                            "w": ".--",
                            "x": "-..-",
                            "y": "-.--",
                            "z": "--..",
                            }

MORSECODE_INVERSE: dict[str, str] = {code: char for char, code in MORSECODE.items()}
assert len(MORSECODE_INVERSE) == 26

ALPHABET = "abcdefghijklmnopqrstuvwxyz".lower()

MORSE1 = "".join([c for c,m in MORSECODE.items() if len(m) ==1])
MORSE2 = "".join([c for c,m in MORSECODE.items() if len(m) ==2])
MORSE3 = "".join([c for c,m in MORSECODE.items() if len(m) ==3])
MORSE4 = "".join([c for c,m in MORSECODE.items() if len(m) ==4])

def make_morse_matches(pattern: str) -> str:
    """
    Returns the set of characters that match a certain pattern:
    We allow the following patterns:
    - single characters a-z: match exactly that character
    - *: match any character
    - strings consisting of '.', '-' and '?' match characters with fitting morse-code
      e.g. ".-?" matches r (.-.) and w (.--)
    - '1', '2', '3' and '4' match all characters with a morse-code of exactly that length
    """
    pattern = pattern.lower()
    if len(pattern) == 1 and 'a' <= pattern[0] <= 'z':
        return pattern
    elif pattern == "*":
        return ALPHABET
    elif pattern == "1":
        return MORSE1
    elif pattern == "2":
        return MORSE2
    elif pattern == "3":
        return MORSE3
    elif pattern == "4":
        return MORSE4
    else:
        assert 1 <= len(pattern) <= 4
        for c in pattern:
            assert c in ".-?"
        morseregexp = re.compile(pattern.replace('.', '[.]').replace("?", "."))
        return "".join(c for c,m in MORSECODE.items() if morseregexp.fullmatch(m))

def to_morse(s: str) -> str:
    """
    translates input string into morse code
    """
    return " ".join([MORSECODE[c] for c in s.lower()])

def from_morse(s: str) -> str:
    """
    translate morse code (separated by whitespace) into string
    """
    return "".join([MORSECODE_INVERSE[m] for m in s.split()])

def parse_patterns(pattern: str) -> list[str]:
    """
    parse pattern in a list of strings out such that each out[i] is suitable for make_morse_matches.
    """
    by_whitespace = pattern.lower().split()
    reg = re.compile("[a-z*1234]|[-.?]+")
    out = []
    for w in by_whitespace:
        out += reg.findall(w)
    return out