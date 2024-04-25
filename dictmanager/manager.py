from typing import Optional, Callable, Union
from pathlib import PurePath

def _identity(x: str) -> Union[str, list[str]]:
    return x


_STATUS_ACTIVE = 1
_STATUS_INACTIVE = 2
_STATUS_FAILURE = 3

class DictSpecification:
    """
    DictSpecification collects all information needed to specify a (base) dictionary that filters are later run on.
    Note that this does not actually load the dict.
    The latter is relevant because we may want to (de-)serialize the specification even if the file is missing or is
    changing.

    path denotes the file path that we use to load the dict
    normalizer is a function str -> str | list[str] that is used to preprocess each entry (e.g. umlaut-normalization)
    encoding is forwarded to open
    display is the name displayed to the user (default: filename without path)
    """

    path: str  # file path
    display: str  # displayed name
    encoding: Optional[str]  # encoding
    normalizer: Callable[[str], Union[str, list[str]]]
    status: int
    def __init__(self, path: str, *, normalizer=_identity, display: Optional[str] = None, encoding: Optional[str] = None, status: int = _STATUS_ACTIVE):
        self.path = path
        self.normalizer = normalizer
        if display is None:
            self.display = PurePath(path).name
        else:
            self.display = display
        self.encoding = encoding
        self.status = status

    def make_active(self):
        """
        NOTE: Need to update the corresponding Unfiltered Dict
        """
        self.status = _STATUS_ACTIVE

    def make_inactive(self):
        """
        NOTE: Need to update the corresponding Unfiltered Dict
        """

        self.status = _STATUS_INACTIVE

class UnfilteredDict:
    """
    UnfilteredDict is the actual dictionary loaded using the specification
    """
    spec: DictSpecification
    L: list[str]
    size: int
    status: int
    error: Optional[Exception]

    def __init__(self, spec: DictSpecification):
        self.spec = spec
        self.L = []
        self.status = spec.status
        self.reload()

    def reload(self):
        """
        (re-)loads the Unfiltered dict from disk.
        """
        self.L = []
        self.error = None
        if self.status == _STATUS_INACTIVE:
            return

        normalizer = self.spec.normalizer

        try:
            with open(self.spec.path, "r", encoding=self.spec.encoding) as f:
                lines = f.readlines()
                for entry in lines:
                    normalized_entries = normalizer(entry)
                    if normalized_entries:
                        self.L += normalized_entries
        except Exception as E:
            self.status = _STATUS_FAILURE
            self.error = E
            self.L = []
        self.L = list(set(self.L)) # remove duplicates
        self.L.sort()


    @property
    def size(self):
        return len(self.L)

    def make_active(self):
        self.status = _STATUS_ACTIVE
        self.reload()

    def make_inactive(self):
        self.status = _STATUS_INACTIVE
        self.reload()

    def __str__(self) -> str:
        s = self.spec.display
        if self.status == _STATUS_FAILURE:
            s += " ERROR: "
            s += str(self.error)
        elif self.status == _STATUS_INACTIVE:
            s += " (inactive)"
        return s

    @property
    def is_active(self) -> bool:
        return self.status == _STATUS_ACTIVE
