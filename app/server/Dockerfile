FROM python:3.11

RUN mkdir /service/
COPY ./src/ /service/
WORKDIR /service/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

expose 443

ENTRYPOINT ["python", "server_stub.py"]