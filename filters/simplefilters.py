import re
import utils.morse as morse

from .defs import Filter, SimpleFilter, FilterMakerMaker, FilterMaker, from_error_count, BinaryFilter
def make_length_filter_exact(i: int) -> Filter:
    assert i >= 0
    return SimpleFilter(lambda s: len(s) == i, "Length is exactly %s." % i, priority=-10)

def make_length_filter_minimum(i: int) -> Filter:
    assert i >= 0
    return SimpleFilter(lambda s: len(s) >= i, "Length is at least %s." % i, priority=-10)

def make_length_filter_maximum(i: int) -> Filter:
    assert i >= 0
    return SimpleFilter(lambda s: len(s) <= i, "Length is at most %s." % i, priority=-10)

def _assert_fun(cond: bool):
    assert cond
class _LengthFilterMakerExact(FilterMakerMaker):
    description = "Match length exactly"
    prompts = {"Please enter length:": int}
    conditions = [lambda x: _assert_fun(x > 0)]
    num_args = 1

    @classmethod
    def initializeFilter(cls, i) -> Filter:
        return SimpleFilter(lambda s: len(s) == i, f"Length is exactly {i}.", priority=-10)

class _LengthFilterMakerMin(FilterMakerMaker):
    description = "Ensure minimal length"
    prompts = {"Please enter length:": int}
    conditions = [lambda x: _assert_fun(x > 0)]
    num_args = 1

    @classmethod
    def initializeFilter(cls, *args) -> Filter:
        i = args[0]
        return SimpleFilter(lambda s: len(s) >= i, f"Length is at least {i}.", priority=-10)

class _LengthFilterMakerMax(FilterMakerMaker):
    description = "Ensure maximal length"
    prompts = {"Please enter length:": int}
    conditions = [lambda x: _assert_fun(x > 0)]
    num_args = 1

    @classmethod
    def initializeFilter(cls, *args) -> Filter:
        i = args[0]
        return SimpleFilter(lambda s: len(s) <= i, f"Length is at most {i}.", priority=-10)


LengthFilterExact: FilterMaker = _LengthFilterMakerExact.make_FilterMaker()
LengthFilterMin: FilterMaker = _LengthFilterMakerMin.make_FilterMaker()
LengthFilterMax: FilterMaker = _LengthFilterMakerMax.make_FilterMaker()


ALPHABET = "abcdefghijklmnopqrstuvwxyz".lower()
assert (len(ALPHABET) == 26)
def maketable(s: str) -> dict[str, int]:
    """
    Creates a dict letter -> number of occurences from a given string
    """
    s = s.lower()
    ret = {}
    for c in ALPHABET:
        ret[c] = s.count(c)
    return ret

class ContainsFilter(Filter):

    substring: str
    table: dict[str, int]
    def __init__(self, substring: str):
        s = f"Must contain the following characters: {substring}"
        super().__init__(allow_errors=True, priority=10, display=s)
        self.substring = substring
        self.table = maketable(substring)

    def apply(self, input_list: list[str]) -> list[str]:
        return self.apply_with_errors(input_list)[0]

    def apply_with_errors(self, input_list: list[str], *, max_errors: int = 0) -> list[list[str]]:
        def count_errors(input_string) -> int:
            occurences = maketable(input_string)
            actual_errors = 0
            for c in ALPHABET:
                if self.table[c] > occurences[c]: #
                    actual_errors += self.table[c] - occurences[c]
                    if actual_errors > max_errors:
                        return -1
            return actual_errors
        return from_error_count(input_list, max_errors=max_errors, fun=count_errors)

class _ContainsFilterMakerMaker(FilterMakerMaker):
    description = "Ensure that a substring is contained (in any order, with multiplicity)"
    prompts = {"Enter substring: ": str}
    num_args = 1

    @classmethod
    def initializeFilter(cls, substring: str) -> Filter:
        return ContainsFilter(substring)

ContainsFilterMaker = _ContainsFilterMakerMaker.make_FilterMaker()


class _PositionFilterMakerMaker(FilterMakerMaker):
    description = "A given position is in a set of characters"
    prompts = {"Enter position (1-indexed): ": int, "Enter possible characters: ": str}
    num_args = 2
    conditions = [lambda x: _assert_fun(x>0), None]

    @classmethod
    def initializeFilter(cls, pos: int, options: str) -> Filter:
        options = options.lower()
        def cond(s: str) -> bool:
            return len(s) >= pos and s[pos-1] in options
        return BinaryFilter(cond, f"The {pos}'th character is among {options}.", priority=-5)

PositionFilterMaker = _PositionFilterMakerMaker.make_FilterMaker()


class _PatternFilterMakerMaker(FilterMakerMaker):
    description = "Some characters are equal"
    prompts = {"Enter first position (1-indexed): ": int, "Enter second position (1-indexed): ": int}
    num_args = 2
    conditions = [lambda x: _assert_fun(x>0), lambda x:_assert_fun(x>0)]

    @classmethod
    def initializeFilter(cls, pos1: int, pos2: int) -> Filter:
        if pos1 == pos2:
            raise ValueError("Positions are equal. This is bogus.")
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
        assert pos2 > pos1
        def cond(s: str) -> bool:
            return len(s) >= pos2 and s[pos2-1] == s[pos1-1]
        return BinaryFilter(cond, f"The {pos1}th and {pos2}th characters agree.", priority=-5)

PatternFilterMaker = _PatternFilterMakerMaker.make_FilterMaker()

class _RegexpFilterMakerMaker(FilterMakerMaker):
    description = "Match regular expression"
    prompts = {"Enter regular expression required to match: ": str}
    num_args = 1

    @classmethod
    def initializeFilter(cls, regexp) -> Filter:
        compile_regexp = re.compile(regexp)
        def cond(s: str) -> bool:
            return compile_regexp.fullmatch(s) is not None
        return SimpleFilter(cond, f"Matches regexp {regexp}")

RegexpFilterMaker = _RegexpFilterMakerMaker.make_FilterMaker()


class MorseFilter(Filter):
    pattern: str
    must_match: list[str]

    def __init__(self, pattern):
        s = f"Must match the following Morse pattern: {pattern}"
        self.pattern = pattern
        parsed_pattern: list[str] = morse.parse_patterns(pattern)
        self.must_match: list[str] = [morse.make_morse_matches(p) for p in parsed_pattern]
        super().__init__(allow_errors=True, priority=-2, display=s)

    def apply_with_errors(self, input_list: list[str], *, max_errors: int = 0) -> list[list[str]]:
        def count_errors(input_string) -> int:
            if len(input_string) < len(self.must_match):
                return -1
            num_errors = 0
            for i in range(len(self.must_match)):
                if input_string[i] not in self.must_match[i]:
                    num_errors+=1
            return num_errors
        return from_error_count(input_list, max_errors=max_errors, fun=count_errors)

    def apply(self, input_list: list[str]) -> list[str]:
        return self.apply_with_errors(input_list)[0]

class _MorseFilterMakerMaker(FilterMakerMaker):
    description = "Filter by (partial knowledge of) morse code"
    prompts = {"Valid conditions are\n - 1,2,3,4: Characters' morse code has that length.\n - a-z: must match that character.\n - '*': match any character\n - a sequence of '.','-' and '?'s: Match character with corresponding morse code.\nEnter list of conditions. Separate morse-code by whitespace: ": str}
    num_args = 1

    @classmethod
    def initializeFilter(cls, pattern) -> Filter:
        return MorseFilter(pattern)

MorseFilterMaker = _MorseFilterMakerMaker.make_FilterMaker()