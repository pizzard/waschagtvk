#ifndef HELP_INCLUDE_
#define HELP_INCLUDE_

#include <QString>
#include <QTime>

QString gibWaschTermin(int zeit);
QString gibWaschTerminTechnisch(int zeit);
QTime gibWaschZeit(int zeit);
int differenz(const QTime& first, const QTime& sec);
int getNow();
int getNowDB(int h, int min, int sec);

#endif

