#include "relais.h"

#define BAUDRATE B2400

struct 	termios oldtio, newtio ;
int     	k8056_port ;
char		k8056_device[16] = "/dev/ttyS0" ;	/*  This is the default device, can be reset on command line. */
unsigned char 	k8056_instruction = 'E';
unsigned char 	k8056_addr = 1 ;
unsigned char	k8056_relay_address = '0'  ;
int		k8056_trame_number = 100 ;		/*  Increase value with a long serial cable or in wireless operation. */
char 		cmd[6] ;

/*------------------------------------------------------------------------------*/
/*  Open serial port 				       				*/
/*------------------------------------------------------------------------------*/
void initserie (void) {
	k8056_port = open(k8056_device, O_RDWR | O_NOCTTY );
	if (k8056_port < 0)
 	{
 		fprintf(stderr, "Error opening device %s !\n", k8056_device) ;
		exit(-1);
	}
 	tcgetattr(k8056_port,&oldtio); 		/* save current port settings */

 	newtio.c_cflag = BAUDRATE | CS8 | CLOCAL | CREAD;
 	newtio.c_oflag = 0;
 	tcflush(k8056_port, TCOFLUSH);		/* Flushes written but not transmitted. */
 	tcsetattr(k8056_port, TCSANOW, &newtio);
}


/*---------------------------------------------------------------------------------*/
/* Checksum	Checkum (2 complement of the sum of the 4 previous byte + 1)       */
/*---------------------------------------------------------------------------------*/
unsigned char checksum(char cmd[]) {
        unsigned char checksum ;
        /*  Ex. VB: checksum = ( 255 - ( ( ( (a+b+c+d / 256 ) - Int( (13 + cmd[1] + cmd[2] + cmd[3]) / 256 ) ) * 256 ) ) + 1 ;	*/
        /* ( 255 - ((a+b+c+d) modulo 256) ) + 1		Calcul de checkum (complement � 2 de la somme de 4 octets + 1).  	*/
	checksum = ~((13 + cmd[1] + cmd[2] + cmd[3]) & 0xFF) + 1 ;
        return checksum ;
}


/*--------------------------------------------------------------------------------*/
/* SendCommand	Send command to k8056 card      				  */
/*--------------------------------------------------------------------------------*/
void SendCommand(char cmd[]) {
	int	i ;
	tcflush(k8056_port, TCOFLUSH) ;		/* Flushes written but not transmitted. */
	for (i=0 ; i < k8056_trame_number ; i++)
	{
		write(k8056_port, cmd, 5) ;
		usleep(5000) ;
	}
}

/*--------------------------------------------------------------------------------*/
/* openPort	�ffnet und schlie�t Port port					  */
/*--------------------------------------------------------------------------------*/
void openPort(int port, bool auf) {
        /* Open serial port */
	if (port > 0 && port < 10) {
		initserie() ;
		
		cmd[0] = 13 ;						/* 13					*/
		cmd[1] = k8056_addr ;					/* Adresse				*/
		cmd[2] = auf?'S':'C';					/* Instruction				*/
		cmd[3] = (char) (port+48);					/* # relais, address or status		*/
		cmd[4] = checksum(cmd) ;				/* Checksum				*/
		
		//std::cout << cmd[2] << cmd[3] << std::endl;
		SendCommand(cmd) ;
		
		/* Close serial port */
		tcsetattr(k8056_port, TCSANOW, &oldtio);		/* Backup old port settings   */
		close(k8056_port);
	} else {
		std::cerr << "Port " << port << " gibts nicht!" << std::endl;
	}
	usleep(1000000);
}

