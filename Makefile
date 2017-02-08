install::
	virtualenv venv -p python3; \
	pip install -r requirements.txt

run::
	. ./venv/bin/activate; \
	python3 main.py
