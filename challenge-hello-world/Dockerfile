FROM alpine:3

RUN apk add --no-cache socat

RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "1000" \
    "ctf"

COPY start.sh /
CMD ["socat", "TCP-LISTEN:8888,fork", "EXEC:'/start.sh',stderr,su=ctf"]
