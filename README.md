Live demo: https://dev.pytaku.com (db may be hosed any time, also expect bugs)

Production instance coming When It's Ready (tm).

# Pytaku

Pytaku is a WIP web-based manga reader that keeps track of your reading
progress and new chapter updates. Its design goals are:

- Self-host friendly - if you have a UNIX-like server with python3.7+ and can
  run `pip install`, you're good.

- Phone/tablet friendly - although I hardly read any webtoons these days so the
  phone experience may not be as polished.

- KISSFFS, or **K**eep **I**t rea**S**onably **S**imple you **F**-ing
  architecture/tooling **F**etishi**S**ts! Oftentimes I have enough practice on
  industrial grade power tools at work so at home I want a change of pace.
  Flask + raw SQL has been surprisingly comfy. On the other side, mithril.js
  provides a good baseline of SPA functionality without having to pull in the
  Rube Goldberg machine that is """modern""" JS devtools.

# Development

```sh
## Backend ##

poetry install
pip install --upgrade pip
pip install https://github.com/rogerbinns/apsw/releases/download/3.32.2-r1/apsw-3.32.2-r1.zip \
      --global-option=fetch --global-option=--version --global-option=3.32.2 --global-option=--all \
      --global-option=build --global-option=--enable-all-extensions

pytaku-generate-config > pytaku.conf.json
# fill stuff as needed

# run migration script once
pytaku-migrate

# run 2 processes:
pytaku-dev -p 8000  # development webserver
pytaku-scheduler  # scheduled tasks e.g. update titles


## Frontend ##

doas pacman -S entr  # to watch source files
npm install -g --prefix ~/.node_modules esbuild # to bundle js

# Listen for changes in js-src dir, automatically build minified bundle:
find src/pytaku/js-src -name '*.js' | entr -rc \
     esbuild src/pytaku/js-src/main.js \
     --bundle --sourcemap --minify \
     --outfile=src/pytaku/static/js/main.min.js
```

## Tests

Can be run with just `pytest`. It needs a pytaku.conf.json as well.

## Code QA tools

- Python: black, isort, flake8 without mccabe
- JavaScript: jshint, prettier

```sh
doas pacman python-black python-isort flake8 prettier
npm install -g --prefix ~/.node_modules jshint
```

# Production

```sh
pip install --user --upgrade pip
pip install --user pytaku
pip install https://github.com/rogerbinns/apsw/releases/download/3.32.2-r1/apsw-3.32.2-r1.zip \
      --global-option=fetch --global-option=--version --global-option=3.32.2 --global-option=--all \
      --global-option=build --global-option=--enable-all-extensions

pytaku-generate-config > pytaku.conf.json
# fill stuff as needed

# run migration script once
pytaku-migrate

# run 2 processes:
pytaku -w 7  # production web server - args are passed as-is to gunicorn
pytaku-scheduler  # scheduled tasks e.g. update titles

# upgrades:
pip install --user --upgrade pytaku
pytaku-migrate
# then restart `pytaku` & `pytaku-scheduler` processes
```

I don't have to remind you to properly set up a firewall and a TLS-terminating
reverse proxy e.g. nginx/caddy, right?

# LICENSE

Copyright (C) 2020  Bùi Thành Nhân

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
