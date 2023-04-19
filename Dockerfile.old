FROM python:latest

ARG NEWUSER

RUN apt update && \
    apt install -y npm 

RUN useradd -ms /bin/bash $NEWUSER
RUN adduser $NEWUSER sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /home/$NEWUSER/

RUN npm install -g @vue/cli && \
    npm install --save-dev eslint eslint-plugin-vue
RUN npm i axios


USER $NEWUSER

COPY requirements.txt .
RUN pip install -r requirements.txt
