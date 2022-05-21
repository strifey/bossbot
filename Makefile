venv: requirements.txt
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

upgrade-requirements: requirements-minimal.txt
	python3 -m venv upgrade
	upgrade/bin/pip install -r requirements-minimal.txt
	upgrade/bin/pip freeze > requirements.txt
	rm -rf upgrade
