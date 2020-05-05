# Pytaku

Goals:

- Simplest backend setup that works, but no simpler.
  A webmaster's installation runlist should be as simple as:
  + pip install pytaku
  + pytaku-generate-config > pytaku.conf.json
  + [edits pytaku.conf.json: db credentials etc.]
  + pytaku-run


# Dev

On Arch Linux:

```sh
sudo pacman -S postgresql-libs python-poetry

# spin up postgres container, because manually creating databases for dev
# purposes is fiddly and annoying.
docker-compose up -d

# assuming pyenv and pyenv-virtualenv are already installed:
pyenv virtualenv 3.7.7 pytaku
pyenv activate pytaku
poetry install

# need to activate again so pyenv can make shims for installed entrypoints:
# (see [tool.poetry.scripts] in pyproject.toml)
pyenv deactivate && pyenv activate

# generate initial config for local dev - should work out of the box with the
# db provided by docker-compose above.
make localconfig

make dev
```

# Env-specific configs

This project uses [goodconf](https://github.com/lincolnloop/goodconf).
See what options are available at **src/pytaku/conf.py**.

# Installation for actual use

```sh
pip install pytaku
```

To be expanded.
