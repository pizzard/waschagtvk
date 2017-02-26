#include <iostream>
#include <QShortcut>
#include <QtGui>
#include <QInputDialog>
#include <QLineEdit>
#include <QMessageBox>
#include <QFont>
#include <QVariant>
#include "WashingProgram.h"
#include "TerminVerwaltung.h"
#include "Hilfsfunktionen.h"
#include "relais.h"
#include "crypt.h"
#include <exception>

// Zuordnung der Maschinen
// Maschinennummer nicht �ndern, die Zahl hinter dem "=" steht f�r das Relais, an dem die jeweilige Maschine angeschlossen ist
const std::array<const int,3> TerminVerwaltung::maschinenNr{
	1,  // Maschine 1 an Relais 1
	2,  // Maschine 2 an Relais 2
	3   // Maschine 3 an Relais 3
};

TerminVerwaltung::TerminVerwaltung(QWidget *parent):
	QWidget(parent),
	timer(this),
	timer2(this),
	messageBox("Nachrichtenfenster"),
	control("Termin wahrnehmen")
{
	// Das Nachrichtenfenster
	QFont message_schrift("Arial", 12, QFont::Bold);
	QString temp;
	sagEs[0] = "Programm Waschente (1.2) gestartet!";
	temp += QString("Programm Waschente (1.2) gestartet!") + "\n";
	for (int i = 1; i < 5; i++){
		sagEs[i] = QString("");
		temp += QString("") + "\n";
	}
	message.setText(temp);
	message.setFont(message_schrift);
	message.setWordWrap(true);
	messageLayout.addWidget(&message);
	messageBox.setLayout(&messageLayout);

	//Fortschrittsbalken
	balken.setTextVisible(false);
	QFont balken_schrift("Arial", 13, QFont::Bold);
	QPalette pal;
	pal.setColor(QPalette::WindowText, QColor(0,255,120)); 
	pal.setColor(QPalette::WindowText, QColor(0,0,0));
	balkenText.setFont(balken_schrift);
	balkenText.setPalette(pal);

	connect(&control, SIGNAL(clicked()), this, SLOT(iWannaWash()));

	db = QSqlDatabase::addDatabase("QMYSQL");

	try{
		getMaschinen();
		getConfig();
	}
	catch(std::exception& e)
	{
		gibMeldung(e.what());
	}

	box.resize(anzahl + 1);

	box.front().reset(new QGroupBox("Uhrzeit"));
	for (int i = 1; i <= anzahl; i++) {
		box[i].reset(new QGroupBox("Maschine " + QString::number(i)));
	}

	tabelle.resize(anzahl + 1);
	for (int i = 0; i <= anzahl; i++) {
		for (int k = 0; k < 3; k++) {
			tabelle[i][k].reset(new QLabel("Keine Informationen geladen!"));
			tabelle[i][k]->setWordWrap(true);
		}
	}

	QFont schrift[4] = {QFont("Arial", 12), QFont("Arial", 16, QFont::Bold), QFont("Arial", 12), QFont("Arial", 14, QFont::Bold)}; //Schriftart f�r Termin davor, Termin, Termin danach, Titel


	for (int i = 0; i <= anzahl; i++) {
		box[i]->setFont(schrift[3]);
		for (int k = 0; k < 3; k++) {
			tabelle[i][k]->setFont(schrift[k]);
		}
	}

	for(int i = 0; i < anzahl; i++) {
		aktStatus[i] = false;
	}

	layout.resize(anzahl + 1);
	for (int i = 0; i <= anzahl; i++) {
		layout[i].reset(new QVBoxLayout());
		for (int k = 0; k < 3; k++) {
			layout[i]->addWidget(tabelle[i][k].get()); //HIER FEHLER?
		}
		box[i]->setLayout(layout[i].get());
		layout_grid.addWidget(box[i].get(), 0, i);
	}

	layout_grid.addWidget(&balken, 1, 0, 1, anzahl+1);
	layout_grid.addWidget(&balkenText, 1, 0, 1, anzahl+1);
	layout_grid.addWidget(&messageBox, 2, 0, 1, anzahl+1);
	layout_grid.addWidget(&control, 3, 0, 1, anzahl+1);
	setLayout(&layout_grid);

	connect(&timer, SIGNAL(timeout()), this, SLOT(update()));
	//   connect(short_alt_f4, SIGNAL(activated()), this, SLOT(shortcutWarning()));

	timer.start(20000);

	connect(&timer2, SIGNAL(timeout()), this, SLOT(checkeMaschinen()));
	timer2.start(2000);


	try {
		printTabelle();
	}
	catch(std::exception& e)
	{
		gibMeldung(e.what());
	}



	for(int i = 0; i < 3; i++) {
		stoppeMaschine(maschinenNr[i]);
	}
}

