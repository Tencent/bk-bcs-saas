FROM busybox:latest

RUN rm -rf `ls /bin/* | egrep -v 'mv|cd|sh|grep|sleep|ls'`

ADD ./kubectl /bin/

ENTRYPOINT ["/bin/sh", "-c", "while true; do sleep 60;done"]
