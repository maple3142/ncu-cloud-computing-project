FROM alpine:3

RUN apk add --no-cache socat

RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "1000" \
    "ctf"

CMD ["socat", "TCP-LISTEN:8888,fork", "EXEC:'/bin/sh',stderr,su=ctf"]

# eval $(minikube docker-env)
# docker build . -t challenge-hello-world:latest