void TerminVerwaltung::shortcutWarning() {
	gibMeldung(QString("Shortcuts sind nicht erlaubt!"));
}



void TerminVerwaltung::printTabelle() {
   int zeit = getNow();
   int davor;
   int danach;
   QString gestern;
   QString morgen;
   if (zeit > 0) {
      davor = zeit - 1;
      gestern = "(zeit = '" + QString::number(davor) + "' AND datum = CURDATE())";
   } else {
      davor = 15;
      gestern = "(zeit = '" + QString::number(davor) + "' AND datum = DATE_SUB(CURDATE(), INTERVAL 1 DAY))";
   }
   tabelle[0][0]->setText(gibWaschTermin(davor));
   tabelle[0][1]->setText(gibWaschTermin(zeit));
   if (zeit < 15) {
      danach = zeit + 1;
      morgen = "(zeit = '" + QString::number(danach) + "' AND datum = CURDATE())";
   } else {
      danach = 0;
      morgen = "(zeit = '" + QString::number(danach) + "' AND datum = DATE_ADD(CURDATE(), INTERVAL 1 DAY))";
   }
   tabelle[0][2]->setText(gibWaschTermin(danach));
   
   for (int i = 1; i <= anzahl; i++) {
      for (int k = 0; k < 3; k++) {
         if (status[i-1] == true) {
            tabelle[i][k]->setText("Termin frei");
         } else {
            tabelle[i][k]->setText("Maschine defekt");
         }
      }
   }

   QString anfrage = "SELECT user, maschine, zeit FROM termine WHERE (zeit = '" + QString::number(zeit) + "' AND datum = CURDATE()) OR " + gestern + " OR " + morgen;
   QSqlQuery qry = multiquery(anfrage, "Fehler Terminansicht!");
   while (qry.next()) {
	   QString anfrage = "SELECT name, nachname, zimmer FROM users WHERE id = '" + qry.value(0).toString() + "'";
	   QSqlQuery q = multiquery(anfrage, "Fehler Terminansicht!");
	   q.next(); // We know this exists
	   int zeile = qry.value(2).toInt()==davor?0:(qry.value(2).toInt()==zeit?1:2);
	   int spalte = qry.value(1).toInt();
	   tabelle[spalte][zeile]->setText(QString::fromUtf8(q.value(1).toString().toLatin1()) + ", " + QString::fromUtf8(q.value(0).toString().toLatin1()) + "   Zi. " + q.value(2).toString());
   }
}

void TerminVerwaltung::gibMeldung(QString nachricht) {
	nachricht = QDateTime::currentDateTime().toString() + ": " + nachricht;
   std::cout << nachricht.toLatin1().data() << std::endl;
   QString temp;
   for (int i = 4; i > 0; i--){
      sagEs[i] = sagEs[i-1];
   }
   sagEs[0] = nachricht;
   for (int i = 0; i < 5; i++){
      temp += sagEs[i] + "\n";
   }
   message.setText(temp);
}

bool TerminVerwaltung::verbindeDB() {
      db.close();
      db.setHostName(SERVER);
      db.setDatabaseName(USER);
      db.setUserName(USER);
      db.setPassword(PWORT);
      bool ok = db.open();
      return ok;
}

