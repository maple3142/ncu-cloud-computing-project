FROM node:18-alpine

RUN adduser \
    --disabled-password \
    --gecos "" \
    --uid "1001" \
    "ctf"

COPY app.js /
USER ctf
CMD ["node", "app.js"]
