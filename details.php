<?php
$con=mysqli_connect("localhost","newuser","password","osm");
// Check connection
if (mysqli_connect_errno())
  {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }

// Perform queries
mysqli_query($con,"SELECT * FROM users");
mysqli_query($con,"INSERT INTO users (name,email,college,id)
VALUES ('$_POST[name]','$_POST[email]','$_POST[college]','$_POST[id]')");

mysqli_close($con);

header('Location: http://kluglug.tk/leaderboard')
?>
