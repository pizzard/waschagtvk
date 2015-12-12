#ifndef WASCH_INCLUDE_
#define WASCH_INCLUDE_

#include <QWidget>
#include <QLabel>
#include <QVBoxLayout>

class QPushButton;
class DigitalUhr;
class TerminVerwaltung;

class WashingProgram : public QWidget{
  //Q_OBJECT
  
public:
	WashingProgram(QWidget *parent = 0);
	~WashingProgram();

	DigitalUhr* uhr;
	TerminVerwaltung* termin;
	
	QVBoxLayout* layout2;

	//void showMessage(QString message);
	
    void close();
        

};

#endif
