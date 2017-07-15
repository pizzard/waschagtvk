#include "DigitalUhr.h"

DigitalUhr::DigitalUhr(QWidget *parent)
   : QLCDNumber(parent)
{
	setSegmentStyle(Filled);
	setDigitCount(8);
   
   QTimer* timer = new QTimer(this);
   connect(timer, SIGNAL(timeout()), this, SLOT(showTime()));
   timer->start(1000);

   showTime();
}

void DigitalUhr::showTime()
{
    QTime time = QTime::currentTime();
    QString text = time.toString("hh:mm:ss");
    if ((time.second() % 2) == 0)
        text.replace(':', ' ');

   display(text);
}
