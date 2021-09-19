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

# Keyboard shortcuts

On Chapter page, press `?` to show keyboard shortcuts.

# Development

```sh
## Backend ##
doas pacman -S nodejs  # used by cloudscraper to bypass Cloudflare

poetry install
pip install --upgrade pip
pip install https://github.com/rogerbinns/apsw/releases/download/3.34.0-r1/apsw-3.34.0-r1.zip \
      --global-option=fetch --global-option=--version --global-option=3.34.0 --global-option=--all \
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

### Dumb proxy

Eventually mangasee started using a somewhat aggressive cloudflare protection
so cloudscraper alone is not enough (looks like our IP got blacklisted or
throttled all the time), so now I have to send requests through a crappy
[GAE-based proxy](https://git.sr.ht/~nhanb/gae-proxy). You'll need to spin up
your own proxy instance (Google App Engine free tier is enough for personal
use), then fill out OUTGOING_PROXY_NETLOC and OUTGOING_PROXY_KEY accordingly.

Yes it's not a standards-compliant http(s) proxy so you can't just use yours. I
chose the cheapest (free) way to get a somewhat reliable IP-rotating proxy.

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

This assumes Debian 11, consequently targeting python 3.9.

```sh
# nodejs is used by cloudscraper to bypass Cloudflare
sudo apt install nodejs python3-pip python3-apsw
pip3 install --user pytaku
# now make sure ~/.local/bin is in your $PATH so pytaku commands are usable

pytaku-generate-config > pytaku.conf.json
# fill stuff as needed

# run migration script once
pytaku-migrate

# run 2 processes:
pytaku -w 7  # production web server - args are passed as-is to gunicorn
pytaku-scheduler  # scheduled tasks e.g. update titles

# don't forget to setup your proxy, same as in development:
# https://git.sr.ht/~nhanb/gae-proxy

# upgrades:
pip3 install --user --upgrade pytaku
pytaku-migrate
# then restart `pytaku` & `pytaku-scheduler` processes
```

If you're exposing your instance to the internet, I don't have to remind you to
properly set up a firewall and a TLS-terminating reverse proxy e.g.
nginx/caddy, right?

Alternatively, just setup [tailscale](https://tailscale.com/) and let them
worry about access control and end-to-end encryption for you.

# LICENSE

Copyright (C) 2021  Bùi Thành Nhân

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
