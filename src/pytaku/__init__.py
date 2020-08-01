from pytaku.conf import config


def migrate():
    import argparse
    from .database.migrator import migrate

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-d",
        "--dev",
        action="store_true",
        help="dev mode: overwrites latest_schema.sql on success",
    )
    args = argparser.parse_args()

    migrate(overwrite_latest_schema=args.dev)


def generate_config():
    print(config.generate_json(DEBUG=True))