void TerminVerwaltung::iWannaWash() {
	try{
		bool ok = false;
		int id = 0;
		int maschine = 0;
		QString pwFromDb;
		QString pw;
		QString login = QInputDialog::getText(this, tr("Login"), tr("Bitte gib deinen Loginnamen ein.\nPlease enter your login nick."), QLineEdit::Normal, tr("Dein Nick"), &ok);
		if (login.contains(";") || login.contains("\"") || login.contains("\'")) {
			gibMeldung("Dieses Programm ist blöderweise gegen Injektion geschützt, du Affe! :P");
			return;
		}
		// Loginname
		if (ok) {
			ok = false;
			QString anfrage = "SELECT id, pw FROM users WHERE login = '" + login.toUtf8() + "'";
			QSqlQuery qry = multiquery(anfrage, "Fehler beim Login!");
			if (qry.next()) {
				id = qry.value(0).toInt();
				pwFromDb = qry.value(1).toString();
				ok = true;
			} else {
				QMessageBox::critical(this, QString("User unbekannt!"), QString("Der User ") + login + QString(" ist unbekannt! Vielleicht hast du dich vertippt?"), QMessageBox::Ok);
			}
		}
		// Passwort
		if (ok) {
			pw = QInputDialog::getText(this, tr("Login"), tr("Bitte gib dein Passwort ein.\nPlease enter your password."), QLineEdit::Password, tr(""), &ok);
			if (ok) {
				ok = false;
				char* buf = new char[66];
				pw = QString(crypt_r(pw.toUtf8().data(), "ps", buf));
				if (pw == pwFromDb) {
					ok = true;
				} else {
					QMessageBox::critical(this, QString("Passwort falsch!"), QString("Das eigegebene Passwort ist inkorrekt!\n Vielleicht hast du dich vertippt?"), QMessageBox::Ok);
				}
				delete [] buf;
			}
		}
		// Check, ob Termin da
		if (ok) {
			QString anfrage = "SELECT maschine FROM termine WHERE user = '" + QString::number(id) + "' AND zeit = '" + QString::number(getNow()) + "' AND datum = CURDATE()";
			QSqlQuery qry = multiquery(anfrage, "Fehler beim Login!");
			bool hadAppointment = false;
			while (qry.next()) {
				hadAppointment = true;
				maschine = qry.value(0).toInt();
				if (starteMaschine(maschine)) {
					QSqlQuery q(db);
					QString anfrage = "UPDATE termine SET wochentag = '8' WHERE user = '" + QString::number(id) + "' AND zeit = '" + QString::number(getNow()) + "' AND datum = CURDATE() AND maschine = '" + QString::number(maschine) + "'";
					if (q.prepare(anfrage)) {
						if (q.exec()) {
						} else {
							gibMeldung("Fehler beim Login! Query nicht ausgef�hrt: " + anfrage);
						}
					} else {
						gibMeldung("Fehler beim Login! Query nicht ausgef�hrt: " + anfrage);
					}
				}
			}
			if(!hadAppointment){
				QMessageBox::critical(this, QString("Kein Termin!"), QString("F�r dich ist gerade kein Termin gebucht! Termine k�nnen online gebucht werden.\nSiehe dazu mehr auf unserer Homepage."), QMessageBox::Ok);
			}
		}
	}
	catch(std::exception& e)
	{
		gibMeldung(e.what());
	}

}   

void TerminVerwaltung::getConfig() {
	QSqlQuery qry = multiquery("SELECT zweck, wert FROM config", "Fehler beim Holen der Konfiguration!");
	while (qry.next()) {
		QString task = qry.value(0).toString();
		if (task == "Antrittszeit (in Min)") {
			antritt = qry.value(1).toInt();
		} else if (task == "Relaiszeit (in Min)") {
			relais = qry.value(1).toInt();
		} else if (task == "Vorhaltezeit Kontodaten (in Monaten)") {
			vorhaltezeit = qry.value(1).toInt();
		} else if (task == "Vorhaltezeit WAG-Kontodaten (in Monaten)") {
			WAGvorhaltezeit = qry.value(1).toInt();
		}
	}
	QString anfrage = "SELECT id, status FROM waschmaschinen WHERE id <= " + QString::number(anzahl);
	qry = multiquery(anfrage, "Fehler beim Holen der Konfiguration!");
	while (qry.next()) {
		status[qry.value(0).toInt() - 1] = qry.value(1).toInt()==1?true:false;
	}
}

