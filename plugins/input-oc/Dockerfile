FROM golang:1.8.5-jessie
RUN mkdir /go/src/github.com
RUN mkdir /go/src/github.com/influxdata
WORKDIR /go/src/github.com/influxdata

RUN go get -u -v google.golang.org/grpc

RUN apt-get update &&\
    apt-get install -y unzip wget

RUN git clone https://github.com/ajhai/telegraf.git

WORKDIR /go/src/github.com/influxdata/telegraf

RUN make

RUN mkdir /source
WORKDIR /source

#COPY telegraf.toml /source/telegraf.toml

COPY start-input-oc.sh /source/start-input-oc.sh
RUN chmod +x /source/start-input-oc.sh

CMD ["/source/start-input-oc.sh"]
# CMD /go/bin/telegraf -debug
