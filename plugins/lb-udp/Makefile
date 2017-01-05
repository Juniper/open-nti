

PWD = $(shell pwd)

build:
	docker build -t juniper/open-nti-lb-udp:consul .

# run:
# 	docker run -t -i -v $(PWD):/data juniper/open-nti-lb-udp /usr/bin/python /data/netconf-collector.py -s --hosts=dev-01.yaml --commands=commands.yaml --credential=credentials.yaml
#
start:
	docker run -t -i -v $(PWD):/source \
			juniper/open-nti-lb-udp /usr/sbin/nginx

sh:
	docker run -t -i \
		-v $(PWD):/source \
		-l consul:consul \
		juniper/open-nti-lb-udp:consul sh
