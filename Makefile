#!make

all: depend test

test: check_format

depend:
	python3 -m pip install black

format:
	python3 -m black --line-length=88 athena-*/**/*.py athena-*/*.py

check_format:
	python3 -m black --line-length=88 --diff --verbose --check athena-*/**/*.py --check athena-*/*.py

install_server:
	cd ./athena-server
	python3 setup.py install
	mkdir -p /opt/athena/voice
	mkdir -p /etc/athena
	cp -rf ./athena-server/*.json /etc/athena/
	cp -rf ./athena-server/*.service /opt/athena/

install_client:
	cd ./athena-client
	python3 setup.py install
	mkdir -p /opt/athena/voice
	mkdir -p /opt/athena/wake
	mkdir -p /etc/athena
	mkdir -p /home/athena
	useradd -d /home/athena athena
	chmod +x /home/athena
	cp -rf ./athena-client/*.py /opt/athena/
	cp -rf ./athena-client/*.json /etc/athena/
	cp -rf ./athena-client/*.service /opt/athena/
	cp -rf ./athena-client/*.ppn /opt/athena/wake
