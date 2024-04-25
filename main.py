from dictmanager import DictSpecification, UnfilteredDict, normalizeToAscii, normalizeStreets
from state import State
from frontends import SimpleFrontEnd

NGERMAN = DictSpecification("/usr/share/dict/ngerman", normalizer=normalizeToAscii)
DORTMUND = DictSpecification( "./dicts/Dortmund.txt", normalizer=normalizeStreets)

DICT_SPECS = [NGERMAN, DORTMUND]

STATE = State(DICT_SPECS)
STATE.validate()

FRONTEND = SimpleFrontEnd()

if __name__ == "__main__":
    FRONTEND.run(STATE)