from dictmanager import DictSpecification, UnfilteredDict, normalizeToAscii
from state import State
from frontends import SimpleFrontEnd

NGERMAN = DictSpecification("/usr/share/dict/ngerman", normalizer=normalizeToAscii)

DICT_SPECS = [NGERMAN]

STATE = State(DICT_SPECS)
STATE.validate()

FRONTEND = SimpleFrontEnd()

from frontends.simplefrontend import filter_from_FilterMaker
from filters import LengthFilterExact

if __name__ == "__main__":
    FRONTEND.run(STATE)