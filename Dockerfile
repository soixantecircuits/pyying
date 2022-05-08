# syntax=docker/dockerfile:latest
FROM python:2.7.18

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        python-pygame \
        gphoto2 \
        libgphoto2-dev \
        libjpeg62-turbo-dev \
        imagemagick \
        subversion

#pyying
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# RUN pip install gphoto2 pyOSC pygame

# mjpg_streamer
# RUN svn co https://svn.code.sf.net/p/mjpg-streamer/code/mjpg-streamer
# RUN cd mjpg-streamer && sed -i -e '32,33s/^/\/\/ /' utils.c && make && make install
COPY . .
EXPOSE 8087 8010
CMD ["sh", "run.sh"]
# CMD ["python", "./pyying.py" "--nowindow", "true"]
