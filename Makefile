dev:
	pytaku-manage runserver

test: lint djangotest

djangotest:
	pytaku-manage test --settings=pytaku.test_settings

shell:
	pytaku-manage shell

lint:
	flake8
	black --check .
	isort --check-only --recursive .

localconfig:
	pytaku-generate-config > pytaku.conf.json

clean:
	rm -rf dist
	rm -rf src/pytaku.egg-info

startdb:
	docker-compose up -d

destroydb:
	docker-compose down
	sudo rm -rf pgdata