void TerminVerwaltung::getMaschinen() {
	QSqlQuery qry = multiquery("SELECT COUNT(*) FROM waschmaschinen", "Fehler beim Holen der Konfiguration!");
	while (qry.next()) {
		anzahl = qry.value(0).toInt();
		status.clear();
		status.resize(anzahl,0);
		aktStatus.clear();
		aktStatus.resize(anzahl,0);
	}
}

bool TerminVerwaltung::starteMaschine(int id) {
   if (differenz(QTime::currentTime(), countdown) <= (antritt * 60)) {
      aktStatus[id-1] = true;
      openPort(maschinenNr[id-1], true);
      gibMeldung("Maschine " + QString::number(id) + " entsperrt!");
      QPalette green;
      green.setColor(QPalette::WindowText, QColor(0,255,0));
      tabelle[id][1]->setPalette(green);
      return true;
   } else {
      QMessageBox::critical(this, QString("Zu spät!"), QString("Login ist nur bis spätestens ") + QString::number(antritt) + " Minuten nach Beginn des Termins möglich!", QMessageBox::Ok);
      return false;
   }
}
   
void TerminVerwaltung::stoppeMaschine(int id) {
   aktStatus[id-1] = false;
   openPort(maschinenNr[id-1], false);
}

void TerminVerwaltung::checkeMaschinen() {
	try {
		QPalette green;
		QPalette red;
		QPalette yellow;
		green.setColor(QPalette::WindowText, QColor(0,255,0));
		red.setColor(QPalette::WindowText, QColor(255,0,0));
		yellow.setColor(QPalette::WindowText, QColor(255,130,0));
		if (aktZeit != getNow()) {
			countdown = gibWaschZeit(getNow());
			aktZeit = getNow();
			balken.setRange(0, antritt*60);
			balkenText.setText("  Verbleibende Zeit um sich fuer den aktuellen Termin einzuloggen...");
			for (int i = 1; i <= anzahl; i++) {
				if (aktStatus[i-1]) {
					tabelle[i][1]->setPalette(green);
				} else {
					tabelle[i][1]->setPalette(yellow);
				}
		}
			speicherAlleFinanzen();
			speicherTermine();
			speicherFirewall();
			speicherWaschAgFinanzen();
		}
		int zeitDiff = differenz(QTime::currentTime(), countdown);

		if (zeitDiff > ((antritt + relais) * 60)) {
			for (int i = 0; i < anzahl; i++) {
				if (aktStatus[i]) {
					stoppeMaschine(i+1);
				}
			}
			if (balken.maximum() != 90*60) {
				balken.setRange(0, 90*60);
				balkenText.setText("  Verbleibende Zeit bis zum naechsten Termin...");
				for (int i = 1; i <= anzahl; i++) {
					if (aktStatus[i-1]) {
						tabelle[i][1]->setPalette(green);
					} else {
						tabelle[i][1]->setPalette(red);
					}
				}
			}
		} else if (zeitDiff > (antritt * 60)) {
			if (balken.maximum() != (antritt+relais)*60) {
				balken.setRange(0, (antritt+relais)*60);
				balkenText.setText("  Verbleibende Zeit um die Maschine zu starten...");
				for (int i = 1; i <= anzahl; i++) {
					if (aktStatus[i-1]) {
						tabelle[i][1]->setPalette(green);
					} else {
						tabelle[i][1]->setPalette(red);
					}
				}
			}
		}
		balken.setValue(zeitDiff);
	}
	catch(std::exception& e)
	{
		gibMeldung(e.what());
	}
}

void TerminVerwaltung::update() {
	try{
		getConfig();
		printTabelle();
	}
	catch(std::exception& e)
	{
		gibMeldung(e.what());
	}
}

