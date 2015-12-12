#include "Hilfsfunktionen.h"
#include <QTime>
#include <iostream>

QString gibWaschTermin(int zeit) {
	QString temp;
	if ( ((zeit * 15) % 10) == 0 ) {
		temp = QString::number((int)(zeit * 1.5)) + ":00" + " - " + QString::number((int)((zeit+1)*1.5)) + ":" + QString::number((((zeit+1)*15)%10)*6);
	} else {
		temp = QString::number((int)(zeit * 1.5))+ ":" + QString::number(((zeit*15)%10)*6) + " - " + QString::number((int)((zeit+1)*1.5)) + ":00";
	}
	return temp;
}

QString gibWaschTerminTechnisch(int zeit) {
	if ((zeit*1.5-((zeit*15)%10)/10)<10) {
		return (QString::number(0) + gibWaschTermin(zeit));
	} else {
		return gibWaschTermin(zeit);
	}
}

int getNow() {
	QTime zeit = QTime::currentTime();
	int offset = 0;
	if (zeit.minute() >= 30) {
		offset = 1;
	}
	return ((zeit.hour() * 2 + offset)/3);
}

int getNowDB(int h, int min, int sec) {
	QTime zeit = QTime(h, min, sec);
	int offset = 0;
	if (zeit.minute() >= 30) {
		offset = 1;
	}
	return ((zeit.hour() * 2 + offset)/3);
}

QTime gibWaschZeit(int zeit) {
	QTime temp;
	if ( ((zeit * 15) % 10) == 0 ) {
		temp = QTime(((int)(zeit * 1.5)),0);
	} else {
		temp = QTime(((int)(zeit * 1.5)),(int)(((zeit*15)%10)*6));
	}
	return temp;
}

int differenz(const QTime& first, const QTime& sec) {
	int secs = 0;
	int hours = 0;
	int minutes = 0;
	secs = first.second() - sec.second();
	if (secs < 0) {
		minutes -= -1;
		secs += 60;
	}
	minutes += first.minute() - sec.minute();
	if (minutes < 0) {
		hours -= -1;
		minutes += 60;
	}
	hours += first.hour() - sec.hour();
	if (hours < 0) {
		hours += 24;
	}
	return ((hours*60+minutes)*60+secs);
}

