FROM alpine:3

RUN apk add --no-cache socat

CMD ["socat", "TCP-LISTEN:8888,fork", "EXEC:'echo hello world'"]

# eval $(minikube docker-env)
# docker build . -t challenge-hello-world:latest
