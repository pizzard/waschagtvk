<?php
header("Content-Type: text/calendar");
header('Content-Disposition: attachment; filename="Waschterminexport.ics"');
if (!isset($_GET['id'])) {
  echo "please provide an id. you can create one by concating pw and login und running sha1 with 160bit on them";
} else {
  $mysqli = new mysqli('137.226.142.1','waschag','4m_P06i!','waschag');
  $id =  $mysqli->real_escape_string($_GET['id']);
  $query_for_userid = 'select id from users where sha(concat(pw,login))=\''.$id.'\'';
  $userid_result = $mysqli->query($query_for_userid);
  if ($userid_result->num_rows != 1) {
    echo 'user not found. maybe the id is wrong';
  } else {
    echo 'BEGIN:VCALENDAR'."\r\n";
    echo 'VERSION:2.0'."\r\n";
    $row = $userid_result->fetch_array(MYSQLI_NUM);
    $userid = $row[0];
    //$query_for_termine = 'select unix_timestamp(datum)+(zeit*90*60) as date,maschine from termine;';
    $query_for_termine = 'select unix_timestamp(datum)+(zeit*90*60) as date,maschine from termine where user='.$userid;
    $termine_result = $mysqli->query($query_for_termine);

    date_default_timezone_set("Europe/Berlin");

    $dateTimeZoneBerlin = new DateTimeZone("Europe/Berlin");
    $dateTimeZoneUTC = new DateTimeZone("UTC");

    while($termin = $termine_result->fetch_array(MYSQLI_NUM)) {
      $begin_waschen = new DateTime();
      $begin_waschen->setTimezone($dateTimeZoneBerlin);
      $begin_waschen->setTimestamp($termin[0]);
      $begin_waschen->setTimezone($dateTimeZoneUTC);
      $end_waschen = new DateTime();
      $end_waschen->setTimezone($dateTimeZoneBerlin);
      $end_waschen->setTimestamp($termin[0]+90*60);
      $end_waschen->setTimezone($dateTimeZoneUTC);
      $end_trocknen = new DateTime();
      $end_trocknen->setTimezone($dateTimeZoneBerlin);
      $end_trocknen->setTimestamp($termin[0]+180*60);
      $end_trocknen->setTimezone($dateTimeZoneUTC);
      //$begin_waschen = date('Ymd\THis\Z',$termin[0]);
      //$end_waschen = date('Ymd\THis\Z',$termin[0]+90*60);
      //$end_trocknen = date('Ymd\THis\Z',$termin[0]+180*60);
      echo 'BEGIN:VEVENT'."\r\n";
      echo 'DTSTART:'.$begin_waschen->format('Ymd\THis\Z')."\r\n";
      echo 'DTEND:'.$end_waschen->format('Ymd\THis\Z')."\r\n";
      echo 'SUMMARY:Waschtermin Maschine '.$termin[1]."\r\n";
      echo 'END:VEVENT'."\r\n";
      echo 'BEGIN:VEVENT'."\r\n";
      echo 'DTSTART:'.$end_waschen->format('Ymd\THis\Z')."\r\n";
      echo 'DTEND:'.$end_trocknen->format('Ymd\THis\Z')."\r\n";
      echo 'SUMMARY:Trockner Maschine '.$termin[1]."\r\n";
      echo 'END:VEVENT'."\r\n";
    }
  }
  echo 'END:VCALENDAR';
  $userid_result->close();
  $mysqli->close();
}
?>
