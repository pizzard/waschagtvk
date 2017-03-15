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
  id INTEGER PRIMARY KEY NOT NULL,
  zweck INTEGER,
  wert INTEGER
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
  von INTEGER REFERENCES users(id),
  termine INTEGER  -- FOREIGN KEY REFERENCES termine(id)
);
CREATE TABLE waschmaschinen (
  id INTEGER PRIMARY KEY NOT NULL,
  status INTEGER,  -- 0: sperre (red, defekt), 1: not sperre (black, betriebsbereit), else: sperre (black)
  bemerkung VARCHAR(255),
  von INTEGER REFERENCES users(id)
);
CREATE TABLE finanzlog (
  enduser INTEGER REFERENCES users(id),
  bestand INTEGER,
  aktion INTEGER,  -- betrag
  bemerkung VARCHAR(255),
  datum DATE,
  bonus VARCHAR(7),  -- not INTEGER because sometimes ''
  id SERIAL PRIMARY KEY
);
CREATE TABLE termine (
  id INTEGER PRIMARY KEY NOT NULL,
  wochentag INTEGER,
  datum DATE,
  zeit TIMESTAMP,
  bonus BOOLEAN,
  enduser INTEGER REFERENCES users(id),
  maschine INTEGER REFERENCES waschmaschinen(id)
);
ALTER TABLE users ADD CONSTRAINT FK_termine FOREIGN KEY (termine) REFERENCES termine(id);
CREATE TABLE waschagtransaktionen (
  enduser INTEGER REFERENCES users(id),
  aktion INTEGER,
  bestand INTEGER,
  bemerkung VARCHAR(255),
  datum DATE,
  id SERIAL PRIMARY KEY
);
CREATE TABLE preise (
  id INTEGER PRIMARY KEY NOT NULL,
  preis INTEGER,
  tag INTEGER,  -- 0..6 weekday
  zeit INTEGER  -- 0..15 available slots
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
INSERT INTO users (login,pw,status) VALUES ('w','b',9);
INSERT INTO waschmaschinen (id,status) VALUES (0,0);
INSERT INTO waschmaschinen (id,status) VALUES (1,1);
INSERT INTO waschmaschinen (id,status) VALUES (2,2);
