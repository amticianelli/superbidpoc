FROM node:20.11.1-alpine3.19 AS frontend  
RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app

WORKDIR /home/node/app 
COPY ./frontend/package*.json ./  
USER node
RUN npm ci  
COPY --chown=node:node ./frontend/ ./frontend  
#COPY --chown=node:node ./frontend/public/ ./static  
WORKDIR /home/node/app/frontend
RUN NODE_OPTIONS=--max_old_space_size=8192 npm run build
  
FROM python:3.12-alpine 
RUN apk add --no-cache --virtual .build-deps \  
    build-base \  
    libffi-dev \  
    openssl-dev \  
    curl \  
    && apk add --no-cache \  
    libpq 
  
COPY ./backend/requirements.txt /usr/src/app/  
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt \  
    && rm -rf /root/.cache
  
COPY ./backend/. /usr/src/app/  
COPY --from=frontend /home/node/app/build  /usr/src/app/static/
WORKDIR /usr/src/app  
EXPOSE 80  

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"] 