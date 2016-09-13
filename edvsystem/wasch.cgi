#!/usr/bin/perl
#use strict;
use CGI;	# CGI-Modul
use CGI::Carp qw(fatalsToBrowser);
use DBD::mysql;
use Apache::DBI;
use Encode;
use CGI qw(:standard);
use POSIX qw(ceil floor);
use Config::IniFiles;
use Digest::SHA qw(sha1_hex);
#use Net::SFTP;

our $cgi = new CGI;	# erzeugt ein neues CGI-Objekt (damit formulare bearbeitet und HTML ausgegeben werden kann)
our $skript = "wasch.cgi"; # Dateiname
our $include = "inc/"; #Include-Verzeichnis
our $progName = "WaschZoo"; # Prgrammname
our $adminsName = "Waschross"; # Login vom Superadmin
our $god = 9; # Status: Superuser
our $godsName = "Christian Ewald"; # Wehe da spielt jemand dran rum ;)
our $version = "5.B"; # Versionsnummer
our $admin = 7; # Status: Kassenwart
our $waschag = 5; # Status: WaschAG-Mitglied
our $exWaschag = 3; # Status: ehemaliges WaschAG-Mitglied
our $user = 1; # Status: User
our $wartung = 0; # 1 sperrt das gesamte System fÃ¼r alle User auÃŸer WaschAG + Admin
our $godWartung = 0; # 1 sperrt das gesamte System für alle User außer Admin
our $superuser = "137.226.143.79";
our $tvkurt = "137.226.143.4"; #TvKurt Adresse
our $maxBetrag = 100; #Betrag, den ein User maximal einzahlen darf
our $stornTime;
our $antrittTime;
our $relaisTime;
our $minBetrag;
our $termPerDay;
our $termPerMonth;
our $freiGeld;
our $anzahlMaschinen;
our $error = ''; # temporÃ¤re Variable für diverse Fehlermeldungen
our $terminhash = ''; # ist der has des users für den ical-export

# Öffnen der Datenbank
#		my $X;
#    open( DBINI, "< ".$include."config.ini" );
#    while ( chomp( $X = <DBINI> ) ) { push( @DBINI, $X ); }
#    close(DBINI);
#    my $dbh = DBI->connect(@DBINI)
#      or die "Can't connect to Database";
#    undef(@DBINI);
#    undef($X);
my $dbh;
my $cfg = Config::IniFiles->new( -file => "./inc/config.ini" );
#$dbh = DBI->connect($cfg->val("wasch","db"),$cfg->val("wasch","user"),$cfg->val("wasch","pw")) or die $dbh->errstr();
$dbh = DBI->connect($cfg->val("wasch","db"),$cfg->val("wasch","user")) or die $DBI::errstr;