bool TerminVerwaltung::speicherAlleFinanzen() {
   QByteArray buffer = QByteArray();
   QString dateiname;
   QDir directory;
   if (!directory.exists("finanzlog")) {
      directory.mkdir("finanzlog");
   }
   QSqlQuery qry = multiquery("SELECT id, name, nachname FROM users", "Fehler beim Speichern der Finanzen!");
   while (qry.next()) {
	   buffer = "";
	   dateiname = "./finanzlog/" + QString::fromUtf8(qry.value(2).toString().toLatin1()) + "_" + QString::fromUtf8(qry.value(1).toString().toLatin1()) + "_" + qry.value(0).toString() + ".txt";
	   QFile datei(dateiname, this);
	   if (QFile::exists(dateiname)) {
	   } else {
		   buffer += "Datum\tBestand\tAktion\tBemerkung\n";
	   }
	   QString anfrage = "SELECT bestand, aktion, bemerkung, datum FROM finanzlog WHERE user = '" + qry.value(0).toString() + "' AND datum < DATE_SUB(CURDATE(), INTERVAL " + QString::number(vorhaltezeit) + " MONTH) AND datum != (SELECT datum FROM finanzlog WHERE user = '" + qry.value(0).toString() + "' ORDER BY datum DESC LIMIT 1)";
	   int count = 0;
	   QSqlQuery q = multiquery(anfrage, "Fehler beim Speichern der Finanzen!" );
	   while (q.next()) {
		   count++;
		   buffer += q.value(3).toString() + " \t " + q.value(0).toString() + " \t " + q.value(1).toString() + " \t " +  QString::fromUtf8(q.value(2).toString().toLatin1()) + " \n";
	   }
	   anfrage = "DELETE FROM finanzlog WHERE user = '" + qry.value(0).toString() + "' AND datum < DATE_SUB(CURDATE(), INTERVAL " + QString::number(vorhaltezeit) + " MONTH) ORDER BY datum ASC LIMIT " + QString::number(count);
	   exec(anfrage, "Fehler beim Speichern der Finanzen!");
	   if (datei.open(QIODevice::Append)) {
		   datei.write(buffer);
		   datei.close();
	   } else {
		   gibMeldung("Fehler beim Speichern der Finanzen! Datei konnte nicht geschrieben werden " + dateiname);
		   return false;
	   }
   }
   return true;
}

bool TerminVerwaltung::speicherWaschAgFinanzen() {
   QByteArray buffer = QByteArray();
   QString dateiname;
   QDir directory;
   if (!directory.exists("waschagtransaktionen")) {
      directory.mkdir("waschagtransaktionen");
   }
      QString anfrage = "SELECT id, name, nachname FROM users WHERE status >= '" + QString::number(INACTIVE_WASCHAG_STATUS) + "'";
      QSqlQuery qry = multiquery(anfrage, "Fehler beim Speichern der WaschAG-Finanzen!");
      while (qry.next()) {
    	  buffer = "";
    	  dateiname = "./waschagtransaktionen/" + QString::fromUtf8(qry.value(2).toString().toLatin1()) + "_" + QString::fromUtf8(qry.value(1).toString().toLatin1()) + "_" + qry.value(0).toString() + ".txt";
    	  QFile datei(dateiname, this);
    	  if (QFile::exists(dateiname)) {
    	  } else {
    		  buffer += "Datum\tBestand\tAktion\tBemerkung\n";
    	  }
    	  anfrage = "SELECT bestand, aktion, bemerkung, datum FROM waschagtransaktionen WHERE user = '" + qry.value(0).toString() + "' AND datum < DATE_SUB(CURDATE(), INTERVAL " + QString::number(WAGvorhaltezeit) + " MONTH) AND datum != (SELECT datum FROM waschagtransaktionen WHERE user = '" + qry.value(0).toString() + "' ORDER BY datum DESC LIMIT 1)";
    	  QSqlQuery q =  multiquery(anfrage, "Fehler beim Speichern der WaschAG-Finanzen!");
    	  int count = 0;
    	  while (q.next()) {
    		  count++;
    		  buffer += q.value(3).toString() + " \t " + q.value(0).toString() + " \t " + q.value(1).toString() + " \t " +  QString::fromUtf8(q.value(2).toString().toLatin1()) + " \n";
    	  }
    	  anfrage = "DELETE FROM waschagtransaktionen WHERE user = '" + qry.value(0).toString() + "' AND datum < DATE_SUB(CURDATE(), INTERVAL " + QString::number(WAGvorhaltezeit) + " MONTH) ORDER BY datum ASC LIMIT " + QString::number(count);
    	  exec(anfrage, "Fehler beim Speichern der WaschAG-Finanzen!");
    	  if (datei.open(QIODevice::Append)) {
    		  datei.write(buffer);
    		  datei.close();
    	  } else {
    		  gibMeldung("Fehler beim Speichern der WaschAG-Finanzen! Datei konnte nicht geschrieben werden " + dateiname);
    		  return false;
    	  }
      }
   return true;
}

