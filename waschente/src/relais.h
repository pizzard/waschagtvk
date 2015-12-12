#ifndef RELAIS_INCLUDE_
#define RELAIS_INCLUDE_

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <termios.h>
#include <string.h>
#include <math.h>
#include <sys/fcntl.h>
#include <iostream>

void initserie (void);
unsigned char checksum(char cmd[]);
void SendCommand(char cmd[]);
void openPort(int port, bool auf);

#endif
