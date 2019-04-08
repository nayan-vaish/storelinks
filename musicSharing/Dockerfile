FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /music_sharing
WORKDIR /music_sharing
COPY requirements.txt /music_sharing/
RUN pip3 install -r requirements.txt
COPY . /music_sharing/
