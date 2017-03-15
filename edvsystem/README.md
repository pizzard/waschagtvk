# edvsystem

Web server of waschagtvk

## Dependencies

* libdbd-mysql-perl
* libapache-dbi-perl
* libconfig-inifiles-perl

## Installation

* Put this folder in `/usr/lib/cgi-bin`
* Enable CGI in the apache config file at `/etc/apache2/sites-available/default-ssl.conf` (the name/location can differ depending on your system) by adding the line
  
  `ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/`

  before `<Directory /usr/lib/cgi-bin>` and adding

  `Options ExecCGI`

  somewhere before `</Directory>`.

Finally run

```
sudo a2enmod cgi
sudo service apache2 restart
```

For the system to get actually functional, the database also needs to be setup with the credentials configured in the [inc/config.ini](inc/config.ini) beforehand. The [setup.sql](../setup.sql) script might be useful for testing.
