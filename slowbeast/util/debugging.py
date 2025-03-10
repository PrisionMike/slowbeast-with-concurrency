from os import getcwd
from sys import stderr, stdout
from typing import Any, Callable, Dict, Optional, TextIO

COLORS = {
    "dark_blue": "\033[0;34m",
    "dark_green": "\033[0;32m",
    "cyan": "\033[0;36m",
    "blue": "\033[1;34m",
    "purple": "\033[0;35m",
    "red": "\033[1;31m",
    "wine": "\033[0;31m",
    "green": "\033[1;32m",
    "brown": "\033[0;33m",
    "yellow": "\033[1;33m",
    "white": "\033[1;37m",
    "gray": "\033[0;37m",
    "dark_gray": "\033[1;30m",
    "dark_gray_thin": "\033[38;5;238m",
    "orange": "\033[38;5;214m",
    "orangebg": "\033[1;43m",
    "greenbg": "\033[1;42m",
    "redbg": "\033[1;41m",
    "orangeul": "\033[1;4;33m",
    "greenul": "\033[1;4;32m",
    "redul": "\033[1;4;31m",
    "reset": "\033[0m",
}

_global_prefix = None


def inc_print_indent():
    global _global_prefix
    _global_prefix = "  " + (_global_prefix or "")


def dec_print_indent():
    global _global_prefix
    _global_prefix = _global_prefix[2:]
    if not _global_prefix:
        _global_prefix = None


def print_stream(
    msg: str,
    stream: TextIO,
    prefix: Optional[str] = None,
    print_ws: Optional[str] = "\n",
    color: Optional[str] = None,
) -> None:
    """
    Print message to stderr/stdout

    @ msg      : str    message to print
    @ prefix   : str    prefix for the message
    @ print_nl : bool  print new line after the message
    @ color    : str    color to use when printing, default None
    """

    # don't print color when the output is redirected
    # to a file
    if not stream.isatty():
        color = None

    if color is not None:
        stream.write(COLORS[color.lower()])

    if msg == "":
        return
    if prefix is not None:
        stream.write(prefix)
    if _global_prefix is not None:
        stream.write(_global_prefix)

    stream.write(msg)

    if color is not None:
        stream.write(COLORS["reset"])

    if print_ws:
        stream.write(print_ws)

    stream.flush()


def print_stderr(
    msg: str,
    prefix: Optional[str] = None,
    print_ws: str = "\n",
    color: Optional[str] = None,
) -> None:
    print_stream(msg, stderr, prefix, print_ws, color)


def print_stdout(
    msg: str, prefix: None = None, print_ws: str = "\n", color: Optional[str] = None
) -> None:
    print_stream(msg, stdout, prefix, print_ws, color)


def print_highlight(
    s: str,
    words: Dict[str, str],
    prefix: Optional[str] = None,
    stream: TextIO = stdout,
) -> None:
    """Words: dictionary words -> colors"""
    if prefix:
        print_stream(prefix, print_ws=None, stream=stream)
    for w in s.split():
        c = words.get(w)
        if c:
            print_stream(w, color=c, print_ws=" ", stream=stream)
        else:
            print_stream(w, print_ws=" ", stream=stream)
    stream.write("\n")


_is_debugging = 0
_debugging_prefix = ""


def set_debugging(verbose_lvl: int = 1) -> None:
    global _is_debugging
    _is_debugging = verbose_lvl


def unset_debugging():
    global _is_debugging
    _is_debugging = 0


def set_debugging_prefix(prefix=""):
    global _debugging_prefix
    _debugging_prefix = prefix


def get_debugging_prefix():
    global _debugging_prefix
    return _debugging_prefix


def inc_debugging_lvl():
    global _debugging_prefix
    _debugging_prefix = "  " + _debugging_prefix


def dec_debugging_lvl():
    global _debugging_prefix
    if _debugging_prefix.startswith("  "):
        _debugging_prefix = _debugging_prefix[2:]


def dbg(
    msg: str, print_ws: str = "\n", color: str = "GRAY", fn: Callable = print_stderr
) -> None:
    if _is_debugging < 1:
        return

    fn(msg, f"[sb] {_debugging_prefix}", print_ws, color)


def dbgv(
    msg: str,
    verbose_lvl: int = 2,
    print_ws: str = "\n",
    color: str = "GRAY",
    fn: Callable = print_stderr,
) -> None:
    if _is_debugging < verbose_lvl:
        return

    fn(msg, f"[sb] {_debugging_prefix}", print_ws, color)


def ldbgv(
    fmt: str,
    args: Any,
    verbose_lvl: int = 2,
    print_ws: str = "\n",
    color: str = "GRAY",
    fn: Callable = print_stderr,
) -> None:
    """
    Lazy dbgv -- does not build the debugging message unless debugging is set
    to True. Especially strings that contain solver expressions take a long
    time to build.
    """
    if __debug__:
        if _is_debugging < verbose_lvl:
            return

        fn(fmt.format(*args), f"[sb] {_debugging_prefix}", print_ws, color)


def ldbg(fmt, args, verbose_lvl=2, print_ws="\n", color="GRAY", fn=print_stderr):
    """
    Lazy dbgv -- does not build the debugging message unless debugging is set
    to True. Especially strings that contain solver expressions take a long
    time to build.
    """
    if __debug__:
        if _is_debugging < verbose_lvl:
            return
        fn(fmt.format(*args), f"[sb] {_debugging_prefix}", print_ws, color)


def dbg_sec(msg=None, color="WHITE"):
    if msg is None:
        dec_debugging_lvl()
    else:
        dbg(msg, color=color)
        inc_debugging_lvl()


def dbgv_sec(msg=None, verbose_lvl=2, color="WHITE"):
    """Exactly as dbg sec, but uses dbgv"""
    if msg is None:
        dec_debugging_lvl()
    else:
        dbgv(msg, color=color, verbose_lvl=verbose_lvl)
        inc_debugging_lvl()


def warn(msg, print_ws="\n", color="BROWN"):
    print_stderr(msg, "[sb] WARNING: ", print_ws, color)


_warned_once = set()


def warn_once(key, msg, print_ws="\n", color="BROWN"):
    global _warned_once
    if key in _warned_once:
        return
    _warned_once.add(key)
    print_stderr(msg, "[sb] WARNING once: ", print_ws, color)


def FIXME(msg: str, print_ws: str = "\n", color: str = "DARK_GRAY_THIN") -> None:
    print_stderr(msg, "[sb] !FIXME! ", print_ws, color)


def new_output_file(name: str, outputdir=None) -> TextIO:
    outdir = outputdir or getcwd()
    return open(f"{outdir}/{name}", "w", encoding="utf-8")
