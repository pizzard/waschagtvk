#ifndef TERMIN_INCLUDE_
#define TERMIN_INCLUDE_

#include <vector>
#include <array>
#include <memory>
#include <QWidget>
#include <QPushButton>
#include <QVBoxLayout>
#include <QGroupBox>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QLabel>
#include <QProgressBar>
#include <QTimer>
#include "Hilfsfunktionen.h"

// Server-Adresse DB
#define SERVER "137.226.142.9"
// Passwort für die DB
#define PWORT "Ariel42Rein:"
// Username der DB
#define USER "waschag"
// WaschAG Status Identifier
#define WASCHAG_STATUS 5
// Inaktiv WaschAG Status Identifier
#define INACTIVE_WASCHAG_STATUS 3

class TerminVerwaltung : public QWidget{
	Q_OBJECT
  
public:
	TerminVerwaltung(QWidget* parent = 0);
	~TerminVerwaltung();
private:
	int anzahl;		//ANZAHL MASCHINEN -> DB
	int antritt;		//ANTRITTSZEIT IN MIN -> DB
	int relais;		//RELAISZEIT IN MIN -> DB
	int vorhaltezeit;	//VORHALTEZEIT KONTODATEN IN MONATEN -> DB
	int WAGvorhaltezeit;	//VORHALTEZEIT WAG-KONTODATEN IN MONATEN -> DB
	int aktZeit;		//aktuelle Zeit
	std::vector<bool> status;		//speichert den Status der Maschinen
	std::vector<bool> aktStatus;	//speichert Zustand des Relais
	static const std::array<const int,3> maschinenNr;	//speichert, welche Maschine welches Relais hat

	QTime countdown;	//innere Uhr ;)

	QSqlDatabase db;
	
	QProgressBar balken;
	std::vector<std::array<std::unique_ptr<QLabel>,3>> tabelle;
	QLabel message;
	QLabel balkenText;

	std::array<QString,5> sagEs;

	QTimer timer;
	QTimer timer2;

	std::vector<std::unique_ptr<QGroupBox>> box;
	std::vector<std::unique_ptr<QVBoxLayout>> layout;
	QGridLayout layout_grid;
	QGroupBox messageBox;
	QVBoxLayout messageLayout;

	QPushButton control;

public slots:
	void update();
	void iWannaWash();
	void checkeMaschinen();
	void shortcutWarning();
	

private:
	bool verbindeDB();
	void gibMeldung(QString nachricht);
	void getConfig();
	void getMaschinen();
	void stoppeMaschine(int id);
	bool starteMaschine(int id);
	void printTabelle();
	bool speicherAlleFinanzen();
	bool speicherTermine();
	bool speicherFirewall();
	bool speicherWaschAgFinanzen();
	bool stornIfNecessary(int wochentag, int zeit, int user, QString datum, bool bonus);
	bool getPreis(int tag, int zeit, double* preis);
	bool getBestand(int user, double* bestand);

	// Refactoring
	void exec(const char * anfrage, const char * error) { return exec(QString(anfrage), error); }
	void exec(QString anfrage, const char* error);

	QSqlQuery multiquery(const char * anfrage, const char * error) { return multiquery(QString(anfrage), error); }
	QSqlQuery multiquery(QString anfrage, const char* error);

	QSqlQuery fetch(const char * anfrage, const char * error) { return fetch(QString(anfrage), error); }
	QSqlQuery fetch(QString anfrage, const char* error);

};

#endif
