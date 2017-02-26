#ifndef TERMIN_INCLUDE_
#define TERMIN_INCLUDE_

#include <iostream>
#include <QtGui>
#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidget>
#include <QGroupBox>
#include <QMessageBox>
#include <QFont>
#include <QtSql>
#include <QSqlError>
#include <QSqlDriver>
#include <QInputDialog>
#include <QSqlDatabase>
#include <QLabel>
#include <QProgressBar>
#include <QPalette>
#include <QtNetwork>
#include <QByteArray>
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

class WashingProgram;

class TerminVerwaltung : public QWidget{
  Q_OBJECT
  
public:
	int anzahl;		//ANZAHL MASCHINEN -> DB
	int antritt;		//ANTRITTSZEIT IN MIN -> DB
	int relais;		//RELAISZEIT IN MIN -> DB
	int vorhaltezeit;	//VORHALTEZEIT KONTODATEN IN MONATEN -> DB
	int WAGvorhaltezeit;	//VORHALTEZEIT WAG-KONTODATEN IN MONATEN -> DB
	int aktZeit;		//aktuelle Zeit
	bool* status;		//speichert den Status der Maschinen
	bool* aktStatus;	//speichert Zustand des Relais
	int* maschinenNr;	//speichert, welche Maschine welches Relais hat

	QTime* countdown;	//innere Uhr ;)
	
	TerminVerwaltung(QObject* parent = 0);
	TerminVerwaltung(WashingProgram* mama = 0);
	~TerminVerwaltung();

	WashingProgram* mutter;
        
	QSqlDatabase db;
	
	QProgressBar* balken;
	QLabel*** tabelle;
	QLabel* message;
	QLabel* balkenText;
        
        QString** sagEs;
	
	QTimer* timer;
	QTimer* timer2;
	
	QGroupBox ** box;
	QVBoxLayout** layout;
	QGridLayout* layout_grid;
	QGroupBox* messageBox;
	QVBoxLayout* messageLayout;
	
	QPushButton* control;

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
