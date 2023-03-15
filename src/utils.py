import remi

ZERO = """
░█████╗░
██╔══██╗
██║░░██║
██║░░██║
╚█████╔╝
░╚════╝░
"""

ONE = """
░░███╗░░
░████║░░
██╔██║░░
╚═╝██║░░
███████╗
╚══════╝
"""

TWO = """
██████╗░
╚════██╗
░░███╔═╝
██╔══╝░░
███████╗
╚══════╝
"""

THREE = """
██████╗░
╚════██╗
░█████╔╝
░╚═══██╗
██████╔╝
╚═════╝░
"""

FOUR = """
░░██╗██╗
░██╔╝██║
██╔╝░██║
███████║
╚════██║
░░░░░╚═╝
"""

FIVE = """
███████╗
██╔════╝
██████╗░
╚════██╗
██████╔╝
╚═════╝░
"""

SIX = """
░█████╗░
██╔═══╝░
██████╗░
██╔══██╗
╚█████╔╝
░╚════╝░
"""

SEVEN = """
███████╗
╚════██║
░░░░██╔╝
░░░██╔╝░
░░██╔╝░░
░░╚═╝░░░
"""

EIGHT = """
░█████╗░
██╔══██╗
╚█████╔╝
██╔══██╗
╚█████╔╝
░╚════╝░
"""

NINE = """
░█████╗░
██╔══██╗
╚██████║
░╚═══██║
░█████╔╝
░╚════╝░
"""

COLON = """
██╗
╚═╝
░░░
░░░
██╗
╚═╝
"""

CLOCK_CHARS = {
    "0": ZERO,
    "1": ONE,
    "2": TWO,
    "3": THREE,
    "4": FOUR,
    "5": FIVE,
    "6": SIX,
    "7": SEVEN,
    "8": EIGHT,
    "9": NINE,
    ":": COLON,
}


def encircle(s: str) -> str:
    """Encircles block of text with a border"""
    lines = s.split("\n")
    max_length = max(len(line) for line in lines)

    top_border = f"╔{'═' * (max_length + 2)}╗\n"
    bottom_border = f"╚{'═' * (max_length + 2)}╝"

    result = [top_border]
    for line in lines:
        if line.strip():
            result.append(f"║ {line:<{max_length}} ║\n")
    result.append(bottom_border)

    return "".join(result)


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
    fancy_chars = [CLOCK_CHARS[char] for char in clock_string]
    together = fancy_chars[0]
    for fancy_char in fancy_chars[1:]:
        together = side_by_side(together, fancy_char)
    return encircle(together)


DEFAULT_STYLES = {
    "background": "lightgray",
}


def add_default_styles(container: remi.gui.Container) -> None:
    container.set_style(DEFAULT_STYLES)
    container.css_font_family = "Monospace"