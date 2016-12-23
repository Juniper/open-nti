

PWD = $(shell pwd)

build:
	docker build -t juniper/open-nti-input-netconf .

run:
	docker run -t -i -v $(PWD):/data juniper/open-nti-input-netconf /usr/bin/python /data/netconf-collector.py -s --hosts=dev-01.yaml --commands=commands.yaml --credential=credentials.yaml

start:
	docker run -t -i -v $(PWD):/data juniper/netconf-collector /usr/bin/telegraf --debug --config /data/telegraf.toml

sh:
	docker run -t -i juniper/open-nti-input-netconf sh
