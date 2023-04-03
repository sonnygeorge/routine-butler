import argparse

from routine_butler.main import main


if __name__ in {"__main__", "__mp_main__"}:
    # Define the "--testing" cli argument
    parser = argparse.ArgumentParser(description="Script description")
    help = "If used, the app will be run with a test database w/ a single fake test user"
    parser.add_argument("--testing", action="store_true", help=help)

    # Parse the arguments
    args = parser.parse_args()

    print(args.testing)

    # pass the --testing argument through to main()
    main(testing=args.testing)
