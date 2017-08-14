-- this is highly experimental!

-- DROP TABLE users CASCADE;
-- DROP TABLE finanzlog;
-- DROP TABLE termine CASCADE;
-- DROP TABLE waschagtransaktionen;
-- DROP TABLE preise;
-- DROP TABLE notify;
-- DROP TABLE doku_deu;
-- DROP TABLE doku_eng;

CREATE TABLE config (
  zweck VARCHAR(64) PRIMARY KEY NOT NULL,
  wert FLOAT
);
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  pw VARCHAR(15),
  ip VARCHAR(15),  -- ip saved as string...
  name VARCHAR(15),
  nachname VARCHAR(15),
  login VARCHAR(15),
  zimmer INTEGER,
  gesperrt BOOLEAN,
  status INTEGER,  -- 1: enduser, 3: exWaschag, 5: waschag, 7: admin, 9: god
  message VARCHAR(4095),
  bemerkung VARCHAR(256),
  lastlogin TIMESTAMP,
  gotfreimarken BOOLEAN,
  termine INTEGER  -- number of used appointments
);
ALTER TABLE users ADD von INTEGER REFERENCES users(id);
CREATE TABLE waschmaschinen (
  id INTEGER PRIMARY KEY NOT NULL,
  status INTEGER,  -- 0: sperre (red, defekt), 1: not sperre (black, betriebsbereit), else: sperre (black)
  bemerkung VARCHAR(255),
  von INTEGER REFERENCES users(id)
);
CREATE TABLE finanzlog (
  "user" INTEGER REFERENCES users(id),  -- user is a keyword! https://dev.mysql.com/doc/refman/5.7/en/keywords.html
  bestand INTEGER,
  aktion INTEGER,  -- betrag
  bemerkung VARCHAR(255),
  datum DATE,
  bonus VARCHAR(7),  -- not INTEGER because sometimes ''
  id SERIAL PRIMARY KEY
);
CREATE TABLE termine (
  "user" INTEGER REFERENCES users(id),
  zeit INTEGER,
  maschine INTEGER REFERENCES waschmaschinen(id),
  datum DATE,
  wochentag INTEGER,
  bonus BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (zeit, maschine, datum)
);
CREATE TABLE waschagtransaktionen (
  "user" INTEGER REFERENCES users(id),
  aktion INTEGER,
  bestand INTEGER,
  bemerkung VARCHAR(255),
  datum DATE,
  id SERIAL PRIMARY KEY
);
CREATE TABLE preise (
  zeit INTEGER,  -- 0..15 available slots
  tag INTEGER,  -- 0..6 weekday
  preis INTEGER,
  id SERIAL PRIMARY KEY
);
CREATE TABLE notify (
  id INTEGER PRIMARY KEY NOT NULL,  -- compared with users.id
  ziel INTEGER,
  datum DATE
);
CREATE TABLE doku_eng (
  paragraph INTEGER,
  abschnitt INTEGER,
  satz INTEGER,
  titel VARCHAR(4095),
  inhalt VARCHAR(16383),
  id SERIAL PRIMARY KEY
);
CREATE TABLE doku_deu (
  paragraph INTEGER,
  abschnitt INTEGER,
  satz INTEGER,
  titel VARCHAR(4095),
  inhalt VARCHAR(16383),
  id SERIAL PRIMARY KEY
);
INSERT INTO users (login,pw,status) VALUES ('w','pszA9..xmmgb6',9);  -- pw=crypt('b','ps')
INSERT INTO waschmaschinen (id,status) VALUES (1,0);
INSERT INTO waschmaschinen (id,status) VALUES (2,1);
INSERT INTO waschmaschinen (id,status) VALUES (3,2);
INSERT INTO config (zweck, wert) VALUES
  ( 'Stornierzeit (in Min)',    5 ),
  ( 'Antrittszeit (in Min)',   15 ),
  ( 'minimaler Einzahlbetrag (in Euro)',    5 ),
  ( 'Termine pro Monat',   12 ),
  ( 'Relaiszeit (in Min)',    5 ),
  ( 'Freigeld fuer WaschAG',   12 ),
  ( 'Vorhaltezeit Kontodaten (in Monaten)',    3 ),
  ( 'Vorhaltezeit WAG-Kontodaten (in Monaten)',    8 );
