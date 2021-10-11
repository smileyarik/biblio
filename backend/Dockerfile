FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y git nginx supervisor uwsgi vim

ADD requirements.txt /code/
WORKDIR /code/
RUN pip install -r requirements.txt

COPY . /code
RUN chmod -R 755 /code/
RUN chmod +x /code/run.sh
CMD ["/code/run.sh"]
