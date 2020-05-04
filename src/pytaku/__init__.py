import os

from pytaku.conf import config


def manage():
    """Django's command-line utility for administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pytaku.settings")
    config.django_manage()  # use goodconf to run a monkey-patched "manage.py"


def generate_config():
    print(config.generate_json(DEBUG=True))


def generate_psql_envars():
    """
    Outputs shell statements to set Postgres connection envars.
    Usage:
        pytaku-generate-psql-envars | source
        psql  # or even better, pgcli
        # should drop you into the pytaku db shell
    """
    print(
        f"""\
export PGHOST='{config.DB_HOST}'
export PGPORT='{config.DB_PORT}'
export PGDATABASE='{config.DB_NAME}'
export PGUSER='{config.DB_USER}'
export PGPASSWORD='{config.DB_PASSWORD}'
"""
    )
