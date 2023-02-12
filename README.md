Live demo: https://pytaku.imnhan.com
(db may be hosed any time, also expect bugs)

Production instance coming When It's Ready (tm).

# Pytaku [![builds.sr.ht status](https://builds.sr.ht/~nhanb/pytaku/commits/master.svg)](https://builds.sr.ht/~nhanb/pytaku/commits/master?)

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
poetry install
pip install --upgrade pip
pip install https://github.com/rogerbinns/apsw/releases/download/3.34.0-r1/apsw-3.34.0-r1.zip \
      --global-option=fetch --global-option=--version --global-option=3.34.0 --global-option=--all \
      --global-option=build --global-option=--enable-all-extensions
# (using apsw 3.34 here to match the version on debian 11)

pytaku-generate-config > pytaku.conf.json
# fill stuff as needed

# run migration script once
pytaku-migrate

# run 2 processes:
pytaku-dev -p 8000  # development webserver
pytaku-scheduler  # scheduled tasks e.g. update titles


## Frontend ##

sudo pacman -S entr  # to watch source files
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
sudo pacman python-black python-isort flake8 prettier
npm install -g --prefix ~/.node_modules jshint
```

# Production

**Gotcha:** mangasee image servers will timeout if you try to download images
via ipv6, so you'll need to disable IPv6 on your VM. It's unfortunate that
python-requests [doesn't][https://github.com/psf/requests/issues/1691] have an
official way to specify ipv4/ipv6 on its API, and I'm too lazy to figure out
alternatives.

I'm running my instance on Debian 11, but any unix-like environment with these
should work:

- python3.7+
- apsw (on Debian, simply install the `python3-apsw` package)
- the rest are all pypi packages that should be automatically installed when
  you run `pip install pytaku`

The following is a step-by-step guide on Debian 11.

```sh
sudo apt install python3-pip python3-apsw
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

Alternatively, just setup a personal [tailscale](https://tailscale.com/)
network and let them worry about access control and end-to-end encryption for
you.

## Optional optimization

With the setup above, you're serving static assets using gunicorn, which is not
ideal performance-wise. For private usage this doesn't really matter. However,
if you want to properly serve static assets using nginx and the like, you can
copy all static assets into a designated directory with:

```sh
pytaku-collect-static target_dir
```

This will copy all assets into `target_dir/static`. You can now instruct
nginx/caddy/etc. to serve this dir on `/static/*` paths. There's an example
caddyfile to do this in the ./contrib/ dir.

# LICENSE

Copyright (C) 2021 Bùi Thành Nhân

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