# Start HTML
if ($cgi->url_param('aktion') eq 'create_user') {
		if (kopf("create_user", $waschag) == 1) {
			create_user();
		}
} elsif ($cgi->url_param('aktion') eq 'login') {
	firstLogin();
} elsif ($cgi->url_param('aktion') eq 'index') {
	if (kopf("index", $user) == 1) {
		hauptMenue();
	}
	# User Management
} elsif ($cgi->url_param('aktion') eq 'new_user') {
	if (kopf("new_user", $waschag) == 1) {
		gibNewForm();
	}
} elsif ($cgi->url_param('aktion') eq 'edit_user') {
	if (kopf("edit_user", $waschag) == 1) {
		start_edit(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'show_user_finance') {
	if (kopf("show_user_finance", $waschag) == 1) {
		user_finance(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'change_pw') {
	if (kopf("change_pw", $user) == 1) {
		changePW() ;
	}
} elsif ($cgi->url_param('aktion') eq 'do_change_pw') {
	if (kopf("change_pw", $user) == 1) {
		doChange();
	}
} elsif ($cgi->url_param('aktion') eq 'delete_user') {
	if (kopf("delete_user", $waschag) == 1) {
		delete_user(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'mach_tot') {
	if (kopf("delete_user", $waschag) == 1) {
		deleteUserEndgueltig(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'do_edit') {
	if (kopf("do_edit", $waschag) == 1) {
		do_edit();
	}
} elsif ($cgi->url_param('aktion') eq 'user_management') {
	if (kopf("user_management", $waschag) == 1) {
		userVerwaltung();
	}
} elsif ($cgi->url_param('aktion') eq 'manage_money') {
	if (kopf("manage_money", $waschag) == 1) {
		manage_money();
	}
} elsif ($cgi->url_param('aktion') eq 'admin_transaktion') {
	if (kopf("manage_money", $waschag) == 1) {
		admin_transaktion();
	}
} elsif ($cgi->url_param('aktion') eq 'god_transaktion') {
	if (kopf("manage_admin_money", $admin) == 1) {
		god_transaktion();
	}
} elsif ($cgi->url_param('aktion') eq 'self_transaktion') {
	if (kopf("manage_admin_money", $admin) == 1) {
		self_transaktion();
	}
} elsif ($cgi->url_param('aktion') eq 'kontoauszug') {
	if (kopf("kontoauszug", $user) == 1) {
		kontoAuszug();
	}
} elsif ($cgi->url_param('aktion') eq 'ueberweisungsformular') {
	if (kopf("ueberweisung", $user) == 1) {
		ueberweisungsFormular();
	}
} elsif ($cgi->url_param('aktion') eq 'ueberweisung') {
	if (kopf("ueberweisung", $user) == 1) {
		ueberweisung();
	}
} elsif ($cgi->url_param('aktion') eq 'storno') {
	if (kopf("storno", $user) == 1) {
		storno();
	}
	# Konfiguration
} elsif ($cgi->url_param('aktion') eq 'waschmaschinen') {
	if (kopf("waschmaschinen", $waschag) == 1) {
		maschinenVerwaltung();
	}
} elsif ($cgi->url_param('aktion') eq 'set_waschmaschinen') {
	if (kopf("waschmaschinen", $waschag) == 1) {
		maschineSetConfig(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'set_config') {
	if (kopf("waschmaschinen", $waschag) == 1) {
		set_config();
	}
} elsif ($cgi->url_param('aktion') eq 'preisliste') {
	if (kopf("set_preis", $god) == 1) {
		preisListe();
	}
} elsif ($cgi->url_param('aktion') eq 'set_preis') {
	if (kopf("set_preis", $god) == 1) {
		set_preis();
	}
} elsif ($cgi->url_param('aktion') eq 'set_einheits_preis') {
	if (kopf("set_preis", $god) == 1) {
		set_einheits_preis();
	}
	# Termine
} elsif ($cgi->url_param('aktion') eq 'look_termine') {
	if (kopf("look_termine", $user) == 1) {
		look_termine();
	}
} elsif ($cgi->url_param('aktion') eq 'buchen') {
	if (kopf("look_termine", $user) == 1) {
		bucheTermin();
	}
} elsif ($cgi->url_param('aktion') eq 'notify_management') {
	if (kopf("notify_management", $waschag) == 1) {
		notifyVerwaltung();
	}
} elsif ($cgi->url_param('aktion') eq 'show_doku') {
	if (kopf("show_doku", $user) == 1) {
		show_doku(makeclean($cgi->url_param('lang')));
	}
} elsif ($cgi->url_param('aktion') eq 'edit_doku') {
	if (kopf("edit_doku", $god) == 1) {
		edit_doku(makeclean($cgi->url_param('lang')));
	}
} elsif ($cgi->url_param('aktion') eq 'new_doku') {
	if (kopf("edit_doku", $god) == 1) {
		new_doku(makeclean($cgi->url_param('lang')),makeclean($cgi->url_param('p')),makeclean($cgi->url_param('a')),makeclean($cgi->url_param('s')));
	}
} elsif ($cgi->url_param('aktion') eq 'write_doku') {
	if (kopf("edit_doku", $god) == 1) {
		write_doku(makeclean($cgi->url_param('lang')),makeclean($cgi->url_param('p')),makeclean($cgi->url_param('a')),makeclean($cgi->url_param('s')));
	}
} elsif ($cgi->url_param('aktion') eq 'edit_this_doku') {
	if (kopf("edit_doku", $god) == 1) {
		edit_this_doku(makeclean($cgi->url_param('lang')),makeclean($cgi->url_param('p')),makeclean($cgi->url_param('a')),makeclean($cgi->url_param('s')));
	}
} elsif ($cgi->url_param('aktion') eq 'del_doku') {
	if (kopf("edit_doku", $god) == 1) {
		del_doku(makeclean($cgi->url_param('sure')),makeclean($cgi->url_param('lang')),makeclean($cgi->url_param('p')),makeclean($cgi->url_param('a')),makeclean($cgi->url_param('s')));
	}
} elsif ($cgi->url_param('aktion') eq 'stats') {
	if (kopf("stats", $waschag) == 1) {
		statistik();
	}
} elsif ($cgi->url_param('aktion') eq 'look_banned_poopies') {
	if (kopf("stats", $waschag) == 1) {
		look_banned_people();
	}
} elsif ($cgi->url_param('aktion') eq 'look_old_data') {
	if (kopf("data", $waschag) == 1) {
		look_old_data($cgi->url_param('dir'), $cgi->url_param('file'));
	}
} elsif ($cgi->url_param('aktion') eq 'create_shout') {
	if (kopf("shout", $waschag) == 1) {
		create_shout();
	}
} elsif ($cgi->url_param('aktion') eq 'send_shout') {
	if (kopf("shout", $waschag) == 1) {
		massenNachricht();
	}
} else {
	print_header();
	Titel("Login");
	logon();
}

print_footer();		# und der html-ausgabe-teil beendet.


# ----- HIER BEGINNT DER ABSCHNITT DER HILFSFUNKTIONEN ENTHÄLT -----

# Berechnet, die Distanz zwischen jetzt und Anfang Waschtermin
sub wieLangNoch {
	my $zeit = substr(gibWaschTerminTechnisch(shift),0,5).":00";
	my $datum = shift;
	my $zeitstring = $datum." ".$zeit;
	my $sth = $dbh->prepare("SELECT (UNIX_TIMESTAMP('$zeitstring')-UNIX_TIMESTAMP(NOW()))/60") || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	return ($row[0]);
}

# entfernt böse Zeichen ausm String ;)
sub makeclean {
	my $text = shift;
	$text =~ s/"//g;
	$text =~ s/'//g;
	$text =~ s/;//g;
	return ($text);
}

# Berechnet, wie lange der Termin schon läuft
sub wieLangSchon {
	my $waschzeit = shift;
	my $zeit;
	if ($waschzeit < 15) {
		$zeit = substr(gibWaschTerminTechnisch($waschzeit),0,5).":00";
	} else {
		$zeit = "00:00:00";
	}
	my $datum = shift;
	my $zeitstring = $datum." ".$zeit;
	my $sth;
	if ($waschzeit < 15) {
		$sth = $dbh->prepare("SELECT (UNIX_TIMESTAMP(NOW())-UNIX_TIMESTAMP('$zeitstring'))/60") || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	} else {
		$sth = $dbh->prepare("SELECT (UNIX_TIMESTAMP(NOW())-UNIX_TIMESTAMP(DATE_ADD('$zeitstring', INTERVAL 1 DAY)))/60") || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	}
	$sth->execute();
	my @row = $sth->fetchrow_array();
	return ($row[0]);
}

# holt die Konfiguration aus der DB
sub getConfig {
	my $sth = $dbh->prepare("SELECT * FROM config")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	while (my @row = $sth->fetchrow_array()) {
		if($row[0] eq "Stornierzeit (in Min)") { $stornTime = $row[1]; }
		elsif($row[0] eq "Antrittszeit (in Min)") { $antrittTime = $row[1]; }
		elsif($row[0] eq "Relaiszeit (in Min)") { $relaisTime = $row[1]; }
		elsif($row[0] eq "minimaler Einzahlbetrag (in Euro)") { $minBetrag = $row[1]; }
		elsif($row[0] eq "Termine pro Monat") { $termPerMonth = $row[1]; }
		elsif($row[0] eq "Freigeld fuer WaschAG") { $freiGeld = $row[1]; }
	}
	$sth = $dbh->prepare("SELECT COUNT(*) FROM waschmaschinen WHERE status = '1'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	$termPerDay = $row[0];
	$sth = $dbh->prepare("SELECT COUNT(*) FROM waschmaschinen")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	@row = $sth->fetchrow_array();
	$anzahlMaschinen = $row[0];
}

# prüft ein Passwort auf Sicherheit
# param pw
sub checkPW {
	my $pw = shift;
	my $pwl = length($pw);
	my $zeichenklassen = 0;

	if($pwl<8) {
		printFehler("Das Passwort ist nur $pwl Zeichen lang, verwende mindestens 8!<br>");
		return (0);
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
		return (1);
	} else {
		printFehler("Dein Passwort ist zu unsicher, du musst mindestens drei verschiedene Arten von Zeichenklassen verwenden: Kleinbuchstaben, Gro&szlig;buchstaben, Sonderzeichen, Ziffern oder Leerzeichen.");
		return (0);
	}
}


# validiert ob pw und login legal sind
# param login
# param pw
# return 0 = false, 1 = success
sub validate {
	my $ip = $ENV{'REMOTE_ADDR'};
	my $login = shift;
	my $pw = shift;
	my $sth = $dbh->prepare("SELECT pw , ip, status, id, NOW(), login FROM users WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array;
	if (scalar(@row) == 0) {
		$error = "User $login unbekannt!";
		return(0);
	}
	if (decode("utf-8", $row[0]) eq $pw) {
		if ($ip eq decode("utf-8", $row[1]) || $ip eq $superuser || $login eq "\'".$adminsName."\'") {
			# Login erfolgreich, generiere hash
			$terminhash = sha1_hex(decode("utf-8", $row[0]).$row[5]);
			return(1);
		}
		if ($ip eq $tvkurt) {
			my $time = $row[4];
			benachrichtige($row[3], "Login vom TvKurt aus am $time");
			return(1);
		}
		if (substr($ip,0,3) eq "10.")
		{
		       my $time = $row[4];
		       benachrichtige($row[3], "Login vom TuermeRoam aus am $time");
		       return(1);
		}

			#Workaround for high level no ip check
			#if($row[2] > 4){
			#	return(1);
			#}
		$error = "IP $ip stimmt nicht. Bitte vom eigenen Rechner oder TvKurt einloggen!";
		return (0);
	} else {
		$error = "Passwort falsch!";
		return(0);
	}
}

# Überprüft, ob der Loginname gültig ist
sub checkLogin {
	my $loginToProof = shift;
	if ($loginToProof =~ m/[^0-9a-zA-Z]/){
		printFehler("Loginname darf nur Buchstaben und Ziffern enthalten, keine Sonderzeichen und Umlaute!");
		return (1);
	} else {
		return (0);
	}
}

# Zählt, wie oft ein Loginname in der DB vorliegt
sub countLogin {
	my $loginToProof = vorbereiten(shift);
	my $sth = $dbh->prepare("SELECT * FROM users WHERE login = $loginToProof")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row;
	my $i = 0;
	while (@row = $sth->fetchrow_array()) {
		$i++;
	}
	return (i);
}

# stellt fest, ob ein User einen anderen User bearbeiten darf
sub darf_bearbeiten {
	my $zielId = shift;
	if ($zielId == $gId) {
		return (1);
	}
	my $sth = $dbh->prepare("SELECT status FROM users WHERE id = '$zielId'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if ($row[0] < $gStatus){
		return (1);
	} else {
		printFehler("Es d&uuml;rfen nur User mit einem kleineren Status bearbeitet werden!");
		return (0);
	}
}

# Angabe der Uhrzeit einer Waschterminzeit
# param ist Waschtermin-Zeit-Nummer
sub gibWaschTermin {
	my $i = shift;
	if (((($i*15)%10)*6) == 0) {
		return (($i*1.5-(($i*15)%10)/10).":00"." - ".(($i+1)*1.5-((($i+1)*15)%10)/10).":".(((($i+1)*15)%10)*6));
	} else {
		return (($i*1.5-(($i*15)%10)/10).":".((($i*15)%10)*6)." - ".(($i+1)*1.5-((($i+1)*15)%10)/10).":00");
	}
}

# Angabe der Uhrzeit einer Waschterminzeit mit dem Format XX:XX - XX:XX (auch Nullen)
# param ist Waschtermin-Zeit-Nummer
sub gibWaschTerminTechnisch {
	my $i = shift;
	my $start = "";
	if (($i*1.5-(($i*15)%10)/10)<10) {
		$start = "0";
	}
	if (((($i*15)%10)*6) == 0) {
		return ($start.($i*1.5-(($i*15)%10)/10).":00"." - ".(($i+1)*1.5-((($i+1)*15)%10)/10).":".(((($i+1)*15)%10)*6));
	} else {
		return ($start.($i*1.5-(($i*15)%10)/10).":".((($i*15)%10)*6)." - ".(($i+1)*1.5-((($i+1)*15)%10)/10).":00");
	}
}

# Setzt die Cookies, die fürs Validieren wichtig sind (Passwort und Login)
sub setCookies {
	my $login = shift;
	my $pw = shift;
	my $cLogin = $cgi->cookie (
		-NAME => 'wlogin',
		-VALUE => $login
	);
	my $cPw = $cgi->cookie (
		-NAME => 'wpw',
		-VALUE => $pw
	);
	print $cgi->redirect(-URL=>"$skript?aktion=index&del=no", -cookie=>[$cLogin, $cPw]);
}

# gibt das aktuelle Datum + n Tage (als Parameter) im richtigen Format für MySQL zurück
sub gibDatumString {
	my $n = shift;
	my @zeit = gibDatum($n);
	my $monat;
	my $tag;
	if ($zeit[1] < 10) {
		$monat = "0".$zeit[1];
	} else {
		$monat = $zeit[1];
	}
	if ($zeit[2] < 10) {
		$tag = "0".$zeit[2];
	} else {
		$tag = $zeit[2];
	}
	return($zeit[0]."-".$monat."-".$tag);
}


# alte Funktion - NICHT BENUTZEN
sub gibDatumZeitString {
	my @jetzt = localtime();
	return (gibDatumString(0)." ".$jetzt[2].":".$jetzt[1].":".$jetzt[0]);
}


# berechnet localtime + n Tage (als Parameter);
sub gibDatum {
	my $n = shift;
	my @jetzt = localtime();
	my @zeit;
	my $monat;
	$zeit[0] = 1900 + $jetzt[5];
	$zeit[1] = $jetzt[4] + 1;
	$zeit[2] = $jetzt[3];
	do {
		if ($zeit[1] == 1 || $zeit[1] == 3 || $zeit[1] == 5 || $zeit[1] == 7 || $zeit[1] == 8 || $zeit[1] == 10 || $zeit[1] == 12) {
			$monat = 31;
		} elsif ($zeit[1] == 2) {
			if (($zeit[0] % 4 == 0 && $zeit[0] % 100 != 0) || $zeit[0] % 400 == 0){
				$monat = 29;
			} else {
				$monat = 28;
			}
		} else {
			$monat = 30;
		}
		if($n <= $monat - $zeit[2]){
			$zeit[2] = $zeit[2] + $n;
			$n = 0;
		} else {
			if ($zeit[1] == 12){
				$zeit[0]++;
				$zeit[1] = 1;
			} else {
				$zeit[1]++;
			}
			$n = $n - 1 - ($monat - $zeit[2]);
			$zeit[2] = 1;
		}
	} until ($n == 0);
	return (@zeit);
}

# berechnet localtime + n Tage (als Parameter) mit Stunden, Minuten, Sekunden;
sub gibZeit {
	my $n = shift;
	my @zeit = gibDatum($n);
	my @jetzt = localtime();
	$zeit[3] = $jetzt[2];
	$zeit[4] = $jetzt[1];
	$zeit[5] = $jetzt[0];
	return (@zeit);
}

# bestimmt den Wochentag von localtime + n Tage (als Parameter) und gibt seine Nummer zurück (Mo = 0 bis 6 = So)
sub gibTag {
	my $n = shift;
	my @zeit = localtime();
	my $dow = ($zeit[6] - 1 + $n) % 7;
	return($dow);
}

# bestimmt den Wochentag von localtime + n Tage (als Parameter) und gibt seinen Namen zurück
sub gibTagText {
	my $n = shift;
	my @zeit = localtime();
	my $dow = ($zeit[6] - 1 + $n) % 7;
	if ($dow == 0){
		$dow = "Montag";
	} elsif ($dow == 1){
		$dow = "Dienstag";
	} elsif ($dow == 2){
		$dow = "Mittwoch";
	} elsif ($dow == 3){
		$dow = "Donnerstag";
	} elsif ($dow == 4){
		$dow = "Freitag";
	} elsif ($dow == 5){
		$dow = "Samstag";
	} elsif ($dow == 6){
		$dow = "Sonntag";
	}
	return($dow);
}

# bestimmt den Wochentag der Nummer n und gibt seinen Namen zurück
sub gibTagTextOhneOffset {
	my $dow = shift;
	if ($dow == 0){
		$dow = "Montag";
	} elsif ($dow == 1){
		$dow = "Dienstag";
	} elsif ($dow == 2){
		$dow = "Mittwoch";
	} elsif ($dow == 3){
		$dow = "Donnerstag";
	} elsif ($dow == 4){
		$dow = "Freitag";
	} elsif ($dow == 5){
		$dow = "Samstag";
	} elsif ($dow == 6){
		$dow = "Sonntag";
	} elsif ($dow == 8){
		$dow = "Wahrgenommen";
	}
	return($dow);
}

# gibt zurück, ob es sich um einen Float handelt
sub isNumeric {
	my $string = scalar(shift);
	if ($string =~ /^((-?\d*)((.\d\d)|(.\d))$)|^(-?)(\d+)$/) {
		return (1);
	} else {
		printFehler($string." ist keine g&uuml;ltige Dezimalzahl mit maximal zwei Nachkommastellen!");
		return (0);
	}
}

# gibt zurück, ob es sich um einen Int handelt
sub isNatural {
	my $string = shift;
	if ($string =~ m/[^0-9]/) {
		printFehler("$string ist keine g&uuml;ltige nat&uuml;rliche Zahl!");
		return (0);
	} else {
		return (1);
	}
}

# gibt eine Dezimalzahl als String der Form XX.XX zurück
sub printNumber {
	$zahl = 100 * shift;
	my $vorzeichen = "";
	if ( $zahl >= 0){
		if (abs($zahl) >= 100){
			return(substr($zahl, 0, length($zahl) - 2).".".substr($zahl, length($zahl) - 2, 2));
		} elsif (abs($zahl) >= 10){
			return ("0.".substr($zahl, length($zahl) - 2, 2));
		} else {
			return ("0.0".int($zahl));
		}
	} else {
		if (abs($zahl) >= 100){
			return(substr($zahl, 0, length($zahl) - 2).".".substr($zahl, length($zahl) - 2, 2));
		} elsif (abs($zahl) >= 10){
			return ("-0.".substr($zahl, length($zahl) - 2, 2));
		} else {
			return ("-0.0".substr($zahl, length($zahl) - 1, 1));
		}
	}
}

# sucht in einem String nach dem Vorkommen eines bestimmten Zeichens/Teilstrings
sub Anzahl {
	my $string = shift;
	my $suchzeichen = shift;
	my $count = 0;
	while ($string =~ m/$suchzeichen/) {
		$string =~ s/$suchzeichen//;
		$count++;
	}
	return ($count);
}

# formatiert Texte für MySQL, codiert Sonderzeichen
sub vorbereiten {
	my $string = shift;
	$string = $dbh->quote(encode("utf-8", $string));
	return ($string);
}

# fügt eine Nachricht bei einem User hinzu
sub benachrichtige {
	my $user = shift;
	my $nachricht = shift;
	my $sth = $dbh->prepare("SELECT message FROM users WHERE id = '$user'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	$row[0] = $row[0]."<br>".encode("utf-8", $nachricht);
	$sth = $dbh->prepare("UPDATE users SET message='$row[0]' WHERE id = '$user'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
}

# ----- ENDE DES HILFS-FUNKTIONEN-ABSCHNITTES -----


# ----- UNIVERSALMETHODEN FÜR LAYOUT UND SICHERHEIT -----

# Kopf jeder Seite, implementiert das Design der Netz-AG
sub print_header {
     print "Content-type: text/html\n\n";
     open (START, " /var/www/start.inc");
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

# Fu  jeder Seite, GegenstÃ¼ck zu print_header
sub print_footer {
	print "<br><br><br><table width=\"100%\" frame=\"above\" cellpadding=\"1\">";
	print "<tr><td align=\"left\"> $progName $version</td><td align=\"right\">by $godsName </td></tr>";
	print "<tr><td colspan=2><b>(1)</b> Sollte eine diese Zeitangaben mehr als 5 Minuten abweichen, das System <b>nicht</b> benutzen und <b>sofort</b> der WaschAG melden! </td></tr>";
	print "<tr><td colspan=2><b>(2)</b> Du bekommst f&uuml;r jede Einzahlung ab 25 Euro eine Bonusw&auml;sche und ab 50 Euro 3 Bonusw&auml;schen!</td></tr></table>";
     open (ENDE, "/var/www/start.inc");
          my @file = <ENDE>;
          print @file;
     close (ENDE);
  $dbh->disconnect;
}

# Titelleiste
# param Titel
sub Titel {
	my $titel = shift;
	print "<table><tr><th  colspan=\"2\" align=\"left\">Hallo $gName $gNname, willkommen im $progName : $titel</th></tr>";
	my $sth;
	my @row;
	if ($titel ne "Login") {
		$sth = $dbh->prepare("SELECT bestand, bonus FROM finanzlog WHERE user='$gId' ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		my $bestand = 0;
		if (@row = $sth->fetchrow_array()) {
			$bestand = $row[0];
			$bonus = $row[1];
		}
		print "<tr><td colspan=\"2\">Dein aktueller Kontostand betr&auml;gt <b>$bestand (+$bonus Bonus ) Euro</b><sup>(2)</sup>.</td></tr>";
	}
	$sth = $dbh->prepare("SELECT NOW()")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	 ($second, $minute, $hour, $day, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
	$year = 1900 + $yearOffset;
	$month++;
	if($month <10){ $month = "0$month";}
	if($day <10){ $day = "0$day";}
	if($second <10) {$second = "0$second";}
	if($hour <10){ $hour = "0$hour";}
	if($minute <10){ $minute = "0$minute";}
	$theTime = "$year-$month-$day $hour:$minute:$second";
	#print "<tr style=\"font-size: 0.8em\"><td>Datenbankzeit: </td><td> ".$row[0]." Uhr</td><td>&nbsp;</td><td>aktuelle Serverzeit: </td><td>$theTime Uhr<b>(1)</b></td></tr></table>";
	print "<table style=\"font-size: 0.8em\"><tr><td>Datenbankzeit: </td><td> ".$row[0]." Uhr</td><td></td></tr><tr><td>aktuelle Serverzeit: </td><td>$theTime Uhr <b> (1)</b></td></tr></table>"
}

# Universalfunktion zum Validieren der Logindaten, überprüfen der Zugriffsrechte, setzen des Titels und Erstellen der Menüleisten
# param anliegen, benötigter Status
sub kopf {
	my $anliegen = shift;
	my $neededStatus = shift;
	# Auslesen der Cookies
	my $login = cookie("wlogin");
	my $pw = cookie("wpw");
	if (validate($login, $pw) == 0) {
		# Aufforderung zum erneuten Login bei falschen Eingabedaten
		print_header();
		Titel("Login");
		logon();
		return (0);
	} else {
		# Setzen globaler Variablen
		my $sth = $dbh->prepare("SELECT ip, name, nachname, status, id, gesperrt, login FROM users WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();	# führt den befehl aus
		my @row = $sth->fetchrow_array();
		our $gIp = decode("utf-8", $row[0]);
		our $gName = decode("utf-8", $row[1]);
		our $gNname = decode("utf-8", $row[2]);
		our $gStatus = decode("utf-8", $row[3]);
		our $gId = decode("utf-8", $row[4]);
		our $gSperre = decode("utf-8", $row[5]);
		our $gLogin = decode("utf-8", $row[6]);
		print_header();
		if (($wartung && $gStatus < $waschag) || ($godWartung && $gStatus < $god)) {
			Titel("Wartungsarbeiten");
			printFehler("<br><br>Momentan werden Wartungsarbeiten am System durchgef&uuml;hrt. Habe bitte ein bisschen Geduld!");
			return (0);
		}
		# Überprüfung der Zugriffsrechte, ggf. Meldung einer Zugriffsverletzung an die DB
		if ($gStatus < $neededStatus) {
			printFehler ("Zugang zu Interna verweigert! Benachrichtigung an Admins versendet.<br><br>Weitere Zugriffsversuche werden geahndet!");
			$sth = $dbh->prepare("INSERT INTO notify VALUES (".vorbereiten($gId).", ".vorbereiten($anliegen).", ".vorbereiten(gibDatumString(0)).")")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
			$sth->execute();	# führt den befehl aus
			return (0);
		}

		if ($anliegen eq "index"){
			Titel("Hauptmen&uuml;");
		} elsif ($anliegen eq "new_user") {
			Titel("Neuen User erstellen");
		} elsif ($anliegen eq "delete_user") {
			Titel("User l&ouml;schen");
		} elsif ($anliegen eq "do_edit") {
			Titel("User bearbeiten");
		} elsif ($anliegen eq "edit_user") {
			Titel("User bearbeiten");
		} elsif ($anliegen eq "create_user") {
			Titel("Neuen User erstellen");
		} elsif ($anliegen eq "user_management") {
			Titel("Userverwaltung");
		} elsif ($anliegen eq "manage_money") {
			Titel("Geld ein-/auszahlen");
		} elsif ($anliegen eq "storno") {
			Titel("Kulanz gew&auml;hren");
		} elsif ($anliegen eq "kontoauszug") {
			Titel("Kontoauszug");
		} elsif ($anliegen eq "set_preis") {
			Titel("Preise aendern");
		} elsif ($anliegen eq "waschmaschinen") {
			Titel("Waschmaschinen und Haupteinstellungen konfigurieren");
		} elsif ($anliegen eq "look_termine") {
			Titel("Terminverwaltung");
		} elsif ($anliegen eq "notify_management") {
			Titel("Firewall-Log");
		} elsif ($anliegen eq "ueberweisung") {
			Titel("&Uuml;berweisung");
		} elsif ($anliegen eq "show_doku") {
			Titel("Hilfe");
		} elsif ($anliegen eq "edit_doku") {
			Titel("Hilfe bearbeiten");
		} elsif ($anliegen eq "change_pw") {
			Titel("Passwort &auml;ndern");
		} elsif ($anliegen eq "stats") {
			Titel("Statistik");
		} elsif ($anliegen eq "data") {
			Titel("Logbuch");
		} elsif ($anliegen eq "shout") {
			Titel("Massennachricht");
		}
		# Menüleisten nach Benutzerstatus
		if ($gStatus >= $user) {
			print "<table cellspacing=\"10\" cellpadding=\"5\" width=\"100%\">";
			print "<tr><td align=\"center\"><a href=\"$skript?aktion=index\">Willkommensseite</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=look_termine\">Termin buchen</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=kontoauszug\">Kontoauszug</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=ueberweisungsformular\">&Uuml;berweisung anlegen</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=change_pw\">Passwort &auml;ndern</a></td>";
			print "<td align=\"center\">Hilfe ansehen<br><a href=\"$skript?aktion=show_doku&lang=ger\">Deutsch</a>/<a href=\"$skript?aktion=show_doku&lang=eng\">Englisch</a></td>";
			print "</tr></table>";
			}
		if ($gStatus >= $waschag){
			print "<table cellspacing=\"10\" cellpadding=\"5\" width=\"100%\">";
			print "<tr><td align=\"center\"><a href=\"$skript?aktion=new_user\">Neuen User erstellen</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=user_management&sort=id%20ASC\">Userverwaltung</a></td>";
			if ($gStatus >= $god) {
				print "<td align=\"center\"><a href=\"$skript?aktion=preisliste\">Preisverwaltung</a></td>";
			}
			print "<td align=\"center\"><a href=\"$skript?aktion=waschmaschinen\">Waschmaschinenverwaltung und Konfiguration</a></td>";
			print "</table><table cellspacing=\"10\" cellpadding=\"5\" width=\"100%\">";
			print "</tr><tr><td align=\"center\"><a href=\"$skript?aktion=notify_management&sort=id%20ASC\">Firewall-<br>Logfile</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=stats\">Statistik</a></td>";
			if ($gStatus >= $god) {
				print "<td align=\"center\">Hilfe bearbeiten<br><a href=\"$skript?aktion=edit_doku&lang=ger\">Deutsch</a>/<a href=\"$skript?aktion=edit_doku&lang=eng\">Englisch</a></td>";
			}
			print "<td align=\"center\"><a href=\"$skript?aktion=look_old_data&dir=./logs&file=.\">Alte Daten ansehen</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=create_shout\">Massennachricht<br>versenden</a></td>";
			print "</tr></table>";
		}
	}
	getConfig();
	return (1);
}

# Macht eine Tabellenzeile für die Userverwaltung mit den beiden Buttons "bearbeiten" und "löschen"
# param farbe, Zellen als Array (beginnend mit der id)
sub tabellenZeile {
	print "<tr>";
	my $farbe = shift;
	my $id = $_[0];
	foreach (@_) {
		print "<td align=\"center\">"."<font color=\"$farbe\">".decode("utf-8", $_)."</font>"."</td>";
	}
	print "<td align=\"center\"><a href=\"$skript?aktion=edit_user&id=$id\">bearbeiten</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=delete_user&id=$id\">l&ouml;schen</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=manage_money&id=$id\">ein-\/auszahlen</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=show_user_finance&id=$id\">Konto</a></td>";
	print "</tr>";
}

sub BannedTabellenZeile {
	print "<tr valign=\"top\">";
	my $bemerkungsfeld = shift;
	my $farbe = shift;
	my $id = $_[0];
	my $counter = 0;
	foreach (@_) {
		if ($counter == $bemerkungsfeld) {
			print "<td align=\"left\">"."<p align=\"justify\"><font color=\"$farbe\">".decode("utf-8", $_)."</font></p>"."</td>";
		} else {
			print "<td align=\"center\">"."<font color=\"$farbe\">".decode("utf-8", $_)."</font>"."</td>";
		}
		$counter++;
	}
	print "<td align=\"center\"><a href=\"$skript?aktion=edit_user&id=$id\">bearbeiten</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=delete_user&id=$id\">l&ouml;schen</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=show_user_finance&id=$id\">Konto</a></td>";
	print "</tr>";
}

# Macht eine Tabellenzeile
# param farbe, Zellen als Array (beginnend mit der id)
sub normalTabellenZeile {
	print "<tr>";
	my $farbe = shift;
	foreach (@_) {
		print "<td align=\"center\">"."<font color=\"$farbe\">".decode("utf-8", $_)."</font>"."</td>";
	}
	print "</tr>";
}

# Macht eine Tabellenzeile für die Titelzeile der Tabelle
# param farbe, Zellen als Array (beginnend mit der id)
sub normalTabellenZeileKopf {
	print "<tr>";
	my $farbe = shift;
	my $id = $_[0];
	foreach (@_) {
		print "<th align=\"center\">"."<font color=\"$farbe\">".decode("utf-8", $_)."</font>"."</th>";
	}
	print "</tr>";
}

# Sperrfunktion
sub sperrCheck {
	my $botschaft = shift;
	if ($gSperre == 1){
		printFehler("<b>Du bist gesperrt!</b> $botschaft");
		return(1);
	}
	return(0);
}


# ----- ENDE UNIVERSALMETHODEN -----


# ----- LOGIN -----

# Login-Formular
sub logon {
	my $login = "";
	$login = shift;
	if ($error ne '') {
		printFehler($error);
		$error = '';
	}
	print "<form action=\"$skript?aktion=login\" method=\"post\">";
	print "<table style='border: 0px;'><tr><td>Login:</td><td><input name=\"login\" size=\"40\" value=\"$login\"></td></tr>";
	print "<tr><td>Passwort:</td><td><input name=\"pw\" type=\"password\" size=\"40\"></td></tr></table><br>";
	print "<input type=\"submit\" value=\"Einloggen\"></form>";
}

# prüft die beim Login eingegebenen Werte und setzt die Cookies
sub firstLogin {
	my $login = $cgi->param('login');
	my $pw = crypt($cgi->param('pw'), "ps");
	if (validate(vorbereiten($login), $pw) == 1){
		$login = vorbereiten($login);
		getConfig();
		my $jetzt = gibDatumString(0);
		my $sth = $dbh->prepare("SELECT lastlogin FROM users WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		my @row = $sth->fetchrow_array();
		if(substr($row[0], 5, 2) ne substr($jetzt, 5, 2)) { # Monatwechsel
			$sth = $dbh->prepare("UPDATE users SET termine='0', gotfreimarken='0' WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			$sth->execute();
		}
		# Freimarken-Geschichte
		$sth = $dbh->prepare("SELECT status, gotfreimarken, id FROM users WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		@row = $sth->fetchrow_array();
		if($row[0] >= $waschag && $row[1] == 0) {
				$sth = $dbh->prepare("UPDATE users SET gotfreimarken='1' WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth->execute();
				geldbewegung($row[2], 0, encode("utf-8", "monatliches Freigeld f&uuml;r WaschAG-Mitglieder"), $freiGeld);
				benachrichtige($row[2], "Du hast dein monatliches Freigeld f&uuml;r WaschAG-Mitglieder erhalten.");
		}
		$sth = $dbh->prepare("UPDATE users SET lastlogin='$jetzt' WHERE login = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		setCookies($login, $pw);
	} else {
		print_header();
		Titel("Login");
		logon($login);
	}
}

# ----- ENDE LOGIN -----


# ----- HAUPTMENÜ -----

# Stellt das Hauptmenü dar, löscht je nach Verlangen die hinterlassene Nachricht
sub hauptMenue {
	if ($cgi->url_param('del') eq 'yes'){
		delete_message();
	}
	if ($cgi->url_param('storn') eq 'yes'){
		stornieren($cgi->url_param('datum'), $cgi->url_param('zeit'), $cgi->url_param('maschine'));
	}
	my $sth = $dbh->prepare("SELECT message , gesperrt, termine FROM users WHERE id='$gId'")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if ($row[0] ne "") {
		my $nachricht = decode("utf-8", $row[0]);
		print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>$nachricht</th>";
		print "<th><a href=\"$skript?aktion=index&del=yes\">l&ouml;schen</a></th></tr></table><br>";
	}
	my $monatlTermine = $row[2];
	if ($row[1] == 1) {
		printFehler("Du wurdest gesperrt!");
	} else {
		print "Du hast bereits $monatlTermine Termine von maximal $termPerMonth erlaubten Terminen pro Monat wahrgenommen oder nicht storniert.<br>";
		print "Damit bleiben dir noch ".($termPerMonth-$row[2])." Termine.";
		$sth = $dbh->prepare("SELECT COUNT(*) FROM termine WHERE user='$gId' ORDER BY datum ASC, zeit ASC, maschine ASC")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		@row = $sth->fetchrow_array();
		if ($row[0] > 0) {
			$sth = $dbh->prepare("SELECT wochentag, datum, zeit, maschine, bonus FROM termine WHERE user='$gId' ORDER BY datum ASC, zeit ASC, maschine ASC")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			$sth->execute();
			print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>Deine gebuchten Termine:</th></tr></table>";
			print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
			while(@row = $sth->fetchrow_array()){
				if ($row[0] != 8) {
					my $bonustermin = "";
					if($row[4] != 0) { $bonustermin = "(Bonustermin)"; } 
					normalTabellenZeile("black", gibTagTextOhneOffset($row[0]), $row[1], gibWaschTermin($row[2])." Uhr", "Maschine ".$row[3]. " ".$bonustermin."<a href=\"$skript?aktion=index&storn=yes&datum=$row[1]&zeit=$row[2]&maschine=$row[3]\">stornieren</a>");
				}
			}
			print "</table>";
		}
	}
}

# Löschen der Nachricht
sub delete_message {
	my $sth = $dbh->prepare("UPDATE users SET message='' WHERE id='$gId'")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
}

# ----- ENDE HAUPTMENÜ -----


# ----- USERVERWALTUNG UND ERSTELLUNG -----

# Hilfsfunktion, die Texte darauf überprüft, ob sie leer sind
# param zu untersuchender String, Bezeichnung für Fehlermeldung
sub notLeer {
	my $string = shift;
	my $bezeichnung = shift;
	if ($string eq ""){
		printFehler("$bezeichnung muss ausgef&uuml;llt werden!");
		return (1);
	}
	return (0);
}

# Hilfsfunktion, die überprüft, ob es sich um ein mögliches TvK-Zimmer handelt
# param zu untersuchender String, Bezeichnung für Fehlermeldung
sub isValidZimmer {
	$zimmer = shift;
	if (int($zimmer / 100) >= 1 && int($zimmer / 100) <= 15 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 16)){
		return (0);
	} elsif ($zimmer == -101 || int($zimmer) == -1 || int($zimmer) == 0 || int($zimmer) == 1 || int($zimmer) == 2 || int($zimmer) == 3 || int($zimmer) == 4) {
		return (0);
	} else {
		printFehler("Zimmernummer ung&uuml;ltig!");
		return (1);
	}
}

# Hilfsfunktion, die überprüft, ob es sich um eine im TvK gültige IP handelt
# param zu untersuchender String, Bezeichnung für Fehlermeldung
sub isValidIP {
	my $ip = shift;
	if ($ip eq "0.0.0.0") {
		return(0)
	} elsif (substr($ip, 0, 10) eq "137.226.14" && (substr($ip, 10, 1) eq "2" || substr($ip, 10, 1) eq "3" ) && substr($ip, 12, 3) >= 0 && substr($ip, 12, 3) <= 255) {
		return (0);
	} else {
		printFehler("IP Adresse ung&uuml;ltig!");
		return (1);
	}
}

#Hilfsfunktion zur Generierung neuer Passwörter
sub genPw {
   my $length = 8 + (int(rand(2)));
   my @possible = ('abcdefghijkmnpqrstuvwxyz', '23456789', 'ABCDEFGHJKLMNPQRSTUVWXYZ');
   my $password;
   my @types = (0,0,0);
   while (length($password) < $length -3) {
	my $i = (int(rand(scalar(@possible))));
	$types[$i] = 1;
	$password .= substr($possible[$i], (int(rand(length($possible[$i])))), 1);
   }
   
   for(my $i = 0; $i < 3; $i++) {
	if($types[$i] < 1){
		$password .= substr($possible[$i], (int(rand(length($possible[$i])))), 1);
	}else{
		my $j = (int(rand(scalar(@possible))));
		$password .= substr($possible[$j], (int(rand(length($possible[$j])))), 1);
	}
   }
   return $password;
}

# Formular zum ändern des Passwortes
sub changePW {
	print "<form action=\"$skript?aktion=do_change_pw\" method=\"post\">";
	print "<table cellspacing=\"5\" cellpadding=\"3\">";
	print "<tr><th>Altes Passwort:</th><th><input name=\"oldpw\" type=\"password\" size=\"40\"></th></tr>";
	print "<tr><th>Neues Passwort:</th><th><input name=\"pw\" type=\"password\" size=\"40\"></th></tr>";
	print "<tr><th>Neues Passwort wiederholen:</th><th><input name=\"pww\" type=\"password\" size=\"40\"></th></tr>";
	print "</table><input type=\"submit\" value=\"Passwort &auml;ndern\"></form>";
	print "Dein neues Passwort muss mindestens aus 8 Zeichen bestehen und 3 verschiedene Zeichenklassen beinhalten.<br>Es gibt 5 Zeichenklassen:<br>";
	print "Kleinbuchstaben, Gro&szlig;buchstaben, Sonderzeichen und Umlaute, Leerzeichen, Ziffern.";
}

sub doChange {
	my $oldpw = $cgi->param('oldpw');
	my $pw = $cgi->param('pw');
	my $pww = $cgi->param('pww');
	if (crypt($oldpw, "ps") ne cookie("wpw")) {
		printFehler("Passwort inkorrekt");
		return;
	}
	if ($pw ne $pww) {
		printFehler("Passw&ouml;rter unterschiedlich!");
	} else {
		if ($pw ne '') {
			if (checkPW($pw) == 1) {
				$pw = crypt($pw, "ps");
				my $sql = "UPDATE users SET pw='$pw' WHERE id='$gId'";
				$sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				printFehler("Dein Passwort wurde erfolgreich ge&auml;ndert!\n");
				printFehler("Du musst dich jetzt neu <a href=\"$skript?aktion=login\">einloggen.</a>");
				return;
			}
		} else {
			printFehler("Kein Passwort eingegeben, Passwort nicht ge&auml;ndert!");
			return;
		}
	}
	changePW();
}

# Formular zum Eingeben der Daten für einen neuen User
sub gibNewForm {
	if(sperrCheck()==1) { return; }
	my $login = shift;
	my $name = shift;
	my $nname = shift;
	my $zimmer = shift;
	my $ip = shift;
	if ($ip eq "") {
		$ip = "137.226.14"
	}
	print "<form action=\"$skript?aktion=create_user\" method=\"post\">";
	print "<table cellspacing=\"5\" cellpadding=\"3\" style='border: 0px;'>";
	print "<tr><td>Login:</td><td><input name=\"login\" size=\"40\" value=\"$login\"></td></tr>";
	print "<tr><td>Nachname:</td><td><input name=\"nachname\" size=\"40\" value=\"$nname\"></td></tr>";
	print "<tr><td>Vorname:</td><td><input name=\"name\" size=\"40\" value=\"$name\"></td></tr>";	
	print "<tr><td>Zimmer:</td><td><input name=\"zimmer\" size=\"4\" value=\"$zimmer\"></td></tr>";
	print "<tr><td>IP:</td><td><input name=\"ip\" size=\"15\" value=\"$ip\"></td></tr>";
	print "</table><input type=\"submit\" value=\"Formulardaten absenden\"></form>";
	print "Falls kein Netz-AG-Account vorhanden, dann f&uuml;r IP \"0.0.0.0\" eingeben.";
}

# erstellt einen neuen User in der DB
sub create_user {
	if(sperrCheck()==1) { return; }
	#holen der Daten
	my $login = $cgi->param('login');
	my $name = $cgi->param('name');
	my $nname = $cgi->param('nachname');
	my $zimmer = $cgi->param('zimmer');
	my $ip = $cgi->param('ip');
	my $ok = notLeer($login, 'Loginname')
				 + notLeer($name, 'Vorname')
				 + notLeer($nname, 'Nachname')
				 + notLeer($login, 'Loginname')
				 + isValidZimmer($zimmer)
				 + isValidIP($ip);

  	my $sth = $dbh->prepare("SELECT * FROM users WHERE login = ".vorbereiten($login))|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	if (my @row = $sth->fetchrow_array()) {
		printFehler("Loginname bereits vorhanden!");
		gibNewForm('', $name, $nname, $zimmer, $ip);
		return;
	}



	if ($ok == 0) {
		$sth = $dbh->prepare("SELECT id FROM users WHERE ip = '$ip'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		if (@row = $sth->fetchrow_array()) {
			printFehler("<b><font color=\"#ff0000\">Ip bereits bei User $row[0] vorhanden. Unbedingt &uuml;berpr&uuml;fen!</font></b>");
		}
		$sth = $dbh->prepare("SELECT id FROM users WHERE zimmer = '$zimmer'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		if (@row = $sth->fetchrow_array()) {
			printFehler("<b><font color=\"#ff0000\">Zimmernummer bereits bei User $row[0] vorhanden. Unbedingt &uuml;berpr&uuml;fen!</font></b>");
		}
		$pw = genPw();
		printFehler("<br>Es wurde folgendes Passwort generiert: <b>$pw</b> <br>");
		$pw = crypt($pw, "ps");
		my $sql = "INSERT INTO users ( id , name , nachname , pw , login , zimmer , gesperrt , message , ip , status, von ) VALUES ('', '$name', '$nname', '$pw', '$login', '$zimmer', '0', '', '$ip', '1' , '$gId')";
		$sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth = $dbh->prepare("SELECT MAX(id) FROM users")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	  	$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		my @row = $sth->fetchrow_array();
		$sth = $dbh->prepare("INSERT INTO finanzlog VALUES ('$row[0]', '0', '0', 'Account-Erstellung', NOW(), '0')")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	  	$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	  	$sth = $dbh->prepare("INSERT INTO waschagtransaktionen VALUES ('$row[0]', '0', '0', 'Account-Erstellung', NOW())")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	  	$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth = $dbh->prepare("SELECT id FROM users WHERE login = ".vorbereiten($login))|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		@row = $sth->fetchrow_array();
		printFehler("Der User Nummer - $row[0] - wurde erfolgreich erstellt!");
	} else {
		gibNewForm($login, $name, $nname, $zimmer, $ip);
	}
	$dbh->disconnect;
}

# stellt die Userliste bereit
# param sortierung
sub userVerwaltung {
	if(sperrCheck()==1) { return; }
	my $sortierung = $cgi->url_param('sort');
	my $zimmernummer= $cgi->url_param('zimmer');
	my $etagennummer= $cgi->url_param('etage');
	my $zimmer_add = "1";
	print <<ENDE_DES_STRINGS;
<script type="text/javascript">
JumpFlag=1;
function go2next(CurrentInp) 
{ 
with (CurrentInp) 
{
if ( (value.length==maxLength) && (tabIndex<=document.FX.elements.length-1) )
{
	document.FX.elements[tabIndex].focus();
}
}
} 
	</script>
ENDE_DES_STRINGS

	print "<form action=\"$skript\" name=\"FX\" method=\"get\">";
	print "<input type=\"hidden\" tabindex=\"1\" name=\"aktion\" value=\"user_management\">";
	print "<input type=\"hidden\" tabindex=\"2\" name=\"sort\" value=\"$sortierung\">";
	print "Zeige nur Etage-Zimmer (freilassen zeigt jew. alle): <input type=\"text\" tabindex=\"3\" name=\"etage\" size=\"2\" maxlength=\"2\" value=\"".$etagennummer."\" onKeyup=\"go2next(this)\">";
	print "-<input type=\"text\"  tabindex=\"4\" name=\"zimmer\" size=\"2\" maxlength=\"2\" value=\"".$zimmernummer."\" onKeyUp=\"go2next(this)\">";
	print "<input type=\"submit\" tabindex=\"5\" value=\"Anzeigen!\"></form>";
	if($zimmernummer > 0 || $etagennummer > 0){
		if($zimmernummer > 0 && $etagennummer > 0 && isValidZimmer($etagennummer*100+$zimmernummer) == 0){
			$zimmer_add = " zimmer = '".($etagennummer*100+$zimmernummer)."' ";
			print "Zeige nur User f&uuml;r Zimmer ".($etagennummer*100+$zimmernummer).":";
		}
		if($zimmernummer > 0 && $etagennummer == 0){
			$zimmer_add = "(zimmer%100) = '".$zimmernummer."'";
			print "Zeige nur User die im ".$zimmernummer.". Zimmer wohnen:";
		}
		if($zimmernummer== 0 && $etagennummer > 0){
			$zimmer_add = " zimmer > '".($etagennummer*100)."' AND zimmer < '".($etagennummer*100+100)."'";
			print "Zeige nur User die auf Etage ".$etagennummer." wohnen:";
		}
	}
	my $sth = $dbh->prepare("SELECT id, nachname, name, login, zimmer, gesperrt, status, lastlogin, ip FROM users WHERE ".$zimmer_add." ORDER BY $sortierung")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row;
	print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
	my $zimmerinfos = "&zimmer=".$zimmernummer."&etage=".$etagennummer;
	normalTabellenZeileKopf("black",
								"id<br><a href=\"$skript?aktion=user_management&sort=id%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=id%20DESC".$zimmerinfos."\">&gt;</a>",
								"Nachname<br><a href=\"$skript?aktion=user_management&sort=nachname%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=nachname%20DESC".$zimmerinfos."\">&gt;</a>",
								"Name<br><a href=\"$skript?aktion=user_management&sort=name%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=name%20DESC".$zimmerinfos."\">&gt;</a>",
								"Login<br><a href=\"$skript?aktion=user_management&sort=login%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=login%20DESC".$zimmerinfos."\">&gt;</a>",
								"Zimmer<br><a href=\"$skript?aktion=user_management&sort=zimmer%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=zimmer%20DESC".$zimmerinfos."\">&gt;</a>",
								"Sperre<br><a href=\"$skript?aktion=user_management&sort=gesperrt%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=gesperrt%20DESC".$zimmerinfos."\">&gt;</a>",
								"Status<br><a href=\"$skript?aktion=user_management&sort=status%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=status%20DESC".$zimmerinfos."\">&gt;</a>",
								"Letzter Login<br><a href=\"$skript?aktion=user_management&sort=lastlogin%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=lastlogin%20DESC".$zimmerinfos."\">&gt;</a>",
								"IP<br><a href=\"$skript?aktion=user_management&sort=ip%20ASC".$zimmerinfos."\">&lt;</a><a href=\"$skript?aktion=user_management&sort=ip%20DESC".$zimmerinfos."\">&gt;</a>");
	while (@row = $sth->fetchrow_array) {
		if ($row[5] == 1) {
			tabellenZeile("red", @row);
		} else {
			tabellenZeile("black", @row);
		}
	}
	print "</table>";
	$dbh->disconnect;
}

# zeigt Kontoauszug von einem User an
sub user_finance {
	my $id = shift;
	my $sth = $dbh->prepare("SELECT name, nachname, status FROM users WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row;
	my $status;
	my $name;
	my $nname;
	if (@row = $sth->fetchrow_array()) {
		$name = $row[0];
		$nname = $row[1];
		$status = $row[2];
	} else {
		printFehler("User existiert nicht!");
	}
	$sth = $dbh->prepare("SELECT datum, bemerkung, aktion, bestand, bonus FROM finanzlog WHERE user='$id' ORDER BY datum ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	if (@row = $sth->fetchrow_array()) {
		my @temp = @row;
		print "<br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
		print decode("utf-8", $name)." ".decode("utf-8", $nname).": Kontostand am ".substr($row[0],0,10)." um ".substr($row[0],11,8)." Uhr betrug ".printNumber($row[3])." Euro.";
		print "</th></tr></table><br><br>";
		print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
		normalTabellenZeileKopf("black", "Datum", "Erl&auml;uterung", "Betrag<br>(Euro)", "Bestand nachher<br>(Euro)", "Bonus nachher<br>(Euro)");
		while (@row = $sth->fetchrow_array){
			@temp = @row;
			if ($row[2] >= 0) {
				normalTabellenZeile("black", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]), printNumber($row[4]));
			} else {
				normalTabellenZeile("red", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]), printNumber($row[4]));
			}
		}
		print "</table><br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
		print "Der aktuelle Kontostand betr&auml;gt ".printNumber($temp[3])." (+".printNumber($temp[4])." Bonus) Euro.";
		print "</th></tr></table><br><br>";
	} else {
		print "<br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
		print "Keine Kontoinformationen vorhanden.";
		print "</th></tr></table><br><br>";
	}
	if($status >= $waschag) {
		$sth = $dbh->prepare("SELECT datum, bemerkung, aktion, bestand FROM waschagtransaktionen WHERE user='$id' ORDER BY datum ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		my @row;
		if (@row = $sth->fetchrow_array) {
			my @temp = @row;
			print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
			print "----------------------------------------<br><br><br><br>";
			print "$name $nname: Der WaschAG-Kontostand am ".substr($row[0],0,10)." um ".substr($row[0],11,8)." Uhr betrug ".printNumber($row[3])." Euro.";
			print "</th></tr></table><br><br>";
			print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
			normalTabellenZeileKopf("black", "Datum", "Erl&auml;uterung", "Betrag<br>(Euro)", "Bestand nachher<br>(Euro)");
			while (@row = $sth->fetchrow_array){
				@temp = @row;
				if ($row[2] >= 0) {
					normalTabellenZeile("black", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]));
				} else {
					normalTabellenZeile("red", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]));
				}
			}
			print "</table><br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
			print "Der aktuelle Kontostand betr&auml;gt ".printNumber($temp[3])." Euro.";
			print "</th></tr></table><br><br>";
		} else {
			print "<br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
			print "Keine Kontoinformationen vorhanden.";
			print "</th></tr></table><br><br>";
		}
	}
}

# Abfragelink, ob ein User wirklich gelöscht werden soll
sub delete_user {
	if(sperrCheck()==1) { return; }
	my $id = shift;
	print "<a href=\"$skript?aktion=mach_tot&id=$id\">Dieser Link l&ouml;scht User $id endg&uuml;ltig!</a>";
}

# löscht einen User endgültig
sub deleteUserEndgueltig {
	if(sperrCheck()==1) { return; }
	my $id = shift;
	if (darf_bearbeiten($id) == 0) {
		return;
	}
	my $sth = $dbh->prepare("DELETE FROM users WHERE id=$id")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	printFehler("User gel&ouml;scht");
}

sub start_edit {
	if(sperrCheck()==1) { return; }
	#holt die Daten eines Users aus der DB um sie dem EditForm zu übergeben
	my $id = shift;
	my $sth = $dbh->prepare("SELECT login , name , nachname , status , zimmer , ip , gesperrt , message , bemerkung, termine, lastlogin FROM users WHERE id=$id")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	gibEditForm($id, @row)
}

sub gibEditForm {
	if(sperrCheck()==1) { return; }
	my $id = shift;
	my $login = decode("utf-8",shift);
	my $name = decode("utf-8",shift);
	my $nname = decode("utf-8",shift);
	my $status = shift;
	my $zimmer = shift;
	my $ip = shift;
	my $sperre = shift;
	my $nachricht = decode("utf-8",shift);
	my $bemerkung = decode("utf-8",shift);
	my $termine = shift;
	my $lastlogin = shift;
	my $jetzt = gibDatumString(0);

	
	print "<form action=\"$skript?aktion=do_edit&id=$id\" method=\"post\">";
	print "<table style='border: 0px;'><tr><td>Vorname:</td><td><input name=\"name\" size=\"30\" value=\"$name\"></td></tr>";
	print "<tr><td>Nachname:</td><td><input name=\"nachname\" size=\"30\" value=\"$nname\"></td></tr>";
	print "<tr><td>Login:</td><td><input name=\"login\" size=\"30\" value=\"$login\"></td></tr>";
	print "<tr><td>Passwort &auml;ndern:</td><td><input type=\"checkbox\" name=\"pw\" value=\"pwchange\"></td></tr>";
	if ($sperre == 1) {
		print "<tr><td>Sperre:</td><td><input type=\"checkbox\" name=\"sperre\" value=\"gesperrt\" checked=\"checked\"></td></tr>";
	} else {
		print "<tr><td>Sperre:</td><td><input type=\"checkbox\" name=\"sperre\" value=\"gesperrt\"></td></tr>";
	}
	print "<tr><td>Status:</td><td><input name=\"status\" size=\"2\" value=\"$status\"></td></tr>";
	print "<tr><td>Zimmer:</td><td><input name=\"zimmer\" size=\"4\" value=\"$zimmer\"></td></tr>";
	print "<tr><td>IP: </td><td><input name=\"ip\" size=\"15\" value=\"$ip\"></td></tr>";
	if(substr($lastlogin, 5, 2) ne substr($jetzt, 5, 2)) { # Monatwechsel
		print "<tr><td colspan=2>Der User war diesen Monat noch nicht eingeloggt. In der Datenbank stehen deswegen noch $termine Termine.</td></tr>";
	} else {
		print "<tr><td>Bereits verbrauchte Termine: </td><td><input name=\"termine\" size=\"3\" value=\"$termine\"></td></tr>";
	}
	print "</table><p>Nachricht f&uuml;r User:<br><textarea name=\"nachricht\" cols=\"50\" rows=\"10\">$nachricht</textarea></p>";
	print "<p>Bemerkung (z.B. f&uuml;r Sperren):<br><textarea name=\"bemerkung\" cols=\"50\" rows=\"10\">$bemerkung</textarea></p>";
	print "<p><input type=\"submit\" value=\"Formulardaten absenden\"></p></form>";
}

sub do_edit {
	if(sperrCheck()==1) { return; }
	#holen der Daten
	my $pw = $cgi->param('pw');;
	my $login = $cgi->param('login');
	my $name = $cgi->param('name');
	my $nname = $cgi->param('nachname');
	my $zimmer = $cgi->param('zimmer');
	my $ip = $cgi->param('ip');
	my $id = $cgi->url_param('id');
	my $status = $cgi->param('status');
	my $sperre = $cgi->param('sperre');
	my $nachricht = $cgi->param('nachricht');
	my $bemerkung = $cgi->param('bemerkung');
	my $termine = $cgi->param('termine');
	my $ok = notLeer($login, 'Loginname')
				 + notLeer($name, 'Vorname')
				 + notLeer($nname, 'Nachname')
				 + notLeer($login, 'Loginname')
				 + isValidZimmer($zimmer, 'Zimmer')
				 + isValidIP($ip, 'IP');

	if (darf_bearbeiten($id) == 0){
		printFehler("Status ung&uuml;ltig! Status muss kleiner als dein eigener sein, au&szlig;er du bearbeitest dich selber!");
		$ok = 1;
	}

	if ($status > $gStatus || ($id != $gId && $status == $gStatus)) {
		printFehler("Du darfst den Status nicht auf deinen oder h&ouml;her anheben!");
		$ok = 1;
	}

	my $sth = $dbh->prepare("SELECT id FROM users WHERE login = ".vorbereiten($login))|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();	# führt den befehl aus
	my @row = $sth->fetchrow_array;
	if (scalar(@row) != 0) {
		if ($row[0] != $id) {
			printFehler("Loginname bereits vorhanden!");
			$ok = 1;
		}
	}

	if ($ok == 0) {
		my $change;
		if ($sperre ne "gesperrt") {
			$sperre = vorbereiten(0);
		} else {
			my $erstattung = 0;
			$sperre = vorbereiten(1);
			$sth = $dbh->prepare("SELECT wochentag, zeit, datum, bonus FROM termine WHERE user ='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			$sth->execute();
			while (@row = $sth->fetchrow_array()){
				if (wieLangSchon($row[1],$row[2]) < 0) {
					my $preis = getPreis($row[0], $row[1]);
					$erstattung += $preis;
					my $sth2 = $dbh->prepare("UPDATE users SET termine = termine - 1 WHERE id = '$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
					$sth2->execute();
					my $sth3 = $dbh->prepare("DELETE FROM termine WHERE user ='$id' AND datum = '$row[2]' AND zeit = '$row[1]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
					$sth3->execute();
				}
			}
			my $CTIME_String = localtime(time);
			if ($erstattung > 0) {
				geldbewegung($id, $erstattung, "Erstattung wegen Terminausfalls (Sperrung)");
				$nachricht = $nachricht."<br>".encode("utf-8", "$CTIME_String: Du wurdest gesperrt. Deine Termine wurden storniert.");
			} else {
				$nachricht = $nachricht."<br>".encode("utf-8", "$CTIME_String: Du wurdest gesperrt.");
			}
		}
		if ($pw ne "pwchange") {
			$change = "";
		} else {
			
			$pw = genPw();
			printFehler("<br>Es wurde folgendes Passwort generiert: <b>$pw</b> <br>");
			$pw = crypt($pw, "ps");
			$change = " pw='$pw' ,";
			printFehler("Passwort ge&auml;ndert!");
		}
		my $sql = "UPDATE users SET name='$name' , nachname='$nname' ,$change login='$login' , zimmer='$zimmer' , gesperrt=$sperre , message='$nachricht' , ip='$ip' , status='$status', bemerkung='$bemerkung' , von='$gId', termine='$termine' WHERE id='$id'";
		$sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		printFehler("Der User wurde erfolgreich ge&auml;ndert!");
	} else {
		gibEditForm($id, encode("utf-8", $login), encode("utf-8", $name), encode("utf-8", $nname), $status, $zimmer, $ip, $sperre, encode("utf-8", $nachricht), encode("utf-8", $bemerkung));
	}
	$dbh->disconnect;
}


# ----- Ein-/Auszahlung, Überweisung -----

sub manage_money {
	if(sperrCheck()==1) { return; }
	my $id = $cgi->url_param('id');
	my $sth = $dbh->prepare("SELECT login , name , nachname, status, zimmer FROM users WHERE id=$id")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	my @row2;
	print "<b>Usermodus (WaschAG-Mitglied - User)</b>";
	print "<table cellspacing=\"5\" cellpadding=\"3\">";
	normalTabellenZeile("black", "<b>Login</b>", $row[0]);
	normalTabellenZeile("black", "<b>Vorname</b>", $row[1]);
	normalTabellenZeile("black", "<b>Nachname</b>", $row[2]);
	normalTabellenZeile("black", "<b>Zimmer</b>", $row[4]);
	$sth = $dbh->prepare("SELECT bestand, bonus FROM finanzlog WHERE user=$id ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	if (@row2 = $sth->fetchrow_array) {
		normalTabellenZeile("black", "<b>aktuelles Guthaben</b>", printNumber($row2[0])." (+".printNumber($row2[1])." Bonus) Euro ");
	} else {
		normalTabellenZeile("black", "<b>aktuelles Guthaben</b>", "0 Euro");
	}
	print "<form action=\"$skript?aktion=admin_transaktion&id=$id\" method=\"post\">";
	normalTabellenZeile("black", "<b>Transaktion</b>", "Betrag: <input name=\"betrag\" size=\"4\">", "", "<input type=\"submit\" value=\" best&auml;tigen\">");
	print "</form>";
	print "<form action=\"$skript?aktion=storno&id=$id\" method=\"post\">";
	normalTabellenZeile("black", "<b>Kulanz</b>", "Betrag: <input name=\"betrag\" size=\"4\">", "Grund: <input name=\"grund\" size=\"40\">", "<input type=\"submit\" value=\" best&auml;tigen\">");
	print "</form></table>";

	if (($row[3] < $waschag) || ($gStatus < $admin)) {
		return;
	}

	if ($id != $gId) {
		print "<br><b>Kassenwartmodus (Kassenwart - WaschAG-Mitglied)</b>";
		print "<table cellspacing=\"5\" cellpadding=\"3\">";
		normalTabellenZeile("black", "<b>Login</b>", $row[0]);
		normalTabellenZeile("black", "<b>Vorname</b>", $row[1]);
		normalTabellenZeile("black", "<b>Nachname</b>", $row[2]);
		$sth = $dbh->prepare("SELECT bestand FROM waschagtransaktionen WHERE user=$id ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		if (@row = $sth->fetchrow_array()) {
			normalTabellenZeile("black", "<b>aktuelles Guthaben</b>", printNumber($row[0])." Euro");
		} else {
			normalTabellenZeile("black", "<b>aktuelles Guthaben</b>", "0 Euro");
		}
		print "<form action=\"$skript?aktion=god_transaktion&id=$id\" method=\"post\">";
		normalTabellenZeile("black", "<b>Transaktion</b>", "Betrag: <input name=\"betrag\" size=\"4\">");
		normalTabellenZeile("black", "<b>Zweck</b>", "<input name=\"zweck\" size=\"20\">", "<input type=\"submit\" value=\"Buchung best&auml;tigen\">");
		print "</table></form>";

		return;
	}

	print "<br><b>Kassenwartmodus (Kassenwart - Selbstentlastung)</b>";
	print "<table cellspacing=\"5\" cellpadding=\"3\">";
	normalTabellenZeile("black", "<b>Login</b>", encode("utf-8", $gLogin));
	normalTabellenZeile("black", "<b>Vorname</b>", encode("utf-8", $gName));
	normalTabellenZeile("black", "<b>Nachname</b>", encode("utf-8", $gNname));
	$sth = $dbh->prepare("SELECT bestand FROM waschagtransaktionen WHERE user=$id ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	if (@row = $sth->fetchrow_array()) {
		normalTabellenZeile("black", "<b>aktuelles Guthaben</b>", printNumber($row[0])." Euro");
	} else {
		normalTabellenZeile("black", "<b>aktuelles Guthaben</b>", "0 Euro");
	}
	print "<form action=\"$skript?aktion=self_transaktion\" method=\"post\">";
	normalTabellenZeile("black", "<b>Transaktion</b>", "<input name=\"betrag\" size=\"4\">");
	normalTabellenZeile("black", "<b>Zweck</b>", "<input name=\"zweck\" size=\"20\">", "<input type=\"submit\" value=\"Buchung best&auml;tigen\">");
	print "</table></form>";
}

# Transaktion, wenn sich jmd Geld zum Waschen ein-/auszahlen lässt
sub admin_transaktion {
	if(sperrCheck()==1) { return; }
	my $id = $cgi->url_param('id');
	my $betrag = $cgi->param('betrag');
	my $sth = $dbh->prepare("SELECT name, nachname, zimmer FROM users WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if ($betrag < 0) {
		$sth = $dbh->prepare("SELECT bestand FROM finanzlog WHERE user=$id ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		my @row3 = $sth->fetchrow_array();
		if ($row3[0] < (-1)*$betrag) {
			printFehler("Zu wenig Guthaben!");
			return;
		}
	} elsif ($betrag == 0) {
		printFehler("Bitte einen sinnvollen Betrag eingeben!");
		return;
	} elsif ($betrag < $minBetrag) {
		printFehler("Du musst mindestens $minBetrag Euro einzahlen!");
		return;
	} elsif ($betrag > $maxBetrag) {
		printFehler("Du darfst maximal $maxBetrag Euro einzahlen!");
		return;
	}
	if (isNumeric($betrag) == 1){
		my $bonus;
		if ($betrag >=  25) { $bonus = 1; }
		if ($betrag >=  50) { $bonus = 3;  }
		geldbewegung($id, $betrag, "Ein-/Auszahlung bei $gNname, $gName", $bonus);
		quittung($gId, $betrag, "Ein-/Auszahlung von $id (".decode("utf-8", $row[1]).", ".decode("utf-8", $row[0]).")(Zimmer: ".decode("utf-8", $row[2]).")");
		printFehler("Transaktion durchgef&uuml;hrt: $betrag (+$bonus Bonus) Euro auf das Waschkonto von ".decode("utf-8", $row[0])." ".decode("utf-8", $row[1])." &uuml;berwiesen");
	} else {
		printFehler("Es wurde ein ung&uuml;ltiger Betrag eingegeben. Abbruch der Transaktion.");
	}
}

# prüft Gültigkeit einer Stornierung und führt gegebenenfalls diese durch
sub storno {
	if(sperrCheck()==1) { return; }
	my $id = $cgi->url_param('id');
	my $grund = encode("utf-8", $cgi->param('grund'));
	if($grund eq "") {
		printFehler("Kein Grund angegeben!");
		return;
	}
	my $betrag = $cgi->param('betrag');
	my $sth = $dbh->prepare("SELECT MAX(preis) from preise")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if(isNumeric($betrag) == 0) {
		printFehler("Es wurde ein ung&uuml;ltiger Betrag eingegeben. Abbruch!");
		return;
	}
	if($betrag > 3 && $betrag > $row[0]) {
		printFehler("Es gibt keinen Waschtermin der derart teuer w&auml;re. Abbruch!");
		return;
	}
	if($betrag <= 0) {
		printFehler("Ja, da w&uuml;rde sich der Nutzer aber nicht so dr&uuml;ber freuen, ne? Also: Vergiss es! :-P");
		return;
	}
	if($id == $gId) {
		printFehler("Du kannst dir aus offensichtlichen Gr&uuml;den nicht selber Kulanz einr&auml;umen!");
		return;
	}
	geldbewegung($id, $betrag, "Kulanz von $gNname, $gName: $grund");
	printFehler("Kulanz gew&auml;hrt!");
}

# vermerkt Transaktionen für User
sub geldbewegung {
	if(sperrCheck()==1) { return; }
	my $user = shift;
	my $betrag = shift;
	my $zweck = shift;
	my $bonus = shift;
	#my $datum = gibDatumZeitString(0);
	my $bestand;
	my $bonusbestand;
	my $bestandsDatum;
	my $sth = $dbh->prepare("SELECT bestand, datum, bonus FROM finanzlog WHERE user='$user' ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	if ($row[0] ne '') {
		$bestand = $betrag + $row[0];
		$bestandsDatum = $row[1];
	} else {
		$bestand = $betrag;
		$bestandsDatum = "0000-00-00 00:00:00";
	}
	$bonusbestand = $bonus + $row[2];
	if( $row[2] eq '') { $bonusbestand = $bonus; }
	# vermeidet "doppelte Zeiten"
	$sth = $dbh->prepare("SELECT NOW()")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	while ($bestandsDatum eq $row[0]) {
		sleep(1);
		$sth = $dbh->prepare("SELECT NOW()")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
	}
	# ENDE vermeidet "doppelte Zeiten"
	$sth = $dbh->prepare("INSERT INTO finanzlog VALUES ('$user', '$bestand', '$betrag', '$zweck', NOW(), '$bonusbestand')")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute()|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor;
}

# vermerkt Transaktionen für Waschag-Mitglieder
sub quittung {
	if(sperrCheck()==1) { return; }
	my $user = shift;
	my $betrag = shift;
	my $zweck = shift;
	#my $datum = gibDatumZeitString(0);
	my $bestand;
	my $bestandsDatum;
	my $sth = $dbh->prepare("SELECT bestand, datum FROM waschagtransaktionen WHERE user='$user' ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	if ($row[0] ne '') {
		$bestand = $betrag + $row[0];
		$bestandsDatum = $row[1];
	} else {
		$bestand = $betrag;
		$bestandsDatum = "0000-00-00 00:00:00";
	}
	# vermeidet "doppelte Zeiten"
	$sth = $dbh->prepare("SELECT NOW()")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	while ($bestandsDatum eq $row[0]) {
		sleep(1);
		$sth = $dbh->prepare("SELECT NOW()")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
	}
	# ENDE vermeidet "doppelte Zeiten"
	$sth = $dbh->prepare("INSERT INTO waschagtransaktionen VALUES ('$user', '$bestand', '$betrag', '$zweck', NOW())")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
}

# Formular, um eine User-User-Überweisung anzulegen
sub ueberweisungsFormular {
	if(sperrCheck("&Uuml;berweisungsfunktion deaktiviert!")==1) { return; }
	print "<form action=\"$skript?aktion=ueberweisung\" method=\"post\">";
	print "<table cellspacing=\"5\" cellspacing=\"5\" cellpadding=\"5\">";
	normalTabellenZeile("black", "Login des Empf&auml;ngers:", "<input name=\"login\" size=\"40\">");
	normalTabellenZeile("black", "Zu &uuml;berweisender Betrag:", "<input name=\"betrag\" size=\"40\">");
	normalTabellenZeile("black", "Zweck:", "<input name=\"zweck\" size=\"40\" maxlength=\"60\">");
	normalTabellenZeile("black", "Passwort zum Best&auml;tigen:", "<input name=\"pw\" type=\"password\" size=\"40\">");
	print "</table><br><input type=\"submit\" value=\"Formulardaten absenden\">";
}

# führt die Überweisung aus
sub ueberweisung {
	if(sperrCheck("N&ouml; dein Geld bleibt erstmal hier...")==1) { return; }
	my $empfang = vorbereiten($cgi->param('login'));
	if(vorbereiten($gLogin) eq $empfang) {
		printFehler("Du kannst dir nicht selber &uuml;berweisen!");
		return;
	}
	my $betrag = $cgi->param('betrag');
	my $pw = $cgi->param('pw');
	#my $zweck = encode("utf-8", $cgi->param('zweck'));
	my $zweck = makeclean($cgi->param('zweck'));
	my @row;
	my @row2;
	my $sth;
	if (crypt($pw, "ps") ne cookie("wpw")) {
		printFehler("Passwort inkorrekt");
	} elsif (isNumeric($betrag) != 1 || $betrag < 0) {
		printFehler("Bitte einen g&uuml;ltigen Betrag eingeben!");
	} elsif ($betrag == 0) {
		printFehler("Du m&uuml;llst unsere Datenbank nicht zu, nein DU NICHT! ;-)");
	} else {
		$sth = $dbh->prepare("SELECT id, name, nachname FROM users WHERE login=$empfang")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		if (@row = $sth->fetchrow_array()) {
			my $id = $row[0];
			$sth = $dbh->prepare("SELECT bestand FROM finanzlog WHERE user='$gId' ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
			$sth->execute();
			if (@row2 = $sth->fetchrow_array()) {
				if ($row2[0] >= $betrag){
					geldbewegung($id, $betrag, "&Uuml;berweisung von $gNname, $gName (Zweck: $zweck)");
					geldbewegung($gId, (-1) * $betrag, "&Uuml;berweisung an ".decode("utf-8", $row[2]).", ".decode("utf-8", $row[1])." (Zweck: $zweck)");
					printFehler("&Uuml;berweisung erfolgreich ausgef&uuml;hrt!");
				} else {
					printFehler("Nicht genug Guthaben!");
				}
			} else {
				printFehler("Nicht genug Guthaben!");
			}
		} else {
			printFehler("Zieluser unbekannt!");
		}
	}
}

# Transaktion zwischen Wasch-AG Mitglied und Kassenwart
sub god_transaktion {
	if(sperrCheck()==1) { return; }
	my $id = $cgi->url_param('id');
	my $betrag = $cgi->param('betrag');
	my $zweck = makeclean($cgi->param('zweck'));
	$zweck = makeclean($zweck);
	my $sth = $dbh->prepare("SELECT name, nachname FROM users WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	if (isNumeric($betrag) == 1){
		quittung($id, $betrag, "Ein-/Auszahlung bei $gNname, $gName (Zweck: $zweck)");
		quittung($gId, (-1)*$betrag, "Ein-/Auszahlung von ".decode("utf-8", $row[1]).", ".decode("utf-8", $row[0])." (Zweck: $zweck)");
		printFehler("Transaktion durchgef&uuml;hrt");
	} else {
		printFehler("Es wurde ein ung&uuml;ltiger Betrag eingegeben. Abbruch der Transaktion.");
	}
}

# Selbstentlastung Kassenwart
sub self_transaktion {
	if(sperrCheck()==1) { return; }
	my $betrag = $cgi->param('betrag');
	my $zweck = makeclean($cgi->param('zweck'));
	$zweck = makeclean($zweck);
	if (isNumeric($betrag) == 1){
		quittung($gId, $betrag, "Selbstent-/belastung Kassenwart $gNname, $gName (Zweck: $zweck)");
		printFehler("Selbstent-/belastung eingetragen!");
	} else {
		printFehler("Es wurde ein ung&uuml;ltiger Betrag eingegeben. Abbruch der Transaktion.");
	}
}

# ----- ENDE EIN-/AUSZAHLUNG, ÜBERWEISUNG -----


# ----- KONTOFÜHRUNG -----

sub kontoAuszug {
	my $sth = $dbh->prepare("SELECT datum, bemerkung, aktion, bestand, bonus FROM finanzlog WHERE user='$gId' ORDER BY datum ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row;
	if (@row = $sth->fetchrow_array) {
		my @temp = @row;
		print "<br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
		print "Dein Kontostand am ".substr($row[0],0,10)." um ".substr($row[0],11,8)." Uhr betrug ".printNumber($row[3])." (+".printNumber($row[4])." Bonus) Euro.";
		print "</th></tr></table><br><br>";
		print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
		normalTabellenZeileKopf("black", "Datum", "Erl&auml;uterung", "Betrag<br>(Euro)", "Bestand nachher<br>(Euro)","Bonus nachher<br>(Euro)");
		while (@row = $sth->fetchrow_array){
			@temp = @row;
			if ($row[2] >= 0) {
				normalTabellenZeile("black", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]), printNumber($row[4]));
			} else {
				normalTabellenZeile("red", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]), printNumber($row[4]));
			}
		}
		print "</table><br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
		print "Dein aktueller Kontostand betr&auml;gt ".printNumber($temp[3])." (+".printNumber($temp[4])." Bonus) Euro.";
		print "</th></tr></table><br><br>";
	} else {
		print "<br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
		print "Keine Kontoinformationen vorhanden.";
		print "</th></tr></table><br><br>";
	}
	if($gStatus >= $waschag) {
		$sth = $dbh->prepare("SELECT datum, bemerkung, aktion, bestand FROM waschagtransaktionen WHERE user='$gId' ORDER BY datum ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		my @row;
		if (@row = $sth->fetchrow_array) {
			my @temp = @row;
			print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
			print "----------------------------------------<br><br><br><br>";
			print "Dein WaschAG-Kontostand am ".substr($row[0],0,10)." um ".substr($row[0],11,8)." Uhr betrug ".printNumber($row[3])." Euro.";
			print "</th></tr></table><br><br>";
			print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
			normalTabellenZeileKopf("black", "Datum", "Erl&auml;uterung", "Betrag<br>(Euro)", "Bestand nachher<br>(Euro)");
			while (@row = $sth->fetchrow_array){
				@temp = @row;
				if ($row[2] >= 0) {
					normalTabellenZeile("black", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]));
				} else {
					normalTabellenZeile("red", $row[0], $row[1], printNumber($row[2]), printNumber($row[3]));
				}
			}
			print "</table><br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
			print "Dein aktueller Kontostand betr&auml;gt ".printNumber($temp[3])." Euro.";
			print "</th></tr></table><br><br>";
		} else {
			print "<br><table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\"><tr><th>";
			print "Keine Kontoinformationen vorhanden.";
			print "</th></tr></table><br><br>";
		}
	}
}

# ----- ENDE KONTOFÜHRUNG -----



# ----- Statistik -----

#gibt dolle Statistiken aus
sub statistik {
	# wie viele User
	my $sth = $dbh->prepare("SELECT count(*) FROM users WHERE status < $god")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row;
	@row = $sth->fetchrow_array();
	my $anzahlLeute = $row[0];

	# heute online gewesen
	$sth = $dbh->prepare("SELECT count(*) FROM users WHERE status < $god AND lastlogin=DATE(NOW())")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlOnline = int($row[0]);

	# Sperren
	$sth = $dbh->prepare("SELECT count(*) FROM users WHERE status < $god AND gesperrt = 1")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlSperre = int($row[0]);

	# Etagenverteilung
	$sth = $dbh->prepare("SELECT zimmer FROM users WHERE status < $god")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @etage;
	for (my $i = 1; $i <= 15; $i++) {
		$etage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[0] - $row[0]%100)/100;
		$etage[$temp] += 1;
	}

	# wie viele Termine
	$sth = $dbh->prepare("SELECT count(*) FROM termine")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlTermine = $row[0];

	# wie viele Termine
	$sth = $dbh->prepare("SELECT count(*) FROM termine WHERE wochentag = 8")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlGoodTermine = $row[0];

	# Geld bei Nutzen nach Etage
	my @etagenGeld;
	for (my $i = 1; $i <= 15; $i++) {
		$etagenGeld[$i] = 0;
	}
	$sth = $dbh->prepare("SELECT id, zimmer FROM users WHERE status < $waschag")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my $sth2;
	my @row2;
	my $finanzSumme = 0;
	my $waschFinanz = 0;
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[1]%100)/100;
		$sth2 = $dbh->prepare("SELECT bestand FROM finanzlog WHERE user=$row[0] ORDER BY datum DESC LIMIT 1")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth2->execute();
		@row2 = $sth2->fetchrow_array();
		$etagenGeld[$temp] += $row2[0];
	}

	# Geld bei den Nutzern und der AG
	$sth = $dbh->prepare("SELECT id FROM users WHERE status < $god")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	$finanzSumme = 0;
	$waschFinanz = 0;
	while (@row = $sth->fetchrow_array()) {
		$sth2 = $dbh->prepare("SELECT bestand FROM finanzlog WHERE user=$row[0] ORDER BY datum DESC LIMIT 1")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth2->execute();
		@row2 = $sth2->fetchrow_array();
		$finanzSumme += $row2[0];
		$sth2 = $dbh->prepare("SELECT bestand FROM waschagtransaktionen WHERE user=$row[0] ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth2->execute();
		@row2 = $sth2->fetchrow_array();
		$waschFinanz += $row2[0];
	}

	# Ausgabe
	print "<b>Userstatistiken</b><br>";
	print "Es sind derzeit <b>$anzahlLeute</b> User angemeldet. <br> Davon waren heute schon <b>$anzahlOnline</b> Leute online. <br>Derzeit sind <b>$anzahlSperre</b> <a href=\"$skript?aktion=look_banned_poopies&sort=id%20ASC\">b&ouml;se Jungs und M&auml;dels</a> gesperrt.<br><br>";
	print "<b>Terminstatistiken</b><br>";
	print "Es sind derzeit <b>$anzahlTermine</b> Termin(e) gebucht.<br>";
	print "Davon wurden bereits <b>$anzahlGoodTermine</b> Termin(e) wahrgenommen.<br><br>";
	print "<b>Finanzstatistiken</b><br>";
	print "Die Barschaft der Wasch-AG bel&auml;uft sich auf stolze <b>$waschFinanz Euro</b>.<br>";
	print "Alle User besitzen zusammen <b>$finanzSumme Euro</b>.<br>Damit besitzt jeder im Durchschnitt <b>".((int($finanzSumme/$anzahlLeute * 100))/100)." Euro</b>.<br>";
	print "<br><b>Und nun alle Etagen im Vergleich:</b>";
	print "<table border=\"0\" align=\"center\" cellspacing=\"10\" cellpadding=\"6\"><tr align=\"center\"><th>Etage</th><th>|</th><th>User</th><th>prozentual</th><th>|</th><th>Kapital</th><th>prozentual</th><th>pro User</th><th>Anteil vom Durchschnitt</th></tr>";
	my $anteil;
	my $prozAnteil;
	my $wohnprozent;
	for (my $i = 1; $i <= 15; $i++) {
		$wohnprozent = (int($etage[$i]/$anzahlLeute * 10000))/100;
		$prozent = (int($etagenGeld[$i]/$finanzSumme * 10000))/100;
		if ($etage[$i] == 0) {
			$anteil = 0;
			$prozAnteil = 0;
		} else {
			$anteil = (int($etagenGeld[$i]/$etage[$i] * 100))/100;
			$prozAnteil = (int($anteil/($finanzSumme/$anzahlLeute) * 10000))/100;
		}
		print "<tr align=\"center\"><td>".$i."te</td><td></td><td>$etage[$i]</td><td>$wohnprozent %</td><td></td><td>$etagenGeld[$i]</td><td>$prozent %</td><td>$anteil</td><td>$prozAnteil %</td></tr>";
	}
	print "</table>";
}

sub look_banned_people {
	if(sperrCheck()==1) { return; }
	my $sortierung = $cgi->url_param('sort');
	my $sth = $dbh->prepare("SELECT id, nachname, name, login, zimmer, bemerkung, lastlogin, ip FROM users WHERE gesperrt=1 ORDER BY $sortierung")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row;
	print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
	#print "<colgroup>
	normalTabellenZeileKopf("black",
								"id<br><a href=\"$skript?aktion=look_banned_poopies&sort=id%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=id%20DESC\">&gt;</a>",
								"Nachname<br><a href=\"$skript?aktion=look_banned_poopies&sort=nachname%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=nachname%20DESC\">&gt;</a>",
								"Name<br><a href=\"$skript?aktion=look_banned_poopies&sort=name%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=name%20DESC\">&gt;</a>",
								"Login<br><a href=\"$skript?aktion=look_banned_poopies&sort=login%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=login%20DESC\">&gt;</a>",
								"Zimmer<br><a href=\"$skript?aktion=look_banned_poopies&sort=zimmer%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=zimmer%20DESC\">&gt;</a>",
								"Bemerkung<br><a href=\"$skript?aktion=look_banned_poopies&sort=status%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=status%20DESC\">&gt;</a>",
								"Letzter Login<br><a href=\"$skript?aktion=look_banned_poopies&sort=lastlogin%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=lastlogin%20DESC\">&gt;</a>",
								"IP<br><a href=\"$skript?aktion=look_banned_poopies&sort=ip%20ASC\">&lt;</a><a href=\"$skript?aktion=look_banned_poopies&sort=ip%20DESC\">&gt;</a>");
	while (@row = $sth->fetchrow_array) {
		BannedTabellenZeile(5,"black", @row);
	}
	print "</table>";
	$dbh->disconnect;
}


# ----- ENDE STATISTIK -----


# ----- FIREWALL FUNKTIONEN -----

sub notifyVerwaltung {
	if(sperrCheck()==1) { return; }
	#holen der Daten
	$sortierung = $cgi->url_param('sort');
	my $sth = $dbh->prepare("SELECT id, (SELECT nachname FROM users where id=notify.id), (SELECT name FROM users where id=notify.id), ziel, datum FROM notify ORDER BY $sortierung")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();	# führt den befehl aus
	my @row;
	print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
	normalTabellenZeileKopf("black",
								"User id<br><a href=\"$skript?aktion=notify_management&sort=id%20ASC\">&lt;</a> <a href=\"$skript?aktion=notify_management&sort=id%20DESC\">&gt;</a>",
								"Zugriffsversuch auf<br><a href=\"$skript?aktion=notify_management&sort=ziel%20ASC\">&lt;</a> <a href=\"$skript?aktion=notify_management&sort=ziel%20DESC\">&gt;</a>",
								"Datum<br><a href=\"$skript?aktion=notify_management&sort=datum%20ASC\">&lt;</a> <a href=\"$skript?aktion=notify_management&sort=datum%20DESC\">&gt;</a>");
	while (@row = $sth->fetchrow_array) {
			normalTabellenZeile("black", $row[1].", ".$row[2]." (id: $row[0])", $row[3], $row[4]);
	}
	print "</table>";
	$dbh->disconnect;
}

# ----- ENDE FIREWALL FUNKTIONEN -----


# ----- KONFIGURATIONSTEIL -----

# Zeigt die Verwaltungsseite an
sub maschinenVerwaltung {
	if(sperrCheck()==1) { return; }
	#holen der Daten
	my $sth = $dbh->prepare("SELECT id, status, bemerkung, (SELECT nachname FROM users where id=waschmaschinen.von), (SELECT name FROM users where id=waschmaschinen.von) FROM waschmaschinen")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();	# führt den befehl aus
	my @row;
	print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
	normalTabellenZeileKopf("black",
								"id",
								"betriebsbereit",
								"Bemerkung",
								"zuletzt ge&auml;ndert von");
	while (@row = $sth->fetchrow_array) {
		print "<form action=\"$skript?aktion=set_waschmaschinen&id=$row[0]\" method=\"post\">";
		my $sperre;
		if ($row[1] == 1) {
			$sperre = "<input type=\"checkbox\" name=\"betrieb\" value=\"betriebsbereit\" checked=\"checked\">";
		} else {
			$sperre = "<input type=\"checkbox\" name=\"betrieb\" value=\"betriebsbereit\">";
		}
		my $bemerkung = "<textarea name=\"bemerkung\" cols=\"40\" rows=\"3\">$row[2]</textarea>";
		my $button = "<input type=\"submit\" value=\"&auml;ndern\"></p></form>";
		if ($row[1] == 0) {
			normalTabellenZeile("red", $row[0], $sperre, $bemerkung, $row[3].", ".$row[4], $button);
		} else {
			normalTabellenZeile("black", $row[0], $sperre, $bemerkung, $row[3].", ".$row[4], $button);
		}
		print "</font>";
	}
	print "</table><br><br><br>";
	if ($gStatus >= $god) {
		$sth = $dbh->prepare("SELECT zweck FROM config ORDER BY zweck ASC")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();	# führt den befehl aus
		my @contents;
		my @werte;
		my $i = 0;
		print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
		while (@row = $sth->fetchrow_array()) {
			$contents[$i] = $row[0];
			$i++;
		}
		$sth = $dbh->prepare("SELECT wert FROM config ORDER BY zweck ASC")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();	# führt den befehl aus
		normalTabellenZeileKopf("black", @contents);
		print "<form action=\"$skript?aktion=set_config\" method=\"post\">";
		@row = $sth->fetchrow_array();
		my $antritt = "<input name=\"antritt\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $freigeld = "<input name=\"freigeld\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $miniGeld = "<input name=\"miniGeld\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $relais = "<input name=\"relais\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $storn = "<input name=\"storn\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $monat = "<input name=\"tpromonat\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $vorhalte = "<input name=\"vorhalte\" size=\"10\" value=\"$row[0]\">";
		@row = $sth->fetchrow_array();
		my $WAGvorhalte = "<input name=\"WAGvorhalte\" size=\"10\" value=\"$row[0]\">";
		my $button = "<input type=\"submit\" value=\"&auml;ndern\"></p></form>";
		normalTabellenZeile("black", $antritt, $freigeld, $miniGeld, $relais, $storn, $monat, $vorhalte, $WAGvorhalte, $button);
		print "</table>";
	}
}

# Setzt die Änderungen für Waschmaschinen
sub maschineSetConfig {
	if(sperrCheck()==1) { return; }
	my $W_Id = shift;
	my $betrieb = $cgi->param('betrieb');
	my $bemerkung = $cgi->param('bemerkung');
	my $ok = 1;
	my $verschoben = 0;
	if ($betrieb eq "betriebsbereit") {
		$betrieb = vorbereiten(1);
	} else {
		$betrieb = vorbereiten(0);
		my $erstattung = 0;
		#$sperre = vorbereiten(1);
		my $sth = $dbh->prepare("SELECT wochentag, zeit, user, datum FROM termine WHERE maschine ='$W_Id' AND wochentag != 8")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		while (@row = $sth->fetchrow_array()){
			if (wieLangNoch($row[1],$row[3]) > 0) {
				for(my $i = 1; $i <= $anzahlMaschinen && $verschoben == 0; $i++) {
					if($i != $W_Id) {
						my $sql = $dbh->prepare("SELECT * FROM termine WHERE maschine = '$i' AND datum = '$row[3]' AND zeit = '$row[1]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			  		$sql->execute();
			  		my @row2 = $sql->fetchrow_array();
			  		if(scalar(@row2) == 0) {
			  			$sql = $dbh->prepare("SELECT status FROM waschmaschinen WHERE id = '$i'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			  			$sql->execute();
			  			@row2 = $sql->fetchrow_array();
			  			if ($row2[0] == 1){
			  				my $sql = $dbh->prepare("UPDATE termine SET maschine='$i' WHERE maschine = '$W_Id' AND datum = '$row[3]' AND zeit = '$row[1]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			  		  	$sql->execute();
			  		  	benachrichtige($row[2], "Ein Termin von dir wurde auf eine andere Maschine verlegt. Bitte beachten!");
			  		  	$verschoben = 1;
			  		  }
			  		}
			  	}
			  }
		  	if($verschoben == 0) {
		  		my $preis = getPreis($row[0], $row[1]);
					geldbewegung($row[2], $preis, "Erstattung wegen Terminausfalls (Sperrung Maschine $W_Id)");
					benachrichtige($row[2], "Ein Termin von dir wurde storniert. Bitte beachten!");
					my $sth2 = $dbh->prepare("UPDATE users SET termine = termine - 1 WHERE id = '$row[2]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
					$sth2->execute();
					sleep(1);
				} else {
					$verschoben = 0;
				}
				my $sth2 = $dbh->prepare("DELETE FROM termine WHERE maschine ='$W_Id' AND datum = '$row[3]' AND zeit = '$row[1]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth2->execute();
			}
		}
	}
	my $sql = "UPDATE waschmaschinen SET status=$betrieb , bemerkung='$bemerkung' , von='$gId' WHERE id=$W_Id";
	my $sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	printFehler("Waschmaschinenstatus aktualisiert!");
	$dbh->disconnect;
}

# Setzt die allgemeinen Änderungen
sub set_config {
	if(sperrCheck()==1) { return; }
	my $storn = $cgi->param('storn');
	my $antritt = $cgi->param('antritt');
	my $relais = $cgi->param('relais');
	my $miniGeld = $cgi->param('miniGeld');
	my $tProMonat = $cgi->param('tpromonat');
	my $freigeld = $cgi->param('freigeld');
	my $vorhalte = $cgi->param('vorhalte');
	my $WAGvorhalte = $cgi->param('WAGvorhalte');
	my $ok = 1;
	if (isNumeric($storn) == 0 && isNumeric($antritt) == 0 && isNumeric($miniGeld) == 0 && isNumeric($tproTag) == 0 && isNumeric($tProMonat) == 0 && isNumeric($freigeld) == 0) {
		printFehler("Unerlaubtes Zeichen eingegeben. Nur Ziffern und '.' erlaubt!");
		$ok = 0;
	}
	if ($storn < 0 || $antritt < 0 || $miniGeld < 0 || $tproTag < 0 || $tProMonat < 0 || $freigeld < 0) {
		printFehler("Negative Werte machen doch keinen Sinn! Abbruch...");
		$ok = 0;
	}
	if ($ok == 1) {
		my $sth = $dbh->prepare("UPDATE config SET wert='$storn' WHERE zweck='Stornierzeit (in Min)'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$antritt' WHERE zweck='Antrittszeit (in Min)'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$relais' WHERE zweck='Relaiszeit (in Min)'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$miniGeld' WHERE zweck='minimaler Einzahlbetrag (in Euro)'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$tProMonat' WHERE zweck='Termine pro Monat'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$freigeld' WHERE zweck='Freigeld fuer WaschAG'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$vorhalte' WHERE zweck='Vorhaltezeit Kontodaten (in Monaten)'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		$sth = $dbh->prepare("UPDATE config SET wert='$WAGvorhalte' WHERE zweck='Vorhaltezeit WAG-Kontodaten (in Monaten)'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		printFehler("Konfiguration aktualisiert.");
	} else {
		printFehler("Aktion abgebrochen!");
	}
}

# Zeigt das Formular zum Ändern der Preise an
sub preisListe {
	if(sperrCheck()==1) { return; }
	my @row;
	print "<table><tr>";
	print "<form action=\"$skript?aktion=set_einheits_preis\" method=\"post\">";
	print "<td align=\"center\">Einheitspreis auf&#160&#160&#160<input name=\"T\" size=\"4\"> Euro&#160&#160&#160<input type=\"submit\" value=\"setzen\"></td></tr></table></form>";

	print "<form action=\"$skript?aktion=set_preis\" method=\"post\">";
	print "<table cellspacing=\"10\" cellpadding=\"5\" width=\"100%\">";
	print "<tr><th>Zeit</th><th>Montag</th><th>Dienstag</th><th>Mittwoch</th><th>Donnerstag</th><th>Freitag</th><th>Samstag</th><th>Sonntag</th></tr>";
	for (my $i = 0; $i <= 15; $i++) {
		print "<tr><th>".gibWaschTermin($i)."</th>";
		my $sth = $dbh->prepare("SELECT preis FROM preise WHERE zeit = '$i'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		for (my $k = 0; $k <= 6; $k++) {
			@row = $sth->fetchrow_array();
			print "<td align=\"center\"><input name=\"T$k$i\" size=\"4\" value=\"$row[0]\"> Euro</td>";
		}
		print "</tr>";
	}
	print "</table><br><p><input type=\"submit\" value=\"Preise &auml;ndern\"></p></form>";
}

# Ändert die Preise individuell
sub set_preis {
	if(sperrCheck()==1) { return; }
	my @preis;
	my $ok = 1;
	my @Feldnamen = $cgi->param();
	my $l = 0;
	my $j = 0;
	foreach (@Feldnamen) {
		$preis[$l++][$j] = $cgi->param($_);
		if ($l == 7) {
			$l = 0;
			$j++;
		}
	}
	for (my $i = 0; $i <= 15; $i++) {
		for (my $k = 0; $k <= 6; $k++) {
			if (isNumeric($preis[$k][$i]) == 0) {
				$ok = 0;
			}
		}
	}
	if ($ok == 1) {
		for (my $i = 0; $i <= 15; $i++) {
			for (my $k = 0; $k <= 6; $k++) {
				my $sth = $dbh->prepare("UPDATE preise SET preis='$preis[$k][$i]' WHERE zeit = '$i' AND tag = '$k'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth->execute();
			}
		}
		printFehler("Preise ge&auml;ndert.");
	} else {
		printFehler("Aktion abgebrochen!");
	}
}

# Setzt einen Einheitspreis
sub set_einheits_preis {
	if(sperrCheck()==1) { return; }
	my $preis = $cgi->param('T');
	my $ok = 1;
	if (isNumeric($preis) == 0) {
		printFehler("Unerlaubtes Zeichen eingegeben. Nur Ziffern und maximal ein '.' erlaubt!");
		$ok = 0;
	}
	if ($ok == 1) {
		my $sth = $dbh->prepare("UPDATE preise SET preis='$preis'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		printFehler("Preise ge&auml;ndert.");
	} else {
		printFehler("Aktion abgebrochen!");
	}
}

# Ermittelt Preis von Tag und Zeit
sub getPreis {
	if(sperrCheck()==1) { return; }
	my $tag = shift;
	my $zeit = shift;
	my $sth = $dbh->prepare("SELECT preis FROM preise WHERE tag = ".gibTag($tag)." AND zeit = '$zeit'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	return ($row[0]);
}

# ----- ENDE KONFIGURATIONSTEIL -----



# ----- ANFANG BUCHUNGEN -----

# erstellt die Auswahlliste zum Buchen eines Termins
sub look_termine {
	if ($gSperre == 1){
		printFehler("<b>Da du gesperrt bist, darfst du auch keine Termine buchen!</b>");
	}
	my @row;
	my @row2;
	my $sth2;
	# ermittelt Status der Maschinen
	my $sth = $dbh->prepare("SELECT status FROM waschmaschinen ORDER BY id ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @maschine;
	for (my $count = 0; my @m0 = $sth->fetchrow_array(); $count++) {
		$maschine[$count] = $m0[0];
	}
	# Start Formular
	print "Link f&uuml;r den iCal-Export aufs Smartphone: <a href=\"https://www.tvk.rwth-aachen.de/~waschag/terminexport.php?id=$terminhash\">https://www.tvk.rwth-aachen.de/~waschag/terminexport.php?id=$terminhash</a>";
	print "<table cellspacing=\"10\" cellpadding=\"0\" width=\"100%\"><colgroup>";
	print "<col width=\"9%\"><col width=\"13%\"><col width=\"13%\"><col width=\"13%\">";
	print "<col width=\"13%\"><col width=\"13%\"><col width=\"13%\"><col width=\"13%\">";
	print "<tr><th>Zeit</th>";
	for (my $i = 0; $i <= 6; $i++) {
		print "<th align=\"center\">".gibTagText($i)."</th>";
	}
	print "</tr>";
	for (my $i = 0; $i <= 15; $i++) {
		print "\n<tr><th>".gibWaschTermin($i)."</th>";
		for (my $k = 0; $k <= 6; $k++) {
			print "\n<td align=\"center\">";
			my $datum = gibDatumString($k);
			$sth = $dbh->prepare("SELECT user, zeit, maschine, datum, wochentag FROM termine WHERE zeit = '$i' AND datum = '$datum' ORDER BY maschine ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
			$sth->execute();
			@row = $sth->fetchrow_array();
			# Unterscheidung ob Maschine defekt, Termin vergeben oder Termin frei und buchbar
			if ($gStatus >= $waschag) {
				for (my $l = 0; $l < $anzahlMaschinen; $l++) {
					if (wieLangNoch($i,$datum) < 0) {
						if (($l+1) ne $row[2]) {
							print "<font color=\"#ff0000\">vorbei</font>";
						} else {
							$sth2 = $dbh->prepare("SELECT zimmer FROM users WHERE id = '$row[0]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
							$sth2->execute();
							@row2 = $sth2->fetchrow_array();
							if ($row[4] == 8) {
								print "<b><font color=\"#0000ff\">".sprintf("%04d",$row2[0])."</font></b>";
							} else {
								print "<b><font color=\"#9d5029\">".sprintf("%04d",$row2[0])."</font></b>";
							}
							@row = $sth->fetchrow_array();
						}
					} else {
						if ($maschine[$l] == 0){
							print "<font color=\"#ff0000\">M".($l+1)." ist defekt</font>";
						} elsif (($l+1) ne $row[2]) {
							print "<a class=\"green\" href=\"$skript?aktion=buchen&maschine=".($l+1)."&datum=$k&zeit=$i&confirm=no\">M".($l+1)." buchen</a>";
						} else {
							$sth2 = $dbh->prepare("SELECT zimmer FROM users WHERE id = '$row[0]'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
							$sth2->execute();
							@row2 = $sth2->fetchrow_array();
							print "<b><font color=\"#9d5029\">".sprintf("%04d",$row2[0])."</b>";
							@row = $sth->fetchrow_array();
						}
					}
					if ($l <= 1) {
						print "<br>";
					}
				}
			} else {
				if (wieLangNoch($i,$datum) < 0) {
						print "<font color=\"#ff0000\">Termin vorbei";
				} else {
					for (my $l = 0; $l < $anzahlMaschinen; $l++) {
						if ($maschine[$l] == 0){
							print "<font color=\"#ff0000\">M".($l+1)." ist defekt</font>";
						} elsif (($l+1) ne $row[2]) {
							print "<a class=\"green\" href=\"$skript?aktion=buchen&maschine=".($l+1)."&datum=$k&zeit=$i&confirm=no\">M".($l+1)." buchen</a>";
						} else {
							print "<font color=\"#ff0000\">M".($l+1)." besetzt";
							@row = $sth->fetchrow_array();
						}
						if ($l <= 1) {
							print "<br>";
						}
					}
				}
			}
			
		}
		print "</tr>";
	}
	print "<tr><th>Zeit</th>";
	for (my $i = 0; $i <= 6; $i++) {
		print "<th align=\"center\">".gibTagText($i)."</th>";
	}
	print "</tr>";
	print "</table>";
}

# Bucht einen Termin
sub bucheTermin {
	if(sperrCheck("Buchung fehlgeschlagen. Ich habs dir doch gesagt!")==1) { return; }
	my $maschine = $cgi->url_param('maschine');
	my $zeit = $cgi->url_param('zeit');
	my $confirm = $cgi->url_param('confirm');
	my $tag = $cgi->url_param('datum');
	my $datum = gibDatumString($tag);
	my $wochentag = gibTag($tag);
	my @row;

	if ($tag > 6) {
		printFehler("Du darfst nicht so weit im Voraus buchen!");
		return;
	}

	if ($tag < 0 || wieLangSchon($zeit,$datum) > 0) {
		printFehler("Ach ja, du m&ouml;chtest in der Vergangenheit buchen... Vergiss es!");
		return;
	}

	if ($zeit > 15 || $zeit < 0) {
		printFehler("Das ist kein g&uuml;ltiger Waschtermin!");
		return;
	}

	if (checkeTermin($maschine, $datum, $zeit) == 0) {
		return;
	}

	my $preis = getPreis($tag, $zeit);

	#frei Waschen für WaschAG
#	if ($gStatus >= $waschag) {
#		$preis = 0;
#	}

	if ($confirm ne 'yes') {
		print "<a href=\"$skript?aktion=buchen&maschine=$maschine&datum=$tag&zeit=$zeit&confirm=yes\">";
		print "Klicke hier um den folgenden Termin zu buchen<br><br>".gibTagText($tag).", $datum um ".gibWaschTermin($zeit)." Uhr<br><br>";
		print "Dabei werden von deinem Konto <b>$preis Euro</b> abgebucht.</a>";
		return;
	}
	my @MaxTerminZahl = TagTerminZahlUeberschritten($datum);
	if ($MaxTerminZahl[0] == 0) {
		my @MaxTerminZahl = MonatTerminZahlUeberschritten($datum);
		if ($MaxTerminZahl[0] == 0) {
			if (wieLangSchon($zeit,$datum) < 0) {
				my $res = geldAbbuchen($preis, $datum, $zeit, $tag);
				if ($res > 0) {
					$sth = $dbh->prepare("INSERT INTO termine VALUES ('$gId', '$zeit', '$maschine', '$datum', '".gibTag($tag)."', ".(($res == 1)?0:1).")")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
					$sth->execute();
					$sth = $dbh->prepare("UPDATE users SET termine = termine + 1 WHERE id = '$gId'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
					$sth->execute();
					printFehler("Termin erfolgreich gebucht!");
					return;
				} else {
					printFehler("Du hast nicht genug Geld!");
					return;
				}
			} else {
				printFehler("Der Termin ist doch bereits vorbei! Buchung abgebrochen!");
				return;
			}
		} else {
			printFehler("Du darfst maximal $MaxTerminZahl[1] Termine pro Monat haben!");
			return;
		}
	} else {
		printFehler("Du darfst maximal $MaxTerminZahl[1] Termine pro Tag haben!");
	}
}

# Stellt Zahlungsfähigkeit fest und bucht ggf ab
sub geldAbbuchen {
	my $preis = shift;
	my $datum = shift;
	my $zeit = shift;
	my $tag = shift;
	my $sth = $dbh->prepare("SELECT bestand, bonus FROM finanzlog WHERE user='$gId' ORDER BY datum DESC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if($row[1] >= $preis) {
		geldbewegung($gId, 0, "Buchung Waschtermin am ".gibTagText($tag).", $datum um ".gibWaschTermin($zeit)." Uhr von Bonusguthaben", (-1)*$preis);
		return (2);
	}
	if ($row[0] < $preis) {
		return (0);
	} else {
		geldbewegung($gId, (-1)*$preis, "Buchung Waschtermin am ".gibTagText($tag).", $datum um ".gibWaschTermin($zeit)." Uhr");
		return (1);
	}
}

# Stellt fest ob ein Termin noch frei ist
sub checkeTermin {
	my $maschine = shift;
	my $datum = shift;
	my $zeit = shift;
	my $sth = $dbh->prepare("SELECT * FROM termine WHERE maschine = '$maschine' AND datum = '$datum' AND zeit = '$zeit'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if (scalar(@row) != 0){
		printFehler("Termin bereits vergeben!");
		return (0);
	}
	return (1);
}

# Ermittelt, ob der User am betreffenden Tag noch buchen darf
sub TagTerminZahlUeberschritten {
	my $datum = shift;
	my $count;
	$sth = $dbh->prepare("SELECT * FROM termine WHERE datum = '$datum' AND user = '$gId'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	$count = 0;
	if ($gStatus == $god) {
		return (0);
	}
	while (my @row = $sth->fetchrow_array()) {
		$count++;
	}
	if ($count >= $termPerDay) {
		return (1, $termPerDay);
	} else {
		return (0);
	}
}

# Ermittelt, ob der User am betreffenden Tag noch buchen darf
sub MonatTerminZahlUeberschritten {
	my $datum = shift;
	my $count;
	if ($gStatus == $god) {
		return (0);
	}
	$sth = $dbh->prepare("SELECT termine FROM users WHERE id = '$gId'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if ($row[0] >= $termPerMonth) {
		return (1, $termPerMonth);
	} else {
		return (0);
	}
}

# storniert einen bestimmten Termin
sub stornieren {
	if(sperrCheck()==1) { return; }
	$datum = shift;
	$zeit = shift;
	$maschine = shift;
	my $sth = $dbh->prepare("SELECT user, wochentag, bonus FROM termine WHERE datum = '$datum' AND zeit = '$zeit' AND maschine = '$maschine'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	if(my @row = $sth->fetchrow_array()){
		if($row[0] == $gId){
			if(wieLangNoch($zeit, $datum) < $stornTime) {
				printFehler("Du darfst nicht so kurzfristig stornieren (Min. $stornTime Minuten vorher)");
				return;
			} else {
				my $preis = getPreis($row[1], $zeit);
				my $bonuspreis = 0;
				if($row[2] != 0) 
				{
					# das ist ein bonustermin
					$bonuspreis = $preis;
					$preis = 0;
				}
				geldbewegung($gId, $preis, "Termin am ".gibTagTextOhneOffset($row[1]).", $datum um ".gibWaschTermin($zeit)." Uhr storniert", $bonuspreis);
				$sth = $dbh->prepare("DELETE FROM termine WHERE datum = '$datum' AND zeit = '$zeit' AND maschine = '$maschine'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth->execute();
				$sth = $dbh->prepare("UPDATE users SET termine = termine - 1 WHERE id = '$gId'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth->execute();
			}
		} else {
			printFehler("Das ist nicht dein Termin!");
		}
	} else {
		printFehler ("Zu diesem Zeitpunkt existiert gar kein Termin!");
	}
}

# ----- ENDE BUCHUNGSSYSTEM -----



# ----- DOKUSYSTEM -----

# Zeigt die Doku an
sub show_doku {
	my $sprache = shift;
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
					print "</$listtype>\n</li>";
				}
				print "<br></$listtype>\n</li>";
			}
			print "<li><b><a href=\"#$row[0].$row[1].$row[2]\">".print_chapter($row[0],$row[1],$row[2])." $row[3]</a></b>";
			print "<$listtype>";
			$paragraph++;
			$abschnitt = 0;
			$satz = 0;
		} elsif ($abschnitt < $row[1]) {
			#PRINT ABSCHNITT
			if($abschnitt != 0){
				print "</$listtype>\n</li>";
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
		print "</$listtype>\n</li>";
	}
	if($abschnitt != 0){
		print "</$listtype>\n</li>";
	}
	print "</$listtype>\n<br><br>";

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
					print "</$listtype>\n</li>";
				}
				print "<br><br></$listtype>\n</li>";
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
				print "<br></$listtype>\n</li>";
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
		print "</$listtype>\n</li>";
	}
	if($abschnitt != 0){
		print "</$listtype>\n</li>";
	}
	print "</$listtype>\n";
}

# Zeigt die Doku zum Bearbeiten an
sub edit_doku {
	if(sperrCheck()==1) { return; }
	my $sprache = shift;
	my $listtype = "ul";
	my $sth = $dbh->prepare("SELECT paragraph, abschnitt, satz, titel FROM doku_$sprache ORDER BY paragraph ASC, abschnitt ASC, satz ASC")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	my $paragraph = 0;
	my $abschnitt = 0;
	my $satz = 0;
	$sth->execute();
	my @row;
	my @all;
	my $class = "green";
	my $class2 = "red";
	my $back = "zur&uuml;ck";
	print "<a name=\"#anfang\"></a><$listtype>";
	while(@row = $sth->fetchrow_array()) {
		if($paragraph < $row[0]) {
			#PRINT PARAGRAPH
			if($paragraph != 0){
				if ($satz != 0){
					print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$paragraph&a=$abschnitt&s=".($satz+1)."\">einf&uuml;gen</a></b></li>";
				}
				if ($abschnitt != 0) {
					print "</$listtype></li>";
				}
				print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$paragraph&a=".($abschnitt+1)."&s=0\">einf&uuml;gen</a></b></li>";
				print "<br><br></$listtype></li>";
			}
			print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">einf&uuml;gen</a></b></li>";
			print "<li><b>".print_chapter($row[0],$row[1],$row[2])." $row[3]</b> ";
			print "<a class=\"$class\" href=\"$skript?aktion=edit_this_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">bearbeiten</a> ";
			print "<a class=\"$class2\" href=\"$skript?aktion=del_doku&sure=no&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">l&ouml;schen</a>";
			print "<$listtype>";
			$paragraph++;
			$abschnitt = 0;
			$satz = 0;
		} elsif ($abschnitt < $row[1]) {
			#PRINT ABSCHNITT
			if($abschnitt != 0){
				if ($satz != 0) {
					print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$paragraph&a=$abschnitt&s=".($satz+1)."\">einf&uuml;gen</a></b></li>";
				}
				print "<br></$listtype></li>";
			}
			print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">einf&uuml;gen</a></b></li>";
			print "<li><b>".print_chapter($row[0],$row[1],$row[2])." $row[3]</b> ";
			print "<a class=\"$class\" href=\"$skript?aktion=edit_this_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">bearbeiten</a> ";
			print "<a class=\"$class2\" href=\"$skript?aktion=del_doku&sure=no&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">l&ouml;schen</a>";
			print "<$listtype>";
			print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=1\">einf&uuml;gen</a></b></li>";
			$abschnitt++;
			$satz = 0;
		} elsif($satz < $row[2]) {
			#PRINT SATZ
			if ($satz != 0) {
				print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">einf&uuml;gen</a></b></li>";
			}
			print "<li><b>".print_chapter($row[0],$row[1],$row[2])." $row[3]</b> ";
			print "<a class=\"$class\" href=\"$skript?aktion=edit_this_doku&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">bearbeiten</a> ";
			print "<a class=\"$class2\" href=\"$skript?aktion=del_doku&sure=no&lang=$sprache&p=$row[0]&a=$row[1]&s=$row[2]\">l&ouml;schen</a>";
			print "</li>";
			$satz++;
		}
	}
	if($abschnitt != 0){
		if ($satz != 0) {
			print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$paragraph&a=$abschnitt&s=".($satz+1)."\">einf&uuml;gen</a></b></li>";
		}
		print "</$listtype></li>";
	}
	if($paragraph != 0){
		print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=$paragraph&a=".($abschnitt+1)."&s=0\">einf&uuml;gen</a></b></li>";
		print "</$listtype></li>";
	}
	print "<li><b><a class=\"$class\" href=\"$skript?aktion=new_doku&lang=$sprache&p=".($paragraph+1)."&a=0&s=0\">einf&uuml;gen</a></b></li>";
	print "</$listtype><br><br>";
}

sub edit_this_doku {
	if(sperrCheck()==1) { return; }
	my $sprache = shift;
	my $paragraph = shift;
	my $abschnitt = shift;
	my $satz = shift;
	my $sth = $dbh->prepare("SELECT titel, inhalt FROM doku_$sprache WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz = '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	print "<form action=\"$skript?aktion=write_doku&lang=$sprache&p=$paragraph&a=$abschnitt&s=$satz\" method=\"post\">";
	print "<p>Titel:<br><input name=\"titel\" size=\"60\" value=\"$row[0]\"></p>";
	print "<p>Inhalt:<br><textarea name=\"inhalt\" cols=\"100\" rows=\"14\">$row[1]</textarea></p>";
	print "<p><input type=\"submit\" value=\"Formulardaten absenden\"></p></form>";
}

sub write_doku {
	if(sperrCheck()==1) { return; }
	my $sprache = shift;
	my $paragraph = shift;
	my $abschnitt = shift;
	my $satz = shift;
	my $titel = $cgi->param('titel');
	my $inhalt = $cgi->param('inhalt');
	my $sth = $dbh->prepare("UPDATE doku_$sprache SET titel = '$titel', inhalt = '$inhalt' WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz = '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	printFehler("Daten gespeichert!");
}

sub del_doku {
	if(sperrCheck()==1) { return; }
	my $sure = shift;
	my $sprache = shift;
	my $paragraph = shift;
	my $abschnitt = shift;
	my $satz = shift;
	my $sth;
	my @row;
	if ($abschnitt == 0) {
		$sth = $dbh->prepare("SELECT * FROM doku_$sprache WHERE paragraph = '$paragraph' AND abschnitt > '0' AND satz > '0'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		@row = $sth->fetchrow_array();
		if (scalar(@row) != 0) {
			printFehler("Es sind noch Unterpunkte vorhanden, bitte l&ouml;sche zuerst diese!");
			return;
		}
	} elsif ($satz == 0) {
		$sth = $dbh->prepare("SELECT * FROM doku_$sprache WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz > '0'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		@row = $sth->fetchrow_array();
		if (scalar(@row) != 0) {
			printFehler("Es sind noch Unterpunkte vorhanden, bitte l&ouml;sche zuerst diese!");
			return;
		}
	}
	$sth = $dbh->prepare("SELECT * FROM doku_$sprache WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz = '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	@row = $sth->fetchrow_array();
	if (scalar(@row) == 0) {
		printFehler("Diesen Punkt gibt es nicht, Aktion unterbrochen!");
		return;
	}

	$sth = $dbh->prepare("SELECT titel FROM doku_$sprache WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz = '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	@row = $sth->fetchrow_array();

	if ($sure ne "yes") {
		print "<a href=\"$skript?aktion=del_doku&sure=yes&lang=$sprache&p=$paragraph&a=$abschnitt&s=$satz\">";
		print "Dieser Link l&ouml;scht ".print_chapter($paragraph,$abschnitt,$satz)." $row[0] endg&uuml;ltig!</a>";
	} else {
		$sth = $dbh->prepare("DELETE FROM doku_$sprache WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz = '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute();
		if ($satz != 0) {
			$sth = $dbh->prepare("UPDATE doku_$sprache SET satz = satz-1 WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz > '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		} elsif ($abschnitt != 0) {
			$sth = $dbh->prepare("UPDATE doku_$sprache SET abschnitt = abschnitt-1 WHERE paragraph = '$paragraph' AND abschnitt > '$abschnitt'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		} else {
			$sth = $dbh->prepare("UPDATE doku_$sprache SET paragraph = paragraph-1 WHERE paragraph > '$paragraph'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		}
		$sth->execute();
		printFehler("L&ouml;schen beendet.");
	}
}


sub new_doku {
	if(sperrCheck()==1) { return; }
	my $sprache = shift;
	my $paragraph = shift;
	my $abschnitt = shift;
	my $satz = shift;
	my $sth;
	if ($satz != 0) {
		$sth = $dbh->prepare("UPDATE doku_$sprache SET satz = satz+1 WHERE paragraph = '$paragraph' AND abschnitt = '$abschnitt' AND satz >= '$satz'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	} elsif ($abschnitt != 0) {
		$sth = $dbh->prepare("UPDATE doku_$sprache SET abschnitt = abschnitt+1 WHERE paragraph = '$paragraph' AND abschnitt >= '$abschnitt'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	} else {
		$sth = $dbh->prepare("UPDATE doku_$sprache SET paragraph = paragraph+1 WHERE paragraph >= '$paragraph'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	}
	$sth->execute();
	$sth = $dbh->prepare("INSERT INTO doku_$sprache VALUES ('$paragraph', '$abschnitt', '$satz', 'Titel', 'Text')")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	edit_this_doku($sprache, $paragraph, $abschnitt, $satz);
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

# ----- ENDE DOKUSYSTEM -----


# ----- ZUGRIFF AUF ALTE DATEN -----

sub look_old_data() {
	my $active_dir = shift; # aktives Verzeichnis
	my $active_file = shift; # aktive Datei; . bei Verzeichnis
	if ($active_file eq '.') {
		my $parent = $active_dir;
		while (chop($parent) ne '/') {} # übergeordnetes Verzeichnis
		my $output;
		$output = `cd $active_dir && find -maxdepth 1 -type d`;
		$output = substr($output, 4);
		my @dirs = split('\n./', $output);
		@dirs = sort(@dirs);
		if ($parent ne ".") {
			print "<a href=\"$skript?aktion=look_old_data&dir=$parent&file=.\">..</a><br>"; #in ein Verzeichnis höher wechseln, außer wenn bereits im tiefsten (./logs)
		}
		foreach(@dirs) {
			print "<a href=\"$skript?aktion=look_old_data&dir=$active_dir/$_&file=.\">$_</a><br>"
		}
		$output = `cd $active_dir && find -maxdepth 1 -type f`;
		$output = substr($output, 2);
		my @files = split('\n./', $output);
		@files = sort(@files);
		
		foreach(@files) {
			print "<a href=\"$skript?aktion=look_old_data&dir=$active_dir&file=$_\">$_</a><br>";
		}
	} else {
		my $output;
		$output = `cd $active_dir && cat $active_file`;
		my @text = split('\n', $output);
		print "<a href=\"$skript?aktion=look_old_data&dir=$active_dir&file=.\">zur&uuml;ck</a><br><br>";
		print "<table cellspacing=\"18\" cellpadding=\"0\">";
		foreach(@text) {
			my $tempstring = $_;
			my @line = split('\t', $tempstring);
			print "<tr>";
			foreach (@line) {
				print "<td align=\"left\">$_</td>";
			}
			print "</tr>";
		}
		print "</table>";
	}
}

# ----- ENDE ZUGRIFF AUF ALTE DATEN -----



# ----- MASSENNACHRICHT SENDEN -----

sub create_shout {
	print "<form action=\"$skript?aktion=send_shout\" method=\"post\">";
	print "<p align=\"center\">Nachricht:<br><textarea name=\"message\" cols=\"80\" rows=\"10\">Hier Nachricht eingeben</textarea><br>";
	print "<input type=\"submit\" value=\"Abschicken\"></p></form>";
}

# fügt eine Nachricht bei einem User hinzu
sub massenNachricht {
	my $nachricht = $cgi->param('message');
	my $nachricht = "<br>".encode("utf-8", $nachricht);
	my $sth = $dbh->prepare("update users set message = CONCAT(message, '$nachricht') where status < $waschag;")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	$nachricht = $nachricht." by $gName $gNname";
	$sth = $dbh->prepare("update users set message = CONCAT(message, '$nachricht') where status >= $waschag;")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	printFehler("Nachricht erfolgreich versendet!");
}

# ----- ENDE MASSENNACHRICHT SENDEN -----



# ----- HTML AUSGABESYSTEM -----
sub printFehler {
	my $fehler = shift;
	print "$fehler<br>";
}
