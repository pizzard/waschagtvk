#include <QApplication>
#include <iostream>
#include "WashingProgram.h"

int main(int argc, char *argv[]){
	QApplication app(argc, argv); // parameter weglassen
	WashingProgram *waschEnte = new WashingProgram();
	waschEnte->showMaximized();
	return app.exec();
return 0;
}
 
 
