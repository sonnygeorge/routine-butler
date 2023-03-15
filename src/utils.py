ZERO = """
 █████  
██   ██ 
██   ██ 
██   ██ 
 █████  
"""

ONE = """
  ███   
 ████   
██ ██   
   ██   
███████ 
"""

TWO = """
██████  
     ██ 
  ███   
██      
███████ 
"""

THREE = """
██████  
     ██ 
 █████  
     ██ 
██████  
"""

FOUR = """
  ██ ██ 
 ██  ██ 
██   ██ 
███████ 
     ██ 
"""

FIVE = """
███████ 
██      
██████  
     ██ 
██████  
"""

SIX = """
 █████  
██      
██████  
██   ██ 
 █████  
"""

SEVEN = """
███████ 
     ██ 
    ██  
   ██   
  ██    
"""

EIGHT = """
 █████  
██   ██ 
 █████  
██   ██ 
 █████  
"""

NINE = """
 █████  
██   ██ 
 ██████ 
     ██ 
 █████  
"""

COLON = """
██ 
   
   
   
██ 
"""

_FANCY_CLOCK_ENCODER_VALS = [
    ZERO,
    ONE,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    COLON,
]
_FANCY_CLOCK_ENCODER_VALS = [c.replace(" ", " ") for c in _FANCY_CLOCK_ENCODER_VALS]
_FANCY_CLOCK_ENCODER_KEYS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":"]
_FANCY_CLOCK_ENCODER = dict(zip(_FANCY_CLOCK_ENCODER_KEYS, _FANCY_CLOCK_ENCODER_VALS))


def side_by_side(string_one: str, string_two: str):
    """Side by side two blocks of text with the same number of lines"""
    assert string_two.count("\n") == string_one.count(
        "\n"
    ), "side_by_side() requires two strings with the same number of lines"
    striing_one_lines = string_one.split("\n")
    string_two_lines = string_two.split("\n")
    result = []
    for string_one_line, string_two_line in zip(striing_one_lines, string_two_lines):
        result.append(f"{string_one_line}{string_two_line}")
    return "\n".join(result)


def get_fancy_clock_string(clock_string) -> str:
    whitelist = "0123456789:"
    assert all(
        char in whitelist for char in clock_string
    ), f"get_fancy_clock_string() argument must only contain {whitelist}"
    fancy_chars = [_FANCY_CLOCK_ENCODER[char] for char in clock_string]
    together = fancy_chars[0]
    for fancy_char in fancy_chars[1:]:
        together = side_by_side(together, fancy_char)
    return together
