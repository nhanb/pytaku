```sh
poetry install
pip install --upgrade pip
pip install https://github.com/rogerbinns/apsw/releases/download/3.32.2-r1/apsw-3.32.2-r1.zip \
      --global-option=fetch --global-option=--version --global-option=3.32.2 --global-option=--all \
      --global-option=build --global-option=--enable-all-extensions

FLASK_ENV=development FLASK_APP=pytaku.main:app flask run

pytaku-generate-config > pytaku.conf.json
# fill stuff as needed

# run migration script once
pytaku-migrate

# run 2 processes:
pytaku -w 7 -b 0.0.0.0:5001  # web server
pytaku-scheduler  # scheduled tasks e.g. update titles
```
