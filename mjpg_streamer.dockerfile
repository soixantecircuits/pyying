# syntax=docker/dockerfile:latest
FROM alpine:latest as build
LABEL maintainer="Valeriu Stinca <ts@strat.zone>"
LABEL version="0.0.1-beta"
LABEL vendor="Strategic Zone"
LABEL release-date="2022-04-25"

RUN apk --no-cache add \
  build-base \
  cmake \
  libjpeg-turbo-dev \
  linux-headers \
  openssl

# Install mjpg-streamer
RUN wget -qO- https://github.com/jacksonliam/mjpg-streamer/archive/master.tar.gz | tar xz
WORKDIR /mjpg-streamer-master/mjpg-streamer-experimental
RUN make && make install

# Build final image
FROM alpine:latest
LABEL maintainer="Valeriu Stinca <ts@strat.zone>"
LABEL version="0.0.1-beta"
LABEL vendor="Strategic Zone"
LABEL release-date="2022-04-25"

RUN apk --no-cache add ffmpeg libjpeg openssh-client v4l-utils

COPY --from=build /usr/local/bin/mjpg_streamer /usr/local/bin
COPY --from=build /usr/local/lib/mjpg-streamer /usr/local/lib
COPY --from=build /usr/local/share/mjpg-streamer /usr/local/share
COPY ./mjpg_streamer.sh /usr/local/bin/mjpg_streamer.sh
RUN chmod +x /usr/local/bin/mjpg_streamer.sh
EXPOSE 36700

CMD ["/usr/local/bin/mjpg_streamer.sh"]