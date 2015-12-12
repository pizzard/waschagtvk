#include <QApplication>
#include <QWidget>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidget>
#include <QGroupBox>
#include <QMessageBox>

#include <iostream>
#include "DigitalUhr.h"
#include "TerminVerwaltung.h"
#include "WashingProgram.h"

WashingProgram::WashingProgram(QWidget *parent) : QWidget(parent){
	setFixedSize(1280, 1024);
	setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint);


	
	uhr = new DigitalUhr(this);
	termin = new TerminVerwaltung(this, this);

	layout2 = new QVBoxLayout;
	layout2->addWidget(uhr);
	layout2->addWidget(termin);
	setLayout(layout2);
}

WashingProgram::~WashingProgram() {
	delete uhr;
	delete termin;
	delete layout2;
}

void WashingProgram::close() {
   qApp->quit();
}

