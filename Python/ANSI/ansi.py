class State:
    def __init__(self, enter="", exit=""):
        self.enter = enter
        self.exit = exit

    def __enter__(self):
        print(self.enter, end="")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.exit, end="")


# Control Sequence Introducer
CUU = "\033[{}A".format  # Cursor Up
CUD = "\033[{}B".format  # Cursor Down
CUF = "\033[{}C".format  # Cursor Forward
CUB = "\033[{}D".format  # Cursor Backward
CNL = "\033[{}E".format  # Cursor Next Line
CPL = "\033[{}F".format  # Cursor Previous Line
CHA = "\033[{}G".format  # Cursor Horizontal Absolute
VPA = "\033[{}d".format  # Vertical Position Absolute
CUP = "\033[{};{}H".format  # Cursor Position
HVP = "\033[{};{}f".format  # Horizontal and Vertical Position
SCP = "\033[s".format  # Save Cursor Position
RCP = "\033[u".format  # Restore Cursor Position
SC = "\033[?25h".format  # Show Cursor
HC = "\033[?25l".format  # Hide Cursor
EB = "\033[?12h".format  # Enable Blinking
DB = "\033[?12l".format  # Disable Blinkin
SU = "\033[{}S".format  # Scroll Up (not ANSI.SYS)
SD = "\033[{}T".format  # Scroll Down (not ANSI.SYS)
ICH = "\033[{}@".format  # Insert Character
DCH = "\033[{}P".format  # Delete Character
ECH = "\033[{}X".format  # Erase Character
IL = "\033[{}L".format  # Insert Line
DL = "\033[{}M".format  # Delete Line
EL = "\033[{}K".format  # Erase in Line (0 = from cursor to end, 1 = from cursor to beginning, 2 = entire line)
ED = "\033[{}J".format  # Erase in Page (0 = from cursor to end, 1 = from cursor to beginning, 2 = entire screen)
STBM = "\033[{};{}r".format  # Set Top and Bottom Margins
EASB = "\033[?1049h".format  # Enable Alternate Screen Buffer
DASB = "\033[?1049l".format  # Disable Alternate Screen Buffer


# Operating System Command
STITLE = "\033]0;{}\033\\".format  # Set Title
SCN = "\033]4;{};{}\033\\".format  # Set Color Number
SDFGC = "\033]10;{}\033\\".format  # Set Default Foreground Color
SDBGC = "\033]11;{}\033\\".format  # Set Default Background Color
SDTCC = "\033]12;{}\033\\".format  # Set Default Text Cursor Color


# C1 Control Codes
RIS = "\033c".format  # Reset to Initial State
IND = "\033D".format  # Index
RND = "\033M".format  # Reverse Index
DECSC = "\0337".format  # Save Cursor
DECRC = "\0338".format  # Restore Cursor
DECLD = "\033(0".format  # DEC Line Drawing Character Set
DECUS = "\033(B".format  # US ASCII Character Set
DECPAM = "\033=".format  # Application Keypad
DECPNM = "\033>".format  # Normal Keypad
DECSTR = "\033[!p".format  # Soft Terminal Reset


Styles = {
    "bold": 1,
    "dim": 2,
    "normal": 22,
    "italic": 3,
    "regular": 23,
    "ulineon": 4,
    "ulineoff": 24,
    "slow": 5,
    "fast": 6,
    "static": 25,
    "negative": 7,
    "positive": 27,
    "hide": 9,
    "show": 29,
    "slineon": 9,
    "slineoff": 29,
    "olineon": 53,
    "olineoff": 55,
}


Colors = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
    "default": 9,
}


class RGB:
    def __init__(self, r, g, b):
        assert (r | g | b) >> 8 == 0
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b)

    def __invert__(self):
        return RGB(255 - self.r, 255 - self.g, 255 - self.b)


def SGR(*style, fgc=None, bgc=None):  # Select Graphic Rendition
    n = [Styles[s.lower()] for s in style]
    for i, c in (30, fgc), (40, bgc):
        if c is None:
            continue
        elif isinstance(c, str):
            n.extend([i + Colors[c.lower()] + c.isupper() * 60])
        elif isinstance(c, int):
            n.extend([i + 8, 5, c])
        elif isinstance(c, RGB):
            n.extend([i + 8, 2, c.r, c.g, c.b])
    return "\033[" + ";".join(map(str, n)) + "m"
