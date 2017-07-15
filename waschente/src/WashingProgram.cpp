//#include "DigitalUhr.h"
//#include "TerminVerwaltung.h"
#include "WashingProgram.h"

WashingProgram::WashingProgram(QWidget *parent):
	QWidget(parent)
{
	ui.setupUi(this);
	setMinimumSize(1280, 1024);
	setWindowState(Qt::WindowFullScreen);
	setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint);
}
