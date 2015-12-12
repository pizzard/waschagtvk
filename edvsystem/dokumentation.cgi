#!/usr/bin/perl
use strict;
use CGI;	# CGI-Modul
use CGI::Carp qw(fatalsToBrowser);
use DBD::mysql;
use Apache::DBI;
use Encode;
use CGI qw(:standard);
use POSIX qw(ceil floor);
use Config::IniFiles;

# DIESES SKRIPT IST IN UTF-8 KODIERT

# ----- GLOBALE VARIABLEN UND KONSTANTEN -----

our $cgi = new CGI;	# erzeugt ein neues CGI-Objekt (damit Formulare bearbeitet und HTML ausgegeben werden kann)
our $skript = "dokumentation.cgi"; # Dateiname
our $include = "inc/"; #Include-Verzeichnis
our $progName = "Punktesystem"; # Prgrammname
our $god = 9; # Status: Superuser
our $godsName = "Christian Ewald"; # Wehe da spielt jemand dran rum ;)
our $version = "Alpha 1"; # Versionsnummer
our $admin = 7; # Status: Haussprecher
our $gremium = 5; # Status: Kontrollgremiumsmitglied
our $agmitglied = 3; # Status: AG-Mitglied
our $user = 1; # Status: User
our $wartung = 0; # 1 sperrt das gesamte System fuer alle User ausser HS + Admin
our $godWartung = 0; # 1 sperrt das gesamte System fuer alle User ausser Admin
our $error = ''; # temporaere Variable fuer diverse Fehlermeldungen
our $db = "wasch"; # DB Name
our $gId;
our $gPunkte;
our $gAgnutzung;
our $gStatus;
our $gEintragung;
our $gBearbeiter;
our $maxPunkte = 10;

# ----- ENDE GLOBALE VARIABLEN UND KONSTANTEN -----



# ----- MAIN -----

# Ã–ffnen der Datenbank
my $dbh;
my $cfg = Config::IniFiles->new( -file => "./inc/config.ini" );
$dbh = DBI->connect($cfg->val($db,"db"),$cfg->val($db,"user"),$cfg->val($db,"pw")) or die $DBI::errstr;

