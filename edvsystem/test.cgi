#!/usr/bin/perl -w
#use strict;
use CGI;	# CGI-Modul
use CGI::Carp qw(fatalsToBrowser);
use DBD::mysql;
use Apache::DBI;
use Encode;
use CGI qw(:standard);
use POSIX qw(ceil floor);
use Config::IniFiles;

     print "Content-type: text/html\n\n";  
     open (START, "/var/www/localhost/htdocs/start.inc");  
          my @file = <START>;  
          print @file;  
     close (START);
     print "<style type=\"text/css\">";
		 print "a.red {color: #FF0000}";
		 print "a.yellow {color: #FFFF00}";
		 print "a.green {color:#008f00}";
		 print "a.green:hover {color:#ff9900}";
		 print "</style>";
		
	my $pw = "AareVGSTRFweärde";
	my $pwl = length($pw);
	my $zeichenklassen = 0; 
if($pwl<8) {
		print "Das Passwort ist nur $pwl Zeichen lang, verwende mindestens 8!<br>";
	}
	if($pw =~ /\ /){
		$zeichenklassen+=1;
	}
	if($pw =~ /[0-9]/){
		$zeichenklassen+=1;
	}
	if($pw =~ /[a-z]/){
		$zeichenklassen+=1;
	}
	if($pw =~ /[A-Z]/){
		$zeichenklassen+=1;
	}
	if($pw =~ /[^a-z,A-Z,0-9,\ ]/){
		$zeichenklassen+=1;
	}
	if($zeichenklassen >= 3) {
		print $zeichenklassen;
	} else {
		print "Dein Passwort ist zu unsicher, du musst mindestens drei verschiedene Arten von Zeichenklassen verwenden: Kleinbuchstaben, Gro&szlig;buchstaben, Sonderzeichen, Ziffern oder Leerzeichen.";
		print $zeichenklassen;	
	}

	print "<br><br><br><br><br><table width=\"100%\" frame=\"above\" cellpadding=\"5\">";
	print "<tr><td align=\"left\"> $progName $version</td><td align=\"right\">by $godsName </td></tr></table>";
     open (ENDE, "/var/www/localhost/htdocs/ende.inc");  
          my @file = <ENDE>;  
          print @file;  
     close (ENDE);
