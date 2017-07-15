#ifndef WASCH_INCLUDE_
#define WASCH_INCLUDE_

#include "ui_ente.h"

class WashingProgram : public QWidget{
	Q_OBJECT
public:
	WashingProgram(QWidget *parent = 0);
private:
	Ui::enteWidget ui;
};

#endif