bool TerminVerwaltung::speicherFirewall() {
   QByteArray buffer = QByteArray();
   QString dateiname;
   QDir directory = QDir::current();
   if (!directory.exists("securitylog")) {
      directory.mkdir("securitylog");
   }
   QSqlQuery qry = multiquery("SELECT datum, id, ziel FROM notify WHERE YEAR(datum) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))", "Fehler beim Speichern des Firewalllogs!");
   while (qry.next()) {
	   buffer = "";
	   dateiname = "./securitylog/seclog_" + QString::number(QDate::currentDate().year() - 1) + ".txt";
	   QFile datei(dateiname, this);
	   if (QFile::exists(dateiname)) {
	   } else {
		   buffer += "Datum\tNachname\tVorname\tZugriffsversuch\n";
	   }
	   QString anfrage = "SELECT nachname, name FROM users WHERE id = '" + qry.value(1).toString() + "'";
	   QSqlQuery q = multiquery(anfrage, "Fehler beim Speichern des Firewalllogs!");
	   while (q.next()) {
		   buffer += qry.value(0).toString() + " \t " + q.value(0).toString() + " \t " + q.value(1).toString() + " \t " +  qry.value(2).toString() + " \n";
	   }
	   if (datei.open(QIODevice::Append)) {
		   datei.write(buffer);
		   datei.close();
	   } else {
		   gibMeldung("Fehler beim Speichern des Firewalllogs! Datei konnte nicht geschrieben werden " + dateiname);
		   return false;
	   }
   }
   exec("DELETE FROM notify WHERE YEAR(datum) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))", "Fehler beim Speichern des Firewalllogs!");
   return true;
}

