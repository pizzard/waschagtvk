# FROM alpine:edge
# FROM httpd
FROM eboraas/apache

RUN apt-get update && apt-get -y install \
        libdbd-pg-perl \
        libapache-dbi-perl \
        libconfig-inifiles-perl \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

# apache2-mod-perl only available in testing
# RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories
# RUN set -ex \
	# && apk add --no-cache \
		# perl-dbd-pg \
		# # apache2-mod-perl \
		# perl-config-inifiles

RUN sed -i \
        -e 's|\(\s*\)<Directory /usr/lib/cgi-bin>|\1ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/\n&|1' \
        -e 's|\(\s*\)</Directory>|\1Options ExecCGI\n\1AddHandler cgi-script cgi pl\n&|1' \
        /etc/apache2/sites-available/default-ssl.conf \
        && a2enmod cgi
