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

my $cgi = new CGI;	# erzeugt ein neues CGI-Objekt (damit formulare bearbeitet und HTML ausgegeben werden kann)
my $skript = "wasch.cgi"; # Dateiname
my $include = "inc/"; #Include-Verzeichnis
my $progName = "WaschZoo - Da wird der Hund in der Pfanne verr&uuml;ckt!"; # Prgrammname
my $godsName = "Christian Ewald"; # Wehe da spielt jemand dran rum ;)

my $dbh;
my $cfg = Config::IniFiles->new( -file => "./inc/config.ini" );
$dbh = DBI->connect($cfg->val("wasch","db"),$cfg->val("wasch","user"),$cfg->val("wasch","pw")) or die $dbh->errstr();
    
sub print_header {  
     print "Content-type: text/html\n\n";  
     open (START, "/var/www/www.tvk.rwth-aachen.de/start.inc");  
          my @file = <START>;  
          print @file;  
     close (START);
     print "<style type=\"text/css\">";
		 print "a.red {color: #FF0000}";
		 print "a.yellow {color: #FFFF00}";
		 print "a.green {color:#008f00}";
		 print "a.green:hover {color:#ff9900}";
		 print "</style>";
}

# Fuß jeder Seite, Gegenstück zu print_header
sub print_footer {  
	print "<br><br><br><br><br><table width=\"100%\" frame=\"above\" cellpadding=\"5\">";
	print "<tr><td align=\"left\"> $progName $version</td><td align=\"right\">by $godsName </td></tr></table>";
     open (ENDE, "/var/www/www.tvk.rwth-aachen.de/ende.inc");  
          my @file = <ENDE>;  
          print @file;  
     close (ENDE);
  $dbh->disconnect;
}

sub printFehler {
	my $fehler = shift;
	print "$fehler<br>";
}

sub show_doku {
	my $sprache = shift;
	if ($sprache ne "ger" && $sprache ne "eng") {
		printFehler("Keine g&uuml;ltige Sprache gew&auml;hlt!");
		return;
	}
	my $listtype = "ul";
	my $sth = $dbh->prepare("SELECT paragraph, abschnitt, satz, titel FROM doku_$sprache ORDER BY paragraph ASC, abschnitt ASC, satz ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	my $paragraph = 0;
	my $abschnitt = 0;
	my $satz = 0;
	$sth->execute();
	my @row;
	my @all;
	my $back = "zur&uuml;ck";
	print "<a name=\"anfang\"></a><$listtype>";
	while(@row = $sth->fetchrow_array()) {
		if($paragraph < $row[0]) {
			#PRINT PARAGRAPH
			if($paragraph != 0){
				if ($abschnitt != 0) {				
					print "</$listtype></li>";
				}
				print "<br></$listtype></li>";
			}
			print "<li><b><a href=\"#$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			print "<$listtype>";
			$paragraph++;
			$abschnitt = 0;
			$satz = 0;
		} elsif ($abschnitt < $row[1]) {
			#PRINT ABSCHNITT
			if($abschnitt != 0){
				print "</$listtype></li>";
			}
			print "<li><b><a href=\"#$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			print "<$listtype>";
			$abschnitt++;
			$satz = 0;
		} elsif($satz < $row[2]) {
			#PRINT SATZ
			print "<li><b><a href=\"#$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			print "</li>";
			$satz++;
		}
	}
	if($paragraph != 0){
		print "</$listtype></li>";
	}
	if($abschnitt != 0){
		print "</$listtype></li>";
	}
	print "</$listtype><br><br>";
	
	$sth = $dbh->prepare("SELECT paragraph, abschnitt, satz, titel, inhalt FROM doku_$sprache ORDER BY paragraph ASC, abschnitt ASC, satz ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$paragraph = 0;
	$abschnitt = 0;
	$satz = 0;
	$sth->execute();
	print "<$listtype>";
	while (@row = $sth->fetchrow_array()) {
		if($paragraph < $row[0]) {
			#PRINT PARAGRAPH
			if($paragraph != 0){
				if ($abschnitt != 0) {				
					print "</$listtype></li>";
				}
				print "<br><br></$listtype></li>";
			}
			print "<li><b><a name=\"$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			if ($row[4] ne "") {
				print "<br>";
			}
			print "$row[4] <a href=\"#anfang\">$back</a><br><br><br><$listtype>";
			$paragraph++;
			$abschnitt = 0;
			$satz = 0;
		} elsif ($abschnitt < $row[1]) {
			#PRINT ABSCHNITT
			if($abschnitt != 0){
				print "<br></$listtype></li>";
			}
			print "<li><b><a name=\"$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			if ($row[4] ne "") {
				print "<br>";
			}
			print "$row[4] <a href=\"#anfang\">$back</a><br><br><$listtype>";
			$abschnitt++;
			$satz = 0;
		} elsif($satz < $row[2]) {
			#PRINT SATZ
			print "<li><b><a name=\"$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			if ($row[4] ne "") {
				print "<br>";
			}
			print "$row[4] <a href=\"#anfang\">$back</a><br><br></li>";
			$satz++;
		}
	}
	if($paragraph != 0){
		print "</$listtype></li>";
	}
	if($abschnitt != 0){
		print "</$listtype></li>";
	}
	print "</$listtype>";
}

# gibt die Kapitelzahl "schön" aus
sub print_chapter {
	my $paragraph = shift;
	my $abschnitt = shift;
	my $satz = shift;
	my $erg = $paragraph.".";
	if ($abschnitt != 0) {
		$erg = $erg.$abschnitt.".";
		if ($satz != 0) {
			$erg = $erg.$satz.".";
		}
	}
	return ($erg);
}

print_header();
my $language = $cgi->url_param('lang');
show_doku($language);
print_footer();