bool TerminVerwaltung::speicherTermine() {
   QByteArray buffer = QByteArray();
   QString dateiname;
   QString gestern = "";
   QDate start;
   QDate ende;
   QDir directory = QDir::current();
   if (!directory.exists("waschlog")) {
      directory.mkdir("waschlog");
   }
   directory.cd("waschlog");
   int zeit;
   QSqlQuery qry = fetch("SELECT HOUR(NOW()), MINUTE(NOW()), SECOND(NOW())", "Fehler beim Speichern des Waschlogs!");
   zeit = getNowDB(qry.value(0).toInt(), qry.value(1).toInt(), qry.value(2).toInt());
   if (zeit == 0) {
      gestern = " AND zeit < '15'";
   }
   qry = fetch("SELECT YEAR(MIN(datum)), MONTH(MIN(datum)), DAY(MIN(datum)) FROM termine", "Fehler beim Speichern des Waschlogs!");
   if (qry.value(0).toInt() == 0) {
	   return true;
   }
   start = QDate(qry.value(0).toInt(), qry.value(1).toInt(), qry.value(2).toInt());

   qry = fetch("SELECT YEAR(DATE_SUB(CURDATE(), INTERVAL 2 DAY)), MONTH(DATE_SUB(CURDATE(), INTERVAL 2 DAY)), DAY(DATE_SUB(CURDATE(), INTERVAL 2 DAY))","Fehler beim Speichern des Waschlogs!");
   ende = QDate(qry.value(0).toInt(), qry.value(1).toInt(), qry.value(2).toInt());

   //Behandlung alte Termine
   while (start <= ende) {
      for (int i = 1; i <= anzahl; i++) {
            if (!directory.exists(start.toString("yyyy_MM"))) {
               directory.mkdir(start.toString("yyyy_MM"));
            }
            QString anfrage = "SELECT user, zeit, wochentag, bonus FROM termine WHERE maschine = '" + QString::number(i) + "' AND datum = '" + QString::number(start.year()) + "-" + QString::number(start.month()) + "-" + QString::number(start.day()) + "' ORDER BY zeit ASC";
            qry = multiquery(anfrage, "Fehler beim Speichern des Waschlogs!");
            while (qry.next()) {
            	buffer = "";
            	dateiname = "./waschlog/" + start.toString("yyyy_MM") + "/" + start.toString("yyyy_MM_dd") + "_Maschine_" +  QString::number(i) + ".txt";
            	QFile datei(dateiname, this);
            	if (QFile::exists(dateiname)) {
            	} else {
            		buffer += "Zeit \t Nachname \t Name \t angetreten \n";
            	}
            	anfrage = "SELECT nachname, name FROM users WHERE id = '" + qry.value(0).toString() + "'";
            	QSqlQuery q = multiquery(anfrage, "Fehler beim Speichern des Waschlogs!");
            	while (q.next()) {
            		buffer += gibWaschTerminTechnisch(qry.value(1).toInt()) + " \t " + q.value(0).toString() + " \t " + q.value(1).toString() + " \t " + ((qry.value(2).toInt())==8?"j":"n") + " \n";
            	}
            	if (datei.open(QIODevice::Append)) {
            		datei.write(buffer);
            		datei.close();
            		if (stornIfNecessary(qry.value(2).toInt(), qry.value(1).toInt(), qry.value(0).toInt(), QString::number(start.year()) + "-" + QString::number(start.month()) + "-" + QString::number(start.day()), qry.value(2).toBool())) {
            			anfrage = "DELETE FROM termine WHERE maschine = '" + QString::number(i) + "' AND datum = '" + QString::number(start.year()) + "-" + QString::number(start.month()) + "-" + QString::number(start.day()) + "' AND zeit = '" + qry.value(1).toString() + "'";
            			exec(anfrage, "Fehler beim Löschen des Waschlogs!");
            		}
            	} else {
            		gibMeldung("Fehler beim Speichern des Waschlogs! Datei konnte nicht geschrieben werden " + dateiname);
            		return false;
            	}
            }
      }
      start = start.addDays(1);
   }

   ende = ende.addDays(1);
   //gestern, um Spezialfall "erster Termin am Tag" abzufangen (letzter von gestern muss erhalten bleiben)
   for (int i = 1; i <= anzahl; i++) {
	   if (!directory.exists(ende.toString("yyyy_MM"))) {
		   directory.mkdir(ende.toString("yyyy_MM"));
	   }
	   QString anfrage = "SELECT user, zeit, wochentag, bonus FROM termine WHERE maschine = '" + QString::number(i) + "' AND datum = '" + QString::number(ende.year()) + "-" + QString::number(ende.month()) + "-" + QString::number(ende.day()) + "'" + gestern + " ORDER BY zeit ASC";
	   qry = multiquery(anfrage, "Fehler beim Speichern des Waschlogs!" );

	   while (qry.next()) {
		   buffer = "";
		   dateiname = "./waschlog/" + ende.toString("yyyy_MM") + "/" + ende.toString("yyyy_MM_dd") + "_Maschine_" +  QString::number(i) + ".txt";
		   QFile datei(dateiname, this);
		   if (QFile::exists(dateiname)) {
		   } else {
			   buffer += "Zeit \t Nachname \t Name \t angetreten \n";
		   }
		   anfrage = "SELECT nachname, name FROM users WHERE id = '" + qry.value(0).toString() + "'";
		   QSqlQuery q = multiquery(anfrage, "Fehler beim Speichern des Waschlogs!");
		   while (q.next()) {
			   buffer += gibWaschTerminTechnisch(qry.value(1).toInt()) + " \t " + q.value(0).toString() + " \t " + q.value(1).toString() + " \t " + ((qry.value(2).toInt())==8?"j":"n") + " \n";
		   }
		   if (datei.open(QIODevice::Append)) {
			   datei.write(buffer);
			   datei.close();
			   if (stornIfNecessary(qry.value(2).toInt(), qry.value(1).toInt(), qry.value(0).toInt(), QString::number(ende.year()) + "-" + QString::number(ende.month()) + "-" + QString::number(ende.day()), qry.value(3).toBool())) {
				   anfrage = "DELETE FROM termine WHERE maschine = '" + QString::number(i) + "' AND datum = '" + QString::number(ende.year()) + "-" + QString::number(ende.month()) + "-" + QString::number(ende.day()) + "' AND zeit = '" + qry.value(1).toString() + "'" + gestern;
				   exec(anfrage, "Fehler beim Löschen des Waschlogs!");
			   }
		   } else {
			   gibMeldung("Fehler beim Speichern des Waschlogs! Datei konnte nicht geschrieben werden " + dateiname);
			   return false;
		   }
	   }
   }
   return true;
}

