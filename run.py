import argparse

from routine_butler.main import main

if __name__ in {"__main__", "__mp_main__"}:
    parser = argparse.ArgumentParser(description="Runs RoutineButler")
    help = "If used, the app will run with a test database and auto-login w/ a test user"
    parser.add_argument("--testing", action="store_true", help=help)
    args = parser.parse_args()
    main(testing=args.testing)
