FROM node:20.11.1-alpine3.19

RUN npm install -g http-server

RUN apk update && apk add --no-cache supervisor

WORKDIR /app

COPY frontend/package.json ./

RUN npm install

COPY frontend/. .

RUN npm run build

EXPOSE 3000 

#CMD ["http-server","dist"]
CMD ["npm","start"]