package Dateutils;

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
1; # MUST BE LAST STATEMENT IN FILE
