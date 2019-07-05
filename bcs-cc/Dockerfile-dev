FROM golang:1.12.6-stretch
WORKDIR /data
ADD . .
RUN make clean && make && cp ./bin/bcs_cc /usr/local/bin/