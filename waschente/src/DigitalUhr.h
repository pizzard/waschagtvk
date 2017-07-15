#ifndef DIGITALUHR_INCLUDE_
#define DIGITALUHR_INCLUDE_

#include <QtGui>
#include <QLCDNumber>

/**
 * shows current time, mostly based on
 * http://doc.qt.io/qt-5/qtwidgets-widgets-digitalclock-digitalclock-h.html
 */
class DigitalUhr : public QLCDNumber {
	Q_OBJECT

public:
	DigitalUhr(QWidget *parent = 0);

private slots:
	void showTime();
};

#endif
