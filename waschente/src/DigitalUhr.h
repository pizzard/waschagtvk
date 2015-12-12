#ifndef DIGITALUHR_INCLUDE_
#define DIGITALUHR_INCLUDE_

#include <QtGui>
#include <QLCDNumber>

class DigitalUhr : public QLCDNumber {
	Q_OBJECT

public:
	DigitalUhr(QWidget *parent = 0);

private slots:
	void showTime();
};

#endif