bool TerminVerwaltung::stornIfNecessary(int wochentag, int zeit, int user, QString datum, bool bonus) {
   double preis;
   double bestand;
   if (wochentag == 8)  {
      return true;
   }
   if (getPreis(wochentag, zeit, &preis)) {
	   if (getBestand(user, &bestand)) {

		   double bonusbestand = 0;
		   double neubestand = preis+bestand;

		   QString anfrage2 = "SELECT bonus FROM finanzlog WHERE user = '" + QString::number(user) + "' ORDER BY datum DESC";
		   QSqlQuery qry = fetch(anfrage2, "Fehler beim Holen des Bonus!");
		   (bonusbestand) = qry.value(0).toDouble();
		   if(bonus)
		   {
			   neubestand -= (preis);
			   bonusbestand += (preis);
		   }
		   QString anfrage = "INSERT INTO finanzlog VALUES('" + QString::number(user) + "', '" + QString::number(neubestand) + "', '" + QString::number(preis) +
				   "', 'Auto-Storno Termin am " + datum + " um " + gibWaschTermin(zeit) + " (Termin nicht wahrgenommen)' , NOW(), " + QString::number(bonusbestand) + ")";
		   exec(anfrage, "Fehler beim Stornieren!");
      } else return false;
   } else return false;
   sleep(1);
   return true;
}

bool TerminVerwaltung::getBestand(int user, double* bestand) {
      QString anfrage = "SELECT bestand FROM finanzlog WHERE user = '" + QString::number(user) + "' ORDER BY datum DESC";
      QSqlQuery qry = fetch(anfrage, "Fehler beim Holen des Bestandes!");
      (*bestand) = qry.value(0).toDouble();
      return true;
}

bool TerminVerwaltung::getPreis(int tag, int zeit, double* preis) {
	QString anfrage = "SELECT preis FROM preise WHERE tag = '" + QString::number(tag) + "' AND zeit = '"
			+ QString::number(zeit) + "'";
	QSqlQuery qry = fetch(anfrage, "Fehler beim Holen des Preises!");
	(*preis) = qry.value(0).toDouble();
	return true;
}

TerminVerwaltung::~TerminVerwaltung() {
   db.close();
}


// Refactoring

QSqlQuery TerminVerwaltung::multiquery(QString anfrage, const char* error) {
	if (!verbindeDB())
		throw QString("Datenbank nicht verfügbar.");
	QSqlQuery qry(db);
	if (!qry.prepare(anfrage))
		throw QString(error) + QString(" Query korrupt: ") + anfrage;
	if (!qry.exec())
		throw QString(error) + QString(" Query nicht ausgeführt: ") + anfrage;
	return qry;
}

QSqlQuery TerminVerwaltung::fetch(QString anfrage, const char* error) {
	if (!verbindeDB())
		throw QString("Datenbank nicht verfügbar.");
	QSqlQuery qry(db);
	if (!qry.prepare(anfrage))
		throw QString(error) + QString(" Query korrupt: ") + anfrage;
	if (!qry.exec())
		throw QString(error) + QString(" Query nicht ausgeführt: ") + anfrage;
    if (!qry.next())
    	throw QString(error) + QString(" Result leer: ") + anfrage;
	return qry;
}

void TerminVerwaltung::exec(QString anfrage, const char* error) {
	if (!verbindeDB())
		throw QString("Datenbank nicht verfügbar.");
	QSqlQuery qry(db);
	if (!qry.prepare(anfrage))
		throw QString(error) + QString(" Query korrupt: ") + anfrage;
	if (!qry.exec())
		throw QString(error) + QString(" Query nicht ausgeführt: ") + anfrage;
}


