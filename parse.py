from typing import List, Optional

from config import Config
from enums import Brackets, Grouping


_brackets = {
    ("h", Brackets.HERALD.name.lower())     :   Brackets.HERALD,
    ("g", Brackets.GUARDIAN.name.lower())   :   Brackets.GUARDIAN,
    ("c", Brackets.CRUSADER.name.lower())   :   Brackets.CRUSADER,
    ("a", Brackets.ARCHON.name.lower())     :   Brackets.ARCHON,
    ("l", Brackets.LEGEND.name.lower())     :   Brackets.LEGEND,
    ("n", Brackets.ANCIENT.name.lower())    :   Brackets.ANCIENT,
    ("d", Brackets.DIVINE.name.lower())     :   Brackets.DIVINE,
    ("p", Brackets.PRO.name.lower())        :   Brackets.PRO,
    ("A", Brackets.ALL.name.lower())        :   Brackets.ALL
}

_grouping = {
    ("m", Grouping.MAINSTAT.name.lower(), "stat")   :   Grouping.MAINSTAT,
    ("a", Grouping.ATTACK.name.lower())             :   Grouping.ATTACK,
    ("r", Grouping.ROLE.name.lower())               :   Grouping.ROLE,
    ("A", "N", Grouping.NONE.name.lower(), "none")  :   Grouping.NONE
}


def parse_arg_bracket(bracket: Optional[str]) -> List[int]:
    """Parses bracket (`-b` `--bracket`) argument.
    
    Returns list of integers.
    """
    default = Config.DEFAULT_BRACKET
    r = []
    
    if not bracket:
        r.append(default.value)
    elif any(c == str(Brackets.ALL) for c in bracket):
        r = [b.value for b in Brackets if b.value != b.ALL.value] # 0 -> [1, 2, 3, .., 8]
    else:
        for c in bracket:                       # check each character in string
            for k, v in _brackets.items():      # to allow for multiple args, e.g. "-b ndp" 
                if c in k or c == str(v.value): # which results in [6,7,8] (Ancient, Divine, Pro)
                    r.append(v.value)
                    break
        
    if not r:
        print(f"ERROR: Unable to identify argument. Using default: {default.name}.")
        r.append(default.value)

    return r    

# Similar, but not identical, in structure to parse_brackets()
def parse_arg_grouping(grouping: Optional[str]) -> int:
    """Parses grouping (`-g` `--group`) argument.
    
    Returns integer
    """
    default = Config.DEFAULT_GROUPING
    r = []
    
    if not grouping:
        r = default.value
    else:
        for k, v in _grouping.items():
            if grouping in k or grouping == str(v.value):
                r = v.value
                break
                
    if not r:
        print(f"ERROR: Unable to identify grouping argument. Using default: {default.name}.")
        r = default.value

    return r 
