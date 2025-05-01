Live demo: https://pytaku.imnhan.com
(db may be hosed any time, also expect bugs)

Production instance coming When It's Ready (tm).

# Pytaku

Pytaku is a WIP web-based manga reader that keeps track of your reading
progress and new chapter updates. Its design goals are:

- Self-host friendly - if you have a UNIX-like server with python3.11+ and can
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
uv sync

pytaku-generate-config > pytaku.conf.json
# fill stuff as needed

# run migration script once
pytaku-migrate

# run 2 processes:
pytaku-dev -p 8000  # development webserver
pytaku-scheduler  # scheduled tasks e.g. update titles


## Frontend ##

sudo pacman -S entr esbuild

# Listen for changes in js-src dir, automatically build minified bundle:
find src/pytaku/js-src -name '*.js' | entr -rc ./build.py js
```

We use `build.py` as a less annoying Makefile.

### Optional proxy

Weebcentral's previous incarnation, mangasee, used to deploy a somewhat
aggressive cloudflare protection level that cloudscraper alone couldn't
bypass. So I had to send requests through a crappy [GAE-based
proxy](https://github.com/nhanb/gae-proxy). Apparently it isn't necessary
anymore.

FWIW, in order to use it, you'll need to deploy your own gae-proxy on Google App
Engine, then fill out `OUTGOING_PROXY_NETLOC` and `OUTGOING_PROXY_KEY`
accordingly.

Yes it's not a standards-compliant http(s) proxy so you can't just use yours. I
chose the cheapest (free) way to get a somewhat reliable IP-rotating proxy.

## Tests

Can be run with just `pytest`. It needs a pytaku.conf.json as well.

## Code QA tools

- Python: ruff
- JavaScript: jshint, prettier

```sh
sudo pacman -S ruff prettier
npm install -g --prefix ~/.node_modules jshint
```

# Production

I'm running my instance on Debian 12, but any unix-like environment with these
should work:

- python3.11+
- the rest are all pypi packages that should be automatically installed when
  you run `pip install pytaku`

The following is a step-by-step guide on Debian 12 using pipx for demonstration
purposes. It's possible to use any python isolation technique (virtualenv, venv,
etc.) - personally I'm running pytaku in production using a venv.

```sh
sudo apt install pipx
pipx install pytaku
# you now have access to pytaku commands

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
pipx upgrade pytaku
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
nginx/caddy/etc. to serve this dir on `/static/*` paths.

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
