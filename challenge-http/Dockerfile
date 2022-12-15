FROM node:18-alpine

RUN apk add tini --no-cache
RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "1001" \
    "ctf"

COPY app.js /
USER ctf
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "app.js"]
