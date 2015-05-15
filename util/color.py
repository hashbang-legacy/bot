

_WEECHAT_COLORS = [
  ("00", "white"),
  ("01", "black"),
  ("02", "blue"),
  ("03", "green"),
  ("04", "lightred"),
  ("05", "red"),
  ("06", "magenta"),
  ("07", "brown"),
  ("08", "yellow"),
  ("09", "lightgreen"),
  ("10", "cyan"),
  ("11", "lightcyan"),
  ("12", "lightblue"),
  ("13", "lightmagenta"),
  ("14", "darkgray"),
  ("15", "gray")]

_03 = chr(3)
_COLOR_MAP = {}

_VALS = [str(n) for n in range(16)]
#Build mappings
for fg in _VALS:
    for bg in _VALS:
        _COLOR_MAP["C{},{}".format(fg, bg)] =\
            _03 + fg +"," + bg.zfill(2)
for v in _VALS:
    code = _03 + v.zfill(2)
    _COLOR_MAP["C{}".format(v)] = code
    _COLOR_MAP["C{},".format(v)] = code

    code = _03 + "," + v.zfill(2)
    _COLOR_MAP["C,{}".format(v)] = code

for val, name in _WEECHAT_COLORS:
  code = _03 + val
  _COLOR_MAP[name.upper()] = code
  _COLOR_MAP[name.lower()] = code

_COLOR_MAP["C"] = chr(15)  #{C} = reset colors
_COLOR_MAP[""] = chr(15)   #{} = reset colors
_COLOR_MAP["B"] = chr(0x02)#{B} bold
_COLOR_MAP["U"] = chr(0x1F)#{U} underline
_COLOR_MAP["R"] = chr(0x12)#{R} reverse
_COLOR_MAP["LINK"] = "\x1F\x0310\02\02"


def parse_colors(line):
    for code, replacement in _COLOR_MAP.items():
        line = line.replace("{{{}}}".format(code), replacement)
    return line
