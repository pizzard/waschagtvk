FROM alpine

LABEL maintainer "Yushin Washio <yuwash at yandex dot com>"

# in alpine:edge required for qt5-qtbase-dev:
# RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories
RUN set -ex \
	&& apk update \
	&& apk add --no-cache \
		build-base \
		qt5-qtbase-dev
		# qt5-qtbase-postgresql contained in qt5-qtbase-dev
RUN ln -s qmake-qt5 /usr/bin/qmake

ENV CC=/usr/bin/cc CXX=/usr/bin/c++

RUN mkdir /waschente
WORKDIR /waschente
CMD ["sh", "-c", "qmake \"DESTDIR=./runtime/entehome\" && make"]
