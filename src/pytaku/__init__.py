from pytaku.conf import config


def serve():
    """
    This command passes all CLI args to gunicorn, so for example:
        pytaku -w 7 -b 0.0.0.0:5001
    would mean:
        gunicorn pytaku.main:app -w 7 -b 0.0.0.0:5001

    It assumes your virtualenv's bin path is already in $PATH of course.
    """
    import subprocess
    from sys import argv

    command = ["gunicorn", "pytaku.main:app"] + argv[1:]
    print("Running:", " ".join(command))

    subprocess.run(command)


def dev():
    import os
    import subprocess
    from sys import argv

    command = ["flask", "run"] + argv[1:]
    print("Running:", " ".join(command))

    subprocess.run(
        command,
        env={"FLASK_ENV": "development", "FLASK_APP": "pytaku.main:app", **os.environ},
    )


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

    config.load()
    migrate(overwrite_latest_schema=args.dev)


def generate_config():
    print(config.generate_json(DEBUG=True))


def scheduler():
    config.load()
    from .scheduler import main_loop

    main_loop()


def collect_static():
    from sys import argv

    if len(argv) != 2:
        print("Usage: pytaku-collect-static path/to/static/dir")
        print("A 'static' dir will be created inside the provided path.")
        exit(1)

    import importlib.resources
    from pathlib import Path
    from shutil import copytree

    destination = Path(argv[1]) / "static"

    with importlib.resources.path("pytaku", "__init__.py") as pytaku_path:
        copytree(pytaku_path.parent / "static", destination)
    print(f"Static files copied to {destination}")
