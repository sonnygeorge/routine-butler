import argparse
from typing import Protocol

from routine_butler.main import main


class RunArgs(Protocol):
    single_user: bool
    testing: bool
    native: bool
    fullscreen: bool
    open_browser: bool
    reload: bool


CLI_DESCRIPTION = "CLI for running RoutineButler"

ARGS = [
    {
        "arg": "--single-user",
        "help": "Runs the app w/ no login screen and a single user",
    },
    {
        "arg": "--testing",
        "help": "Runs the app in testing mode",
    },
    {
        "arg": "--native",
        "help": "Runs in a native window",
    },
    {
        "arg": "--fullscreen",
        "help": "Runs in fullscreen mode, only works w/ --native",
    },
    {
        "arg": "--open-browser",
        "help": "Auto-opens browser on startup, not applicable w/ --native",
    },
    {
        "arg": "--reload",
        "help": "Reloads the app on file changes (useful for development)",
    },
]


if __name__ in {"__main__", "__mp_main__"}:
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    for arg in ARGS:
        parser.add_argument(arg["arg"], action="store_true", help=arg["help"])
    args: RunArgs = parser.parse_args()
    
    main(
        testing=args.testing,
        single_user=args.single_user,
        native=args.native,
        fullscreen=args.fullscreen,
        open_browser=args.open_browser,
        reload=args.reload,
    )
