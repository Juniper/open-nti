

PWD = $(shell pwd)

build:
	docker build -t juniper/open-nti-input-jti .

run:
	docker run -t -i -v $(PWD):/data juniper/open-nti-input-jti

sh:
	docker run -t -i juniper/open-nti-input-jti sh
