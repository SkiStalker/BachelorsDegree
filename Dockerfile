FROM ubuntu:latest

RUN apt-get update
RUN apt-get dist-upgrade -y

RUN DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update
RUN apt-get -y dist-upgrade
RUN apt-get -y install net-tools nginx  python3.11  python3.11-full curl apt-transport-https gpg findutils gettext-base grep
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

RUN curl -LO https://dl.k8s.io/release/`curl -LS https://dl.k8s.io/release/stable.txt`/bin/linux/amd64/kubectl

RUN chmod +x ./kubectl

RUN mv ./kubectl /usr/local/bin/kubectl

RUN pip3.11 install --upgrade pip
RUN pip3.11 install supervisor



RUN mkdir -p /app/secrets/
COPY ./secrets/vars.env /app/secrets/vars.env


RUN mkdir -p /app/controller/
COPY ./app/controller/src /app/controller/

RUN mkdir -p /app/frontend/

COPY ./frontend/diploma/out/ /app/frontend/

RUN rm -rf /etc/nginx/sites-*

COPY ./frontend/nginx/ /etc/nginx/conf.d/

COPY ./supervisord.conf /etc/supervisord.conf

RUN pip3.11 install -r /app/controller/requirements.txt

RUN mkdir -p /root/.kube

COPY kubectl/config.yaml /root/.kube/config

RUN env -S $(grep -v '^#' /app/secrets/vars.env) envsubst < /root/.kube/config > /root/.kube/_config

RUN mv /root/.kube/_config /root/.kube/config

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/supervisord"]