# Start HTML
if ($cgi->url_param('aktion') eq 'login') {
	firstLogin();
} elsif ($cgi->url_param('aktion') eq 'index') {
	if (kopf("index", $user) == 1) {
		hauptMenue();
	}
# User Management
} elsif ($cgi->url_param('aktion') eq 'new_user') {
	if (kopf("new_user", $gremium) == 1) {
		gibNewForm();
	}
} elsif ($cgi->url_param('aktion') eq 'create_user') {
		if (kopf("create_user", $gremium) == 1) {
			create_user();
		}
} elsif ($cgi->url_param('aktion') eq 'edit_user') {
	if (kopf("edit_user", $gremium) == 1) {
		start_edit(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'do_edit') {
	if (kopf("do_edit", $gremium) == 1) {
		do_edit(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'delete_user') {
	if (kopf("delete_user", $gremium) == 1) {
		delete_user(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'mach_tot') {
	if (kopf("delete_user", $gremium) == 1) {
		deleteUserEndgueltig(makeclean($cgi->url_param('id')));
	}
} elsif ($cgi->url_param('aktion') eq 'change_pw') {
	if (kopf("change_pw", $user) == 1) {
		changePW() ;
	}
} elsif ($cgi->url_param('aktion') eq 'do_change_pw') {
	if (kopf("change_pw", $user) == 1) {
		doChange();
	}
} elsif ($cgi->url_param('aktion') eq 'give_points') {
	if (kopf("give_points", $gremium) == 1) {
		manage_points();
	}
} elsif ($cgi->url_param('aktion') eq 'save_points') {
	if (kopf("give_points", $gremium) == 1) {
		punkte_transaktion();
	}
} elsif ($cgi->url_param('aktion') eq 'user_management') {
	if (kopf("user_management", $gremium) == 1) {
		userVerwaltung();
	}
} elsif ($cgi->url_param('aktion') eq 'stats') {
	if (kopf("stats", $admin) == 1) {
		statistik();
	}
} elsif ($cgi->url_param('aktion') eq 'look_ag_use') {
	if (kopf("ag_use", $agmitglied) == 1) {
		look_ag_use();
	}
} else {
	print_header();
	Titel("Login");
	logon();
}
print_footer();		# und der html-ausgabe-teil beendet.

# ----- MAIN ENDE -----



# ----- HEADER, FOOTER UND LAYOUT -----

# Kopf jeder Seite, implementiert das Design der Netz-AG
sub print_header {
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
}

# FuÃŸ jeder Seite, GegenstÃ¼ck zu print_header
sub print_footer {
	print "<br><br><br><br><br><table width=\"100%\" frame=\"above\" cellpadding=\"5\">";
	print "<tr><td align=\"left\"> $progName $version</td><td align=\"right\">by $godsName </td></tr>";
	open (ENDE, "/var/www/localhost/htdocs/ende.inc");
	my @file = <ENDE>;
	print @file;
	close (ENDE);
	#$dbh->disconnect;
}

# Titelleiste
# param Titel
sub Titel {
	my $titel = shift;
	print "<table><tr><th align=\"left\">$progName : $titel</th></tr></table>";
}

# Universalfunktion zum Validieren der Logindaten, Ueberpruefen der Zugriffsrechte, setzen des Titels und Erstellen der Menueleisten
# param anliegen, benoetigter Status
sub kopf {
	my $anliegen = shift;
	my $neededStatus = shift;
	# Auslesen der Cookies
	my $login = cookie("plogin");
	my $pw = cookie("ppw");
	if (validate($login, $pw) == 0) {
		# Aufforderung zum erneuten Login bei falschen Eingabedaten
		print_header();
		Titel("Login");
		logon();
		return (0);
	} else {
		# Setzen globaler Variablen
		my $sth = $dbh->prepare("SELECT punktestand, agnutzung, status, eintragung, bearbeiter, id FROM userlist WHERE id = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();	# fÃ¼hrt den befehl aus
		my @row = $sth->fetchrow_array;
		our $gId = decode("utf-8", $row[5]);
		our $gPunkte = decode("utf-8", $row[0]);
		our $gAgnutzung = decode("utf-8", $row[1]);
		our $gStatus = decode("utf-8", $row[2]);
		our $gEintragung = decode("utf-8", $row[3]);
		our $gBearbeiter = decode("utf-8", $row[4]);
		print_header();
		if (($wartung && $gStatus < $admin) || ($godWartung && $gStatus < $god)) {
			Titel("Wartungsarbeiten");
			printFehler("<br><br>Momentan werden Wartungsarbeiten am System durchgef&uuml;hrt. Habe bitte ein bisschen Geduld!");
			return (0);
		}
		# ÃœberprÃ¼fung der Zugriffsrechte, ggf. Meldung einer Zugriffsverletzung an die DB
		if ($gStatus < $neededStatus) {
			# Leere Drohungen ausstossen ;)
			printFehler ("Zugang zu Interna verweigert! Benachrichtigung an Admins versendet.<br><br>Weitere Zugriffsversuche werden geahndet!");
			return (0);
		}
		if ($anliegen eq "index"){
			Titel("Willkommensseite / Welcome page");
		} elsif ($anliegen eq "new_user") {
			Titel("Neuen User erstellen / Create new user");
		} elsif ($anliegen eq "look_user") {
			Titel("Userverwaltung / User management");
		} elsif ($anliegen eq "stats") {
			Titel("Statistiken / Statistics");
		} elsif ($anliegen eq "give_points") {
			Titel("Punkte eintragen / Enter points");
		} elsif ($anliegen eq "delete_user") {
			Titel("User l&ouml;schen / Delete user");
		} elsif ($anliegen eq "ag_use") {
			Titel("AG-Nutzungsliste einsehen / View AG use list");
		}
		# Menueleisten nach Benutzerstatus
		if ($gStatus >= $user) {
			print "<table cellspacing=\"10\" cellpadding=\"5\" width=\"100%\">";
			print "<tr><td align=\"center\"><a href=\"$skript?aktion=index\">Willkommensseite<br>Welcome page</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=change_pw\">Passwort &auml;ndern<br>Change password</a></td>";
			if ($gStatus >= $agmitglied) {
				print "<td align=\"center\"><a href=\"$skript?aktion=look_ag_use\">AG-Nutzungsliste<br>AG use list</a></td>";
			}
			print "</tr></table>";
		}
		if ($gStatus >= $gremium){
			print "<table cellspacing=\"10\" cellpadding=\"5\" width=\"100%\">";
			print "<tr><td align=\"center\"><a href=\"$skript?aktion=new_user\">Neuen User erstellen<br>Create new user</a></td>";
			print "<td align=\"center\"><a href=\"$skript?aktion=user_management&sort=id%20ASC\">Userverwaltung<br>User management</a></td>";
			if ($gStatus >= $admin){
				print "<td align=\"center\"><a href=\"$skript?aktion=stats\">Statistiken<br>Statistics</a></td>";
			}
			print "</tr></table><br><br>";
		}
	}
	return (1);
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

# Macht eine Tabellenzeile fÃ¼r die Titelzeile der Tabelle
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

# ----- ENDE HEADER, FOOTER UND LAYOUT -----



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
	print "<p>User-ID:<br><input name=\"login\" size=\"40\" value=\"$login\"></p>";
	print "<p>Passwort:<br><input name=\"pw\" type=\"password\" size=\"40\"></p>";
	print "<p><input type=\"submit\" value=\"Einloggen\"></p></form>";
}

# prÃ¼ft die beim Login eingegebenen Werte und setzt die Cookies
sub firstLogin {
	my $login = $cgi->param('login');
	my $pw = crypt($cgi->param('pw'), "ps");
	if (validate(vorbereiten($login), $pw) == 1){
		$login = vorbereiten($login);
		setCookies($login, $pw);
	} else {
		print_header();
		Titel("Login");
		logon($login);
	}
}

# validiert ob pw und login legal sind
# param login
# param pw
# return 0 = false, 1 = success
sub validate {
	my $login = shift;
	my $pw = shift;
	my $sth = $dbh->prepare("SELECT pw FROM userlist WHERE id = $login")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array;
	if (scalar(@row) == 0) {
		$error = "User $login unbekannt!";
		return(0);
	}
	if (decode("utf-8", $row[0]) eq $pw) {
		return(1);
	} else {
		$error = "Passwort falsch!";
		return(0);
	}
}

# Setzt die Cookies, die fÃ¼rs Validieren wichtig sind (Passwort und Login)
sub setCookies {
	my $login = shift;
	my $pw = shift;
	my $cLogin = $cgi->cookie (
		-NAME => 'plogin',
		-VALUE => $login
	);
	my $cPw = $cgi->cookie (
		-NAME => 'ppw',
		-VALUE => $pw
	);
	print $cgi->redirect(-URL=>"$skript?aktion=index&del=no", -cookie=>[$cLogin, $cPw]);
}

# ----- ENDE LOGIN -----



# ----- HAUPTMENUE -----

# Stellt das HauptmenÃ¼ dar, lÃ¶scht je nach Verlangen die hinterlassene Nachricht
sub hauptMenue {
	if ($cgi->url_param('del') eq 'yes'){
		prepare_delete_message();
		return;
	} elsif ($cgi->url_param('del') eq 'sure'){
		delete_message();
	}
	if ($cgi->url_param('sell') eq 'yes'){
		sell_points();
	}
	my $sth = $dbh->prepare("SELECT nachricht, agnutzung, punktestand, eintragung, bearbeiter FROM userlist WHERE id='$gId'")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	print "<table cellspacing=\"5\" cellpadding=\"10\" width=\"100%\"><tr><td>Hallo $gId, du hast momentan <b>$row[2] Punkte</b> auf deinem Punktekonto. AG-Nutzung f&uuml;r das laufende T&uuml;rmester ist bei dir";
	if ($row[1] == 0) { print " <font color=\"red\"><b>nicht</b></font>"; }
	print " freigeschaltet.</td></tr>";
	print "<tr><td>Hello $gId, at the moment you have <b>$row[2] points</b> on your account. AG use for the current T&uuml;rmester is";
	if ($row[1] == 0) { print " <font color=\"red\"><b>not</b></font>"; }
	print " unlocked.</td></tr>";
	if ($row[1] == 0 && $row[2] >= 2) {
		print "<tr><th bgcolor=\"#00ee00\">";
		print "<form action=\"$skript?aktion=index&sell=yes\" method=\"post\">";
		print "<input type=\"submit\" value=\"2 Punkte einl&ouml;sen um AG-Nutzung f&uuml;r das laufende T&uuml;rmester freizuschalten\nUse 2 points to unlock AG use for the current T&uuml;rmester\"></form>";
		print "</th></tr>";
		}
	if ($row[0] ne "") {
		my $nachricht = $row[0];
		print "<tr><td>$nachricht</td>";
		print "<td><a href=\"$skript?aktion=index&del=yes\">l&ouml;schen</a></td></tr>";
	}
	print "</table>";
}

# Loeschen der Nachricht bestaetigen
sub prepare_delete_message {
	print "<a href=\"$skript?aktion=index&del=sure\">Ein Klick auf diesen Link l&ouml;scht deinen Verlauf endg&uuml;ltig!<br>One click on this link deletes your history irrevocably.</a>";
}

# Loeschen der Nachricht
sub delete_message {
	my $sth = $dbh->prepare("UPDATE userlist SET nachricht='' WHERE id='$gId'")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
}

# Punkte einloesen
sub sell_points {
	my $sth = $dbh->prepare("SELECT agnutzung, punktestand from userlist WHERE id='$gId'")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if ($row[0] == 0) {
		if ($row[1] >= 2) {
			$sth = $dbh->prepare("UPDATE userlist SET agnutzung='1', punktestand=punktestand-2 WHERE id='$gId'")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
			$sth->execute();
		} else {
			printFehler("Du hast nicht genug Punkte daf&uuml;r");
			printFehler("You do not have enough points!");
		}
	} else {
		printFehler("AG-Nutzung ist bei dir bereits freigeschaltet!");
		printFehler("AG use is already unlocked!");
	}
}

# ----- ENDE HAUPTMENUE -----


# ----- USERUEBERSICHTEN -----

# stellt die Userliste bereit
# param sortierung
sub userVerwaltung {
	my $sortierung = $cgi->url_param('sort');
	my $sth = $dbh->prepare("SELECT id, punktestand, agnutzung, status, eintragung, bearbeiter, verlauf FROM userlist ORDER BY $sortierung")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row;
	print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
	normalTabellenZeileKopf("black",
								"ID<br><a href=\"$skript?aktion=user_management&sort=id%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=id%20DESC\">&gt;</a>",
								"Punkte<br>points<br><a href=\"$skript?aktion=user_management&sort=punktestand%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=punktestand%20DESC\">&gt;</a>",
								"AG-Nutzung<AG use><br><a href=\"$skript?aktion=user_management&sort=agnutzung%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=agnutzung%20DESC\">&gt;</a>",
								"Status<br>status<br><a href=\"$skript?aktion=user_management&sort=status%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=status%20DESC\">&gt;</a>",
								"Letzte Eintragung<br>last entry<br><a href=\"$skript?aktion=user_management&sort=eintragung%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=eintragung%20DESC\">&gt;</a>",
								"von<br>by<br><a href=\"$skript?aktion=user_management&sort=bearbeiter%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=bearbeiter%20DESC\">&gt;</a>",
								"Verlauf<br>history<br><a href=\"$skript?aktion=user_management&sort=verlauf%20ASC\">&lt;</a><a href=\"$skript?aktion=user_management&sort=verlauf%20DESC\">&gt;</a>");
	while (@row = $sth->fetchrow_array()) {
		if ($row[2] == 1) {
			tabellenZeile("black", @row);
		} elsif ($row[2] == 0) {
			tabellenZeile("red", @row);
		} else {
			tabellenZeile("orange", @row);
		}
	}
	print "</table>";
	#$dbh->disconnect;
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
	print "<td align=\"center\"><a href=\"$skript?aktion=give_points&id=$id\">Punkte<br>eingeben</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=edit_user&id=$id\">bearbeiten</a></td>";
	print "<td align=\"center\"><a href=\"$skript?aktion=delete_user&id=$id\">l&ouml;schen</a></td>";
	print "</tr>";
}

# ----- USERÜBERSICHT ENDE -----



# ----- USER BEARBEITEN -----

sub gibNewForm {
	my $name = shift;
	my $nachname = shift;
	my $haus = shift;
	my $zimmer = shift;
	my $altBewohner = shift;
	my $verlauf = shift;
	print "<form action=\"$skript?aktion=create_user\" method=\"post\">";
	print "<table cellspacing=\"5\" cellpadding=\"3\">";
	print "<tr><th>Vorname:</th><th><input name=\"name\" size=\"40\" value=\"$name\"></th></tr>";
	print "<tr><th>Nachname:</th><th><input name=\"nachname\" size=\"40\" value=\"$nachname\"></th></tr>";
	print "<tr><th>Haus:</th><th><select name=\"haus\" size=\"4\"><option value=\"oih\">OIH</option><option value=\"oph\">OPH</option><option value=\"tvk\" selected>TvK</option><option value=\"weh\">WEH</option></th></tr>"; #Dropbox
	print "<tr><th>Zimmer:</th><th><input name=\"zimmer\" size=\"4\" value=\"$zimmer\"></th></tr>";
	if ($altBewohner == 1) {
		print "<tr><th>Einzug vor dem 01.01.2010?</th><th><input type=\"checkbox\" name=\"altBewohner\" value=\"1\" checked></th></tr>";
	} else {
		print "<tr><th>Einzug vor dem 01.01.2010?</th><th><input type=\"checkbox\" name=\"altBewohner\" value=\"1\"></th></tr>";
	}
	if ($verlauf == 1) {
		print "<tr><th>Verlauf aktivieren</th><th><input type=\"checkbox\" name=\"verlauf\" value=\"1\" checked></th></tr>";
	} else {
		print "<tr><th>Verlauf aktivieren</th><th><input type=\"checkbox\" name=\"verlauf\" value=\"1\"></th></tr>";
	}
	print "<tr><th></th><th><input type=\"submit\" value=\"Neuen User erstellen\nCreate new user\"></th></tr></form></table>";
}

sub start_edit {
	my $id = shift;
	my $sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4), status , verlauf , nachricht FROM userlist WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	gibEditForm($id, @row, 0);
}

sub gibEditForm {
	my $id = shift;
	my $haus = shift;
	my $zimmer = shift;
	my $status = shift;
	my $verlauf = shift;

	my $sth = $dbh->prepare("SELECT nachricht FROM userlist WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;

	print "<table><form action=\"$skript?aktion=do_edit&id=$id\" method=\"post\">";
	print "<tr><th>ID:</th><th>".decode("utf-8", $id)."</th></tr>";
	if ($haus eq "OIH") {
		print "<tr><th>Haus:</th><th><select name=\"haus\" size=\"4\"><option value=\"OIH\" selected>OIH</option><option value=\"OPH\">OPH</option><option value=\"TVK\">TvK</option><option value=\"WEH\">WEH</option></th></tr>"; #Dropbox
	} elsif ($haus eq "OPH") {
		print "<tr><th>Haus:</th><th><select name=\"haus\" size=\"4\"><option value=\"OIH\">OIH</option><option value=\"OPH\" selected>OPH</option><option value=\"TVK\">TvK</option><option value=\"WEH\">WEH</option></th></tr>"; #Dropbox
	} elsif ($haus eq "TVK") {
		print "<tr><th>Haus:</th><th><select name=\"haus\" size=\"4\"><option value=\"OIH\">OIH</option><option value=\"OPH\">OPH</option><option value=\"TVK\" selected>TvK</option><option value=\"WEH\">WEH</option></th></tr>"; #Dropbox
	} elsif ($haus eq "WEH") {
		print "<tr><th>Haus:</th><th><select name=\"haus\" size=\"4\"><option value=\"OIH\">OIH</option><option value=\"OPH\">OPH</option><option value=\"TVK\">TvK</option><option value=\"WEH\" selected>WEH</option></th></tr>"; #Dropbox
	}
	print "<tr><th>Zimmer:</th><th><input name=\"zimmer\" size=\"4\" value=\"$zimmer\"></th></tr>";
	if ($status == $user) {
		print "<tr><th>Status:</th><th><select name=\"status\" size=\"4\"><option value=\"$user\" selected>User</option><option value=\"$agmitglied\">AG-Mitglied</option><option value=\"$gremium\">Gremiumsmitglied</option><option value=\"$admin\">Haussprecher</option></th></tr>"; #Dropbox
	} elsif ($status == $agmitglied) {
		print "<tr><th>Status:</th><th><select name=\"status\" size=\"4\"><option value=\"$user\">User</option><option value=\"$agmitglied\" selected>AG-Mitglied</option><option value=\"$gremium\">Gremiumsmitglied</option><option value=\"$admin\">Haussprecher</option></th></tr>"; #Dropbox
	} elsif ($status == $gremium) {
		print "<tr><th>Status:</th><th><select name=\"status\" size=\"4\"><option value=\"$user\">User</option><option value=\"$agmitglied\">AG-Mitglied</option><option value=\"$gremium\" selected>Gremiumsmitglied</option><option value=\"$admin\">Haussprecher</option></th></tr>"; #Dropbox
	} elsif ($status == $admin) {
		print "<tr><th>Status:</th><th><select name=\"status\" size=\"4\"><option value=\"$user\">User</option><option value=\"$agmitglied\">AG-Mitglied</option><option value=\"$gremium\">Gremiumsmitglied</option><option value=\"$admin\" selected>Haussprecher</option></th></tr>"; #Dropbox
	}
	if ($verlauf == 1) {
		print "<tr><th>Verlauf aktivieren</th><th><input type=\"checkbox\" name=\"verlauf\" value=\"1\" checked></th></tr>";
	} else {
		print "<tr><th>Verlauf aktivieren</th><th><input type=\"checkbox\" name=\"verlauf\" value=\"1\"></th></tr>";
	}
	print "<tr><th>Passwort &auml;ndern:</th><th><input type=\"checkbox\" name=\"pw\" value=\"pwchange\"></th></tr>";
	if ($row[0] ne "") {
		print "<tr><th>Verlauf:</th><th>".$row[0]."</th></tr>";
	}
	print "<tr><th><input type=\"submit\" value=\"Formulardaten absenden\"></th></tr></form></table>";
}

sub do_edit {
	my $id = decode("utf-8", shift);
	my $haus = $cgi->param('haus');
	my $zimmer = $cgi->param('zimmer');
	my $status = $cgi->param('status');
	my $verlauf = $cgi->param('verlauf');
	my $pw =  $cgi->param('pw');
	my $ok = isNatural($status) + isValidZimmer(\$zimmer, $haus);

	my @row;
	if (darf_bearbeiten($id) == 0){
		printFehler("Status ung&uuml;ltig! Status muss kleiner als dein eigener sein, au&szlig;er du bearbeitest dich selber!");
		$ok = 1;
	}

	if ($status > $gStatus || ($id != $gId && $status == $gStatus)) {
		printFehler("Du darfst den Status nicht auf deinen oder h&ouml;her anheben!");
		$ok = 1;
	}
	
	my $ort = $haus."_".$zimmer;
	my $sth = $dbh->prepare("SELECT id FROM userlist WHERE SUBSTR(id,1,8) = '$ort' && id!='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	while (@row = $sth->fetchrow_array()) {
		printFehler("Zimmernummer bereits von ".decode("utf-8", $row[0])." belegt. Unbedingt &uuml;berpr&uuml;fen und alten User ggf. l&ouml;schen!</font></b>");
		printFehler("Room number already occupied by ".decode("utf-8", $row[0]).". Check is essential. Delete old user, if necessary!</font></b>");
	}

	if ($ok == 0) {
		my $change;
		if ($pw ne "pwchange") {
			$change = "";
		} else {
			my @randpw = `apg`;
			$pw = $randpw[0];
			printFehler("<br>Es wurde folgendes Passwort generiert: <b>$pw</b>");
			printFehler("<br>The following password has been generated: <b>$pw</b><br>");
			$pw = crypt($pw, "ps");
			$change = " pw='$pw' ,";
			printFehler("Passwort ge&auml;ndert!");
			printFehler("Password has been changed!");
		}
		my $sql = "UPDATE userlist SET $change id=CONCAT('".$haus."_".$zimmer."_', SUBSTR(id FROM 10)), status='$status', verlauf='$verlauf', bearbeiter='$gId', eintragung=NOW() WHERE id='$id'";
		#printFehler($sql);
		$sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		printFehler("Der User wurde erfolgreich ge&auml;ndert!");
		printFehler("The user has been changed successfully!");
	} else {
		gibEditForm($id, $haus, $zimmer, $status, $verlauf);
	}
	$dbh->disconnect;
}

# stellt fest, ob ein User einen anderen User bearbeiten darf
sub darf_bearbeiten {
	my $zielId = shift;
	if ($zielId == $gId) {
		return (1);
	}
	my $sth = $dbh->prepare("SELECT status FROM userlist WHERE id = '$zielId'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	if ($row[0] < $gStatus){
		return (1);
	} else {
		printFehler("Es d&uuml;rfen nur User mit einem kleineren Status bearbeitet werden!");
		return (0);
	}
}

# ----- USER BEARBEITEN ENDE -----



# ----- USER LOESCHEN -----

# Abfragelink, ob ein User wirklich gelöscht werden soll
sub delete_user {
	my $id = shift;
	print "<a href=\"$skript?aktion=mach_tot&id=$id\">Dieser Link l&ouml;scht User ".decode("utf-8", $id)." endg&uuml;ltig!</a>";
}

# löscht einen User endgültig
sub deleteUserEndgueltig {
	my $id = decode("utf-8", shift);
	if (darf_bearbeiten($id) == 0) {
		return;
	}
	my $sth = $dbh->prepare("DELETE FROM userlist WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	printFehler("User gel&ouml;scht");
}


# ----- PUNKTE EINGEBEN -----

sub manage_points {
	my $id = $cgi->url_param('id');
	if ($id eq $gId) {
		printFehler("Du darfst dir nicht selber Punkte eintragen!");
		return;
	}
	my $sth = $dbh->prepare("SELECT punktestand, eintragung, bearbeiter, verlauf FROM userlist WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array;
	print "<table>";
	normalTabellenZeile("black", "<b>ID</b>", $id);
	normalTabellenZeile("black", "<b>aktueller Punktestand</b>", $row[0]);
	normalTabellenZeile("black", "<b>letzte Eintragung</b>", $row[1]);
	normalTabellenZeile("black", "<b>eingetragen von</b>", $row[2]);
	print "<form action=\"$skript?aktion=save_points&id=$id\" method=\"post\">";
	if ($row[3] == 1) {
		normalTabellenZeile("black", "<b>Punkte eintragen</b>", "<input name=\"punkte\" size=\"1\">", "", "");
		normalTabellenZeile("black", "<b>Grund</b>", "<input name=\"grund\" size=\"20\" maxlength=\"200\"></input>", "", "<input type=\"submit\" value=\" best&auml;tigen\">");
	} else {
		normalTabellenZeile("black", "<b>Punkte eintragen</b>", "<input name=\"punkte\" size=\"2\">", "", "<input type=\"submit\" value=\" best&auml;tigen\">");
	}
	print "</form></table>";
}

# Punteeintragung ausfuehren
sub punkte_transaktion {
	my $id = $cgi->url_param('id');
	$id = decode("utf-8", $cgi->url_param('id'));
	my $punkte = $cgi->param('punkte');
	my $sth = $dbh->prepare("SELECT punktestand, verlauf, nachricht, NOW() FROM userlist WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row = $sth->fetchrow_array();
	my $grund;
	if ($row[1] == 1) {
		$grund = decode("utf-8",$cgi->param('grund'));
	} else {
		$grund = "";
	}
	if ($row[0] + $punkte < 0) {
		printFehler("Die Punkte d&uuml;rfen nicht unter 0 fallen!");
		printFehler("Point balance must not become negative!");
		return;
	} elsif ($punkte == 0 && isNatural($punkte) == 1) {
		printFehler("Bitte einen sinnvollen Betrag eingeben!");
		printFehler("Please enter a reasonable value!");
		return;
	} elsif ($punkte > $maxPunkte) {
		printFehler("Maximal auf einmal zu vergebende Punktzahl ist auf $maxPunkte festgelegt!");
		printFehler("The maximum amount of points per entry is limited to $maxPunkte points!");
		return;
	}
	if ($row[1] == 1 && $grund eq '') {
		printFehler("Bitte einen Grund eingeben!");
		printFehler("Please enter a reason!");
		return;
	} elsif ($row[1] == 1 && $grund ne '') {
		my $nachricht = decode("utf-8", $row[2]).$row[3]." von ".$gId." | ".$punkte." Punkte f&uuml;r: ".$grund."<br>";
		$punkte = $punkte + $row[0];
		$sth = $dbh->prepare("UPDATE userlist SET nachricht='$nachricht', punktestand=$punkte, eintragung=NOW(), bearbeiter='$gId' WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		printFehler("Punkte und Verlauf aktualisiert.");
		printFehler("Point balance and history updated.");
	} elsif ($row[1] == 0) {
		$sth = $dbh->prepare("UPDATE userlist SET punktestand=$punkte, eintragung=NOW(), bearbeiter='$gId' WHERE id='$id'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		printFehler("Punkte aktualisiert.");
		printFehler("Point balance updated.");
	}
}

# gibt zurück, ob es sich um einen Int handelt
sub isNatural {
	my $string = shift;
	if ($string =~ m/[^0-9]/) {
		printFehler("$string ist keine g&uuml;ltige nat&uuml;rliche Zahl!");
		return (1);
	} else {
		return (0);
	}
}

# ----- PUNKTE EINGEBEN ENDE -----



# Formular zum ändern des Passwortes
sub changePW {
	print "<form action=\"$skript?aktion=do_change_pw\" method=\"post\">";
	print "<table cellspacing=\"5\" cellpadding=\"3\">";
	print "<tr><th>Altes Passwort / Old password:</th><th><input name=\"oldpw\" type=\"password\" size=\"40\"></th></tr>";
	print "<tr><th>Neues Passwort / New password:</th><th><input name=\"pw\" type=\"password\" size=\"40\"></th></tr>";
	print "<tr><th>Neues Passwort wiederholen / Retype new password:</th><th><input name=\"pww\" type=\"password\" size=\"40\"></th></tr>";
	print "</table><input type=\"submit\" value=\"Passwort &auml;ndern\"></form>";
	print "Dein neues Passwort muss mindestens aus 8 Zeichen bestehen und 3 verschiedene Zeichenklassen beinhalten.<br>Es gibt 5 Zeichenklassen:<br>";
	print "Kleinbuchstaben, Gro&szlig;buchstaben, Sonderzeichen und Umlaute, Leerzeichen, Ziffern.<br>";
	print "Your new password has contain at least 8 characters of 3 different character classes.<br>There are 5 character classes:<br>";
	print "lowercases, capitals, special characters and umlauts, spaces, digits.";
}

sub doChange {
	my $oldpw = $cgi->param('oldpw');
	my $pw = $cgi->param('pw');
	my $pww = $cgi->param('pww');
	if (crypt($oldpw, "ps") ne cookie("ppw")) {
		printFehler("Passwort inkorrekt!");
		printFehler("Password incorrect!");
		return;
	}
	if ($pw ne $pww) {
		printFehler("Passw&ouml;rter unterschiedlich!");
		printFehler("Passwords are different!");
	} else {
		if ($pw ne '') {
			if (checkPW($pw) == 1) {
				$pw = crypt($pw, "ps");
				my $sql = "UPDATE userlist SET pw='$pw' WHERE id='$gId'";
				my $sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
				printFehler("Dein Passwort wurde erfolgreich ge&auml;ndert!\n");
				printFehler("Du musst dich jetzt neu <a href=\"$skript\">einloggen.</a>");
				printFehler("Your password has been changed successfully!\n");
				printFehler("Now please <a href=\"$skript\">log in</a> again.");
				return;
			}
		} else {
			printFehler("Kein Passwort eingegeben, Passwort nicht ge&auml;ndert!");
			printFehler("No password was entered, aborting!");
			return;
		}
	}
	changePW();
}

# prueft ein Passwort auf Sicherheit
# param pw
sub checkPW {
	my $pw = shift;
	my $pwl = length($pw);
	my $zeichenklassen = 0;

	if($pwl<8) {
		printFehler("Das Passwort ist nur $pwl Zeichen lang, verwende mindestens 8!<br>");
		printFehler("The password is only $pwl characters long, use at least 8!<br>");
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
		printFehler("Your password is too insecure, you have to use at least three different types of character classes: lowercases, capitals, special characters, digits oder spaces.");
		return (0);
	}
}


# ----- NEUEN USER ERSTELLEN -----

# Formular zum Eingeben der Daten für einen neuen User
sub gibNewForm {
	my $name = shift;
	my $nachname = shift;
	my $haus = shift;
	my $zimmer = shift;
	my $altBewohner = shift;
	my $verlauf = shift;
	print "<form action=\"$skript?aktion=create_user\" method=\"post\">";
	print "<table cellspacing=\"5\" cellpadding=\"3\">";
	print "<tr><th>Vorname:</th><th><input name=\"name\" size=\"40\" value=\"$name\"></th></tr>";
	print "<tr><th>Nachname:</th><th><input name=\"nachname\" size=\"40\" value=\"$nachname\"></th></tr>";
	print "<tr><th>Haus:</th><th><select name=\"haus\" size=\"4\"><option value=\"oih\">OIH</option><option value=\"oph\">OPH</option><option value=\"tvk\" selected>TvK</option><option value=\"weh\">WEH</option></th></tr>"; #Dropbox
	print "<tr><th>Zimmer:</th><th><input name=\"zimmer\" size=\"4\" value=\"$zimmer\"></th></tr>";
	if ($altBewohner == 1) {
		print "<tr><th>Einzug vor dem 01.01.2010?</th><th><input type=\"checkbox\" name=\"altBewohner\" value=\"1\" checked></th></tr>";
	} else {
		print "<tr><th>Einzug vor dem 01.01.2010?</th><th><input type=\"checkbox\" name=\"altBewohner\" value=\"1\"></th></tr>";
	}
	if ($verlauf == 1) {
		print "<tr><th>Verlauf aktivieren</th><th><input type=\"checkbox\" name=\"verlauf\" value=\"1\" checked></th></tr>";
	} else {
		print "<tr><th>Verlauf aktivieren</th><th><input type=\"checkbox\" name=\"verlauf\" value=\"1\"></th></tr>";
	}
	print "<tr><th></th><th><input type=\"submit\" value=\"Neuen User erstellen\nCreate new user\"></th></tr></form></table>";
}

# erstellt einen neuen User in der DB
sub create_user {
	#holen der Daten
	my @row;
	my $name = $cgi->param('name');
	my $nachname = $cgi->param('nachname');
	my $haus = uc($cgi->param('haus'));
	my $zimmer = $cgi->param('zimmer');
	my $altBewohner = $cgi->param('altBewohner');
	my $verlauf = $cgi->param('verlauf');
	my $ok = notLeer($haus, 'Haus')
				 + notLeer($name, 'Vorname')
				 + notLeer($nachname, 'Nachname')
				 + isValidZimmer(\$zimmer, $haus);
  	my $sth;
	if ($ok == 0) {
		my $ort = $haus."_".$zimmer;
		my $id = $ort."_".uc(substr($nachname,0,30));
		$sth = $dbh->prepare("SELECT id FROM userlist WHERE SUBSTR(id,1,8) = '$ort'")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
		$sth->execute();
		while (@row = $sth->fetchrow_array()) {
			printFehler("Zimmernummer bereits von ".decode("utf-8", $row[0])." belegt. Unbedingt &uuml;berpr&uuml;fen und alten User ggf. l&ouml;schen!</font></b>");
			printFehler("Room number already occupied by ".decode("utf-8", $row[0]).". Check is essential. Delete old user, if necessary!</font></b>");
		}
		my @randpw = `apg`;
		my $pw = $randpw[0];
		printFehler("<br>Es wurde folgendes Passwort generiert: <b>$pw</b>");
		printFehler("<br>The following password has been generated: <b>$pw</b><br>");
		$pw = crypt($pw, "ps");
		my $punkte;
		if ($altBewohner == 1) {
			$punkte = 0;
		} else {
			$punkte = 2;
			$altBewohner = 0;
		}
		if ($verlauf != 1) {
			$verlauf = 0;
		}
		my $sql = "INSERT INTO userlist ( id , pw , punktestand , agnutzung , status , eintragung , bearbeiter, nachricht ) VALUES ('$id', '$pw', '$punkte', '1', '1', NOW(), '$gId', '')";
		$sth = $dbh->prepare($sql) || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		$sth->execute() || die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
		printFehler("Der User Nummer - $id - wurde erfolgreich erstellt!");
		printFehler("User number - $id - was created successfully!");
	} else {
		gibNewForm($name, $nachname, $haus, $zimmer, $altBewohner, $verlauf);
	}
	$dbh->disconnect;
}

# Hilfsfunktion, die Texte darauf überprüft, ob sie leer sind
# param zu untersuchender String, Bezeichnung für Fehlermeldung
sub notLeer {
	my $string = shift;
	my $bezeichnung = shift;
	if ($string eq ""){
		printFehler("$bezeichnung muss ausgef&uuml;llt werden!");
		printFehler("$bezeichnung has to be filled in!");
		return (1);
	}
	return (0);
}

# Hilfsfunktion, die überprüft, ob es sich um ein mögliches TvK-Zimmer handelt
# param zu untersuchender String, Bezeichnung für Fehlermeldung
sub isValidZimmer {
	my $zimmerzeiger = shift;
	my $haus = shift;
	${$zimmerzeiger} = int(${$zimmerzeiger});
	my $zimmer = ${$zimmerzeiger};
	if ($haus eq "TVK") {
		if (int($zimmer / 100) >= 1 && int($zimmer / 100) <= 15 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 16)){
			# gut
		} elsif (int($zimmer) == 0 || int($zimmer) == 1 || int($zimmer) == 3 || int($zimmer) == 4) {
			# gut
		} else {
			printFehler("Zimmernummer ung&uuml;ltig!");
			printFehler("Invalid room number!");
			return (1);
		}
	} elsif ($haus eq "WEH") {
		if (int($zimmer / 100) >= 1 && int($zimmer / 100) <= 17 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 16)){
			# gut
		} elsif (int($zimmer) == 0 || int($zimmer) == 1) {
			# gut
		} else {
			printFehler("Zimmernummer ung&uuml;ltig!");
			printFehler("Invalid room number!");
			return (1);
		}
	} elsif ($haus eq "OPH") {
		if (int($zimmer / 100) >= 1 && int($zimmer / 100) <= 4 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 16)){
			# gut
		} elsif (int($zimmer / 100) >= 5 && int($zimmer / 100) <= 17 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 10)){
			# gut
		} elsif (int($zimmer) == 0) {
			# gut
		} else {
			printFehler("Zimmernummer ung&uuml;ltig!");
			printFehler("Invalid room number!");
			return (1);
		}
	} elsif ($haus eq "OIH") {
		if (int($zimmer / 100) >= 1 && int($zimmer / 100) <= 4 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 16)){
			# gut
		} elsif (int($zimmer / 100) >= 5 && int($zimmer / 100) <= 15 && ($zimmer % 100 >= 1 && $zimmer % 100 <= 10)){
			# gut
		}elsif (int($zimmer) == 0 || int($zimmer) == 1) {
			# gut
		} else {
			printFehler("Zimmernummer ung&uuml;ltig!");
			printFehler("Invalid room number!");
			return (1);
		}
	}
	# auf 4 Ziffern auffuellen und ab dafuer
	for (my $i = 0; $i < 4 - length(${$zimmerzeiger}); $i++) {
		${$zimmerzeiger} = "0".${$zimmerzeiger};
	}
	return (0);
}




# ----- AG-NUTZUNGSLISTE EINSEHEN -----

sub look_ag_use {
	my $sth = $dbh->prepare("SELECT id, agnutzung FROM userlist ORDER BY id ASC")||die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";
	$sth->execute();
	my @row;
	my $farbe;
	print "<table cellspacing=\"5\" cellpadding=\"3\" width=\"100%\">";
	print "<tr><th align=\"center\">"."<font color=\"black\">ID</th><th align=\"center\">AG-Nutzung<br>AG use</th></font></tr>";
	while (@row = $sth->fetchrow_array()) {
		if ($row[1] == 1) {
			$farbe = "black";
		} elsif ($row[1] == 0) {
			$farbe = "red";
		} else {
			$farbe = "orange";
		}
		print "<tr>";
		foreach (@row) {
			print "<td align=\"center\">"."<font color=\"$farbe\">".decode("utf-8", $_)."</font>"."</td>";
		}
		print "</tr>";
	}
	print "</table>";
}

# ----- AG-NUTZUNGSLISTE EINSEHEN ENDE -----



# ----- STATISTIKEN -----

#gibt dolle Statistiken aus
sub statistik {
	# wie viele User
	my $sth = $dbh->prepare("SELECT count(*) FROM userlist WHERE status < $god")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @row;
	@row = $sth->fetchrow_array();
	my $anzahlLeute = $row[0];

	# boese Mitbewohner
	$sth = $dbh->prepare("SELECT count(*) FROM userlist WHERE status < $god AND agnutzung = 0")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlSperre = int($row[0]);
	
	# brave Mitbewohner
	$sth = $dbh->prepare("SELECT count(*) FROM userlist WHERE status < $god AND agnutzung = 1")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $brav = int($row[0]);
	
	# Sparer
	$sth = $dbh->prepare("SELECT count(*) FROM userlist WHERE status < $god AND agnutzung = 0 AND punktestand >= 2")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $sparen = int($row[0]);

	# Etagenverteilung boese Mitbewohner
	$sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4) FROM userlist WHERE status < $god AND agnutzung = 0")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @btvketage;
	my @bophetage;
	my @boihetage;
	my @bwehetage;
	for (my $i = 0; $i <= 17; $i++) {
		$bophetage[$i] = 0;
		$bwehetage[$i] = 0;
	}
	for (my $i = 0; $i <= 15; $i++) {
		$btvketage[$i] = 0;
		$boihetage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[0]%100)/100;
		if ($row[0] eq "TVK") {
			$btvketage[$temp] += 1;
		} elsif ($row[0] eq "OPH") {
			$bophetage[$temp] += 1;
		} elsif ($row[0] eq "OIH") {
			$boihetage[$temp] += 1;
		} elsif ($row[0] eq "WEH") {
			$bwehetage[$temp] += 1;
		}
	}
	
	# Etagenverteilung brave Mitbewohner
	$sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4) FROM userlist WHERE status < $god AND agnutzung = 1")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @tvketage;
	my @ophetage;
	my @oihetage;
	my @wehetage;
	for (my $i = 0; $i <= 17; $i++) {
		$ophetage[$i] = 0;
		$wehetage[$i] = 0;
	}
	for (my $i = 0; $i <= 15; $i++) {
		$tvketage[$i] = 0;
		$oihetage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[0]%100)/100;
		if ($row[0] eq "TVK") {
			$tvketage[$temp] += 1;
		} elsif ($row[0] eq "OPH") {
			$ophetage[$temp] += 1;
		} elsif ($row[0] eq "OIH") {
			$oihetage[$temp] += 1;
		} elsif ($row[0] eq "WEH") {
			$wehetage[$temp] += 1;
		}
	}

	# wie viele Verlauf haben wollen
	$sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4) FROM userlist WHERE status < $god AND verlauf = 1")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @vtvketage;
	my @vophetage;
	my @voihetage;
	my @vwehetage;
	my $vtvk = 0;
	my $vweh = 0;
	my $voph = 0;
	my $voih = 0;
	for (my $i = 0; $i <= 17; $i++) {
		$vophetage[$i] = 0;
		$vwehetage[$i] = 0;
	}
	for (my $i = 0; $i <= 15; $i++) {
		$vtvketage[$i] = 0;
		$voihetage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[0]%100)/100;
		if ($row[0] eq "TVK") {
			$vtvketage[$temp] += 1;
			$vtvk += 1; 
		} elsif ($row[0] eq "OPH") {
			$vophetage[$temp] += 1;
			$voph += 1;
		} elsif ($row[0] eq "OIH") {
			$voihetage[$temp] += 1;
			$voih += 1;
		} elsif ($row[0] eq "WEH") {
			$vwehetage[$temp] += 1;
			$vweh += 1;
		}
	}
	
	# wie viele Verlauf nicht haben wollen
	$sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4) FROM userlist WHERE status < $god AND verlauf = 0")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @nvtvketage;
	my @nvophetage;
	my @nvoihetage;
	my @nvwehetage;
	my $nvtvk = 0;
	my $nvweh = 0;
	my $nvoph = 0;
	my $nvoih = 0;
	for (my $i = 0; $i <= 17; $i++) {
		$nvophetage[$i] = 0;
		$nvwehetage[$i] = 0;
	}
	for (my $i = 0; $i <= 15; $i++) {
		$nvtvketage[$i] = 0;
		$nvoihetage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[0]%100)/100;
		if ($row[0] eq "TVK") {
			$nvtvketage[$temp] += 1;
			$nvtvk += 1; 
		} elsif ($row[0] eq "OPH") {
			$nvophetage[$temp] += 1;
			$nvoph += 1;
		} elsif ($row[0] eq "OIH") {
			$nvoihetage[$temp] += 1;
			$nvoih += 1;
		} elsif ($row[0] eq "WEH") {
			$nvwehetage[$temp] += 1;
			$nvweh += 1;
		}
	}

	# wie viele Haussprecher
	$sth = $dbh->prepare("SELECT count(*) FROM userlist WHERE status = $admin")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlHS = $row[0];
	
	# wie viele Gremiumsmitglieder
	$sth = $dbh->prepare("SELECT count(*) FROM userlist WHERE status = $gremium")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	@row = $sth->fetchrow_array();
	my $anzahlGremium = $row[0];

	# wie viele AG-Mitglieder
	$sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4) FROM userlist WHERE status = $agmitglied")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @atvketage;
	my @aophetage;
	my @aoihetage;
	my @awehetage;
	my $atvk = 0;
	my $aweh = 0;
	my $aoph = 0;
	my $aoih = 0;
	for (my $i = 0; $i <= 17; $i++) {
		$aophetage[$i] = 0;
		$awehetage[$i] = 0;
	}
	for (my $i = 0; $i <= 15; $i++) {
		$atvketage[$i] = 0;
		$aoihetage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[0]%100)/100;
		if ($row[0] eq "TVK") {
			$atvketage[$temp] += 1;
			$atvk += 1; 
		} elsif ($row[0] eq "OPH") {
			$aophetage[$temp] += 1;
			$aoph += 1;
		} elsif ($row[0] eq "OIH") {
			$aoihetage[$temp] += 1;
			$aoih += 1;
		} elsif ($row[0] eq "WEH") {
			$awehetage[$temp] += 1;
			$aweh += 1;
		}
	}

	# wie viele Punkte pro Turm und Etage
	$sth = $dbh->prepare("SELECT SUBSTR(id, 1, 3), SUBSTR(id, 5, 4), punktestand FROM userlist WHERE status < $god")|| die "Fehler bei der Datenverarbeitung! $DBI::errstr\n";	# bereitet den befehl vor
	$sth->execute();
	my @ptvketage;
	my @pophetage;
	my @poihetage;
	my @pwehetage;
	my $ptvk = 0;
	my $pweh = 0;
	my $poph = 0;
	my $poih = 0;
	for (my $i = 0; $i <= 17; $i++) {
		$pophetage[$i] = 0;
		$pwehetage[$i] = 0;
	}
	for (my $i = 0; $i <= 15; $i++) {
		$ptvketage[$i] = 0;
		$poihetage[$i] = 0;
	}
	while (@row = $sth->fetchrow_array()) {
		my $temp = ($row[1] - $row[0]%100)/100;
		if ($row[0] eq "TVK") {
			$ptvketage[$temp] += $row[2];
			$ptvk += $row[2]; 
		} elsif ($row[0] eq "OPH") {
			$pophetage[$temp] += $row[2];
			$poph += $row[2];
		} elsif ($row[0] eq "OIH") {
			$poihetage[$temp] += $row[2];
			$poih += $row[2];
		} elsif ($row[0] eq "WEH") {
			$pwehetage[$temp] += $row[2];
			$pweh += $row[2];
		}
	}

	# Ausgabe
	my $color = "#000000";
	print "<b>Userstatistiken</b><br>";
	print "Es sind derzeit <b>$anzahlLeute</b> User angemeldet. <br> Davon sind <b>$brav</b> Leute f&uuml;r AG-Nutzung freigeschaltet. <b>$anzahlSperre</b> waren faule S&auml;cke und sind's nicht. Davon wiederum h&auml;tten <b>$sparen</b> Leute genug Punkte, um die AG-Nutzung freizuschalten, scheinen aber zu sparen.<br><br>";
	print "Freigeschaltete / Gesperrte Leute<table width=\"100%\"><tr><th align=\"center\">Etage</th><th align=\"center\">OPH</th><th align=\"center\">OIH</th><th align=\"center\">TVK</th><th align=\"center\">WEH</th></tr>";
	for (my $i = 0; $i <= 15; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$ophetage[$i]/$bophetage[$i]</td><td align=\"center\">$oihetage[$i]/$boihetage[$i]</td><td align=\"center\">$tvketage[$i]/$btvketage[$i]</td><td align=\"center\">$wehetage[$i]/$bwehetage[$i]</td></font></tr>";
	}
	for (my $i = 16; $i <= 17; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$ophetage[$i]/$bophetage[$i]</td><td align=\"center\"></td><td align=\"center\"></td><td align=\"center\">$wehetage[$i]/$bwehetage[$i]</td></font></tr>";
	}
	print "</table><br><br>";
	print "Es gibt insgesamt ".($poph+$ptvk+$pweh+$poih)." Punkte auf allen Konten.<br>";
	print "Punkteverteilung:<table width=\"100%\"><tr><th align=\"center\">Etage</th><th align=\"center\">OPH<br>$poph Punkte</th><th align=\"center\">OIH<br>$poih Punkte</th><th align=\"center\">TVK<br>$ptvk Punkte</th><th align=\"center\">WEH<br>$pweh Punkte</th></tr>";
	for (my $i = 0; $i <= 15; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$pophetage[$i]</td><td align=\"center\">$poihetage[$i]</td><td align=\"center\">$ptvketage[$i]</td><td align=\"center\">$pwehetage[$i]</td></font></tr>";
	}
	for (my $i = 16; $i <= 17; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$pophetage[$i]</td><td align=\"center\"></td><td align=\"center\"></td><td align=\"center\">$pwehetage[$i]</td></font></tr>";
	}
	print "</table><br>";
	print "Es wollen <b>".($voph+$vtvk+$vweh+$voih)."</b> Leute den <b>Verlauf</b> und sind keine \"WU&Auml;&Auml;H-aber-der-Datenschutz\"-Heulsusen. <b>".($nvoph+$nvtvk+$nvweh+$nvoih)."</b> sind allerdings so weinerlich.<br>";
	print "Verteilung:<table width=\"100%\"><tr><th align=\"center\">Etage</th><th align=\"center\">OPH<br>$voph/$nvoph Verl&auml;ufe<br>ja/nein</th><th align=\"center\">OIH<br>$voih/$nvoih Verl&auml;ufe<br>ja/nein</th><th align=\"center\">TVK<br>$vtvk/$nvtvk Verl&auml;ufe<br>ja/nein</th><th align=\"center\">WEH<br>$vweh/$nvweh Verl&auml;ufe<br>ja/nein</th></tr>";
	for (my $i = 0; $i <= 15; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$vophetage[$i]/$nvophetage[$i]</td><td align=\"center\">$voihetage[$i]/$nvoihetage[$i]</td><td align=\"center\">$vtvketage[$i]/$nvtvketage[$i]</td><td align=\"center\">$vwehetage[$i]/$nvwehetage[$i]</td></font></tr>";
	}
	for (my $i = 16; $i <= 17; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$vophetage[$i]/$nvophetage[$i]</td><td align=\"center\"></td><td align=\"center\"></td><td align=\"center\">$vwehetage[$i]/$nvwehetage[$i]</td></font></tr>";
	}
	print "</table><br>";
	print "Es gibt <b>$anzahlHS Haussprecher</b> und <b>$anzahlGremium Gremiumsmitglieder</b>.<br><br>";
	print "Es gibt insgesamt <b>".($aoph+$atvk+$aweh+$aoih)." AG-Mitglieder</b> in den T&uuml;rmen.<br>";
	print "Verteilung:<table width=\"100%\"><tr><th align=\"center\">Etage</th><th align=\"center\">OPH<br>$poph Mitglieder</th><th align=\"center\">OIH<br>$poih Mitglieder</th><th align=\"center\">TVK<br>$ptvk Mitglieder</th><th align=\"center\">WEH<br>$pweh Mitglieder</th></tr>";
	for (my $i = 0; $i <= 15; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$aophetage[$i]</td><td align=\"center\">$aoihetage[$i]</td><td align=\"center\">$atvketage[$i]</td><td align=\"center\">$awehetage[$i]</td></font></tr>";
	}
	for (my $i = 16; $i <= 17; $i++) {
		if ($i%2==0) {
			$color = "#88aa88";
		} else {
			$color = "#000000";
		}
		print "<tr><font color=\"$color\"><td align=\"center\">$i</td><td align=\"center\">$aophetage[$i]</td><td align=\"center\"></td><td align=\"center\"></td><td align=\"center\">$awehetage[$i]</td></font></tr>";
	}
	print "</table><br>";
}


# ----- STATISTIKEN ENDE -----


# ----- SICHERHEITSRELEVANTE HILFSFUNKTIONEN ------
 
# entfernt böse Zeichen ausm String ;)
sub makeclean {
	my $text = shift;
	$text =~ s/"//g;
	$text =~ s/'//g;
	$text =~ s/;//g;
	return ($text);
}



# ----- ENDE SICHERHEITSRELEVANTE HILFSFUNKTIONEN ------

# formatiert Texte fuer MySQL, codiert Sonderzeichen
sub vorbereiten {
	my $string = shift;
	$string = $dbh->quote(encode("utf-8", $string));
	return ($string);
}

sub printFehler {
	my $fehler = shift;
	print "$fehler<br>";
}
