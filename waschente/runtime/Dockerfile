FROM alpine

LABEL maintainer "Yushin Washio <yuwash at yandex dot com>"

RUN set -ex \
	&& apk update \
	&& apk add --no-cache \
		xvfb \
		dbus-x11 \
		qt5-qtbase-x11 \
		qt5-qtbase-postgresql

RUN mkdir /entehome
WORKDIR /entehome
ENV XVFB_WHD 1280x720x16
CMD ["sh", "-c", "Xvfb :99 -screen 0 $XVFB_WHD & xvfbps=$! && DISPLAY=:99.0 ./waschente \"$@\"; wait $xvfbps"]
