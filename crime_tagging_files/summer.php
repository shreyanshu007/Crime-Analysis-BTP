<!DOCTYPE html>
<html>
<head>

    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <link href="https://fonts.googleapis.com/css?family=Fira+Sans" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    

	<title>CRIME ANALYSIS</title>

	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
	<script type="text/javascript">
		var formSubmitting = false;
		var setFormSubmitting = function() { formSubmitting = true; };

		window.onload = function() {
		    window.addEventListener("beforeunload", function (e) {
		        if (formSubmitting) {
		            return undefined;
		        }

		        var confirmationMessage = 'It looks like you have been editing something. '
		                                + 'If you leave before saving, your changes will be lost.';

		        (e || window.event).returnValue = confirmationMessage; //Gecko + IE
		        return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
		    });
		};
	</script>


</head>
<body>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>




	<?php

		$servername = "localhost";
		$username = "root";
		$password = "root";
		$dbname = "CRIME_ANALYSIS";

		// Create connection
		$conn = new mysqli($servername, $username, $password, $dbname);
		// Check connection
		if ($conn->connect_error) {
		    die("Connection failed: " . $conn->connect_error);
		} 
		else{

			// echo "Connection established";
		}
		// session_start();
		$name = $_GET['name'];

	?>

	<form method="post" action="summer.php?name=<?php echo $name; ?>" onsubmit="setFormSubmitting()">
		<!-- IS this a crime article? -->
<!-- 		<input type="radio" name="crimeTag" value="yes" unchecked>YES
		<input type="radio" name="crimeTag" value="no" unchecked>NO -->
		<center>
    	<h2>Is this a crime article?</h2>
    	<button type="submit" class="btn btn-primary btn-lg" name="yesCrime">YES</button>
		<button type="submit" class="btn btn-primary btn-lg" name="noCrime">NO</button>
	</center>
		<!-- <input type="submit" name="submit"> -->
	</form>

	<?php
		
		// $servername = "localhost";
		// $username = "root";
		// $password = "root";
		// $dbname = "CRIME_ANALYSIS";

		// // Create connection
		// $conn = new mysqli($servername, $username, $password, $dbname);
		// // Check connection
		// if ($conn->connect_error) {
		//     die("Connection failed: " . $conn->connect_error);
		// } 
		// else{

		// 	// echo "Connection established";
		// }
		session_start();
		// $name = $_GET['name'];

		
		// $state_code = 0;
		// $text = $_SESSION['text'];
		$prevID = $_SESSION['NewsArticleId'];
		// echo 'text text'.$text;
		if(!isset($_POST['yesCrime']) and !isset($_POST['noCrime'])){

			$sql = "SELECT NewsArticleId, NewsArticleTitle, NewsArticleText, NewsArticleDate, NewsArticleUrl FROM NewsArticles WHERE (NewsArticleText LIKE '%rape%' OR NewsArticleText LIKE '%murder%' OR NewsArticleText LIKE '%robb%' OR NewsArticleText LIKE '%kill%') AND AnalyzedBy is NULL AND (NewsArticleUrl NOT LIKE '%ndtv.com%' AND NewsArticleUrl NOT LIKE '%timesofindia%') LIMIT 1";

			$results = $conn->query($sql);

			$rowCount = $results->num_rows;

		    if($rowCount > 0){

		        $row = $results->fetch_assoc();

		        // echo "<center>";
		        $textdata = $row['NewsArticleText'];
		        $date_from_text = preg_match_all("/First Published.*IST/", $textdata, $output);
		        // echo "DATE FROM TEXT: "."<br>";
		        
				echo '<div class="container"';
		        echo "<br><h3>NewsArticle Id: ".$row['NewsArticleId'];
		        echo "</h3><br><h4><b>NewsArticle Title: </b>".$row['NewsArticleTitle'];
		        echo "</h4><br><h6><b>NewsArticle Text: </b>".$row['NewsArticleText'];
		        if(strpos($row['NewsArticleUrl'], 'hindustantimes') !== false){
		        	echo "</h6><br><b>NewsArticle Date(YYYY-MM-DD HH:MM:SS): </b>";
		        	print_r($output[0][0]);
		        	$_SESSION['NewsArticleDate'] = $output[0][0];
		        }
		        else{
		        	echo "</h6><br><b>NewsArticle Date(YYYY-MM-DD HH:MM:SS): </b>".$row['NewsArticleDate'];
		        	$_SESSION['NewsArticleDate'] = $row['NewsArticleDate'];
		        }
		        
		        echo "<br><b>NewsArticle Url: </b>".$row['NewsArticleUrl'];
		        // echo "</center>";
		        echo '</div>';
		        $_SESSION['NewsArticleId'] = $row['NewsArticleId'];
		        $_SESSION['NewsArticleTitle'] = $row['NewsArticleTitle'];
		        $_SESSION['NewsArticleText'] = $row['NewsArticleText'];
		        
		        $_SESSION['NewsArticleUrl'] = $row['NewsArticleUrl'];
		        $text = $row['NewsArticleTitle'];
		        $text .= " ";
		        $text .= $row['NewsArticleText'];
		        // $_GET['count'] = 1;
		        // echo "<br>".$_SESSION['text'];

		        $id = $_SESSION['NewsArticleId'];

		        $sql = "UPDATE NewsArticles SET AnalyzedBy = '$name', TimeStamp = CURRENT_TIMESTAMP WHERE NewsArticleID = '$id'";
				if ($conn->query($sql) === TRUE) {
				    // echo "1Record updated successfully";
				} else {
				    // echo "1Error updating record: " . $conn->error;
				}
				// echo '<form method="post">
				// 		IS this a crime article?
				// 		<input type="radio" name="crimeTag" value="yes" unchecked>YES
				// 		<input type="radio" name="crimeTag" value="no" unchecked>NO
				// 		<input type="submit" name="submit">
				// 	</form>';

		    }else{
		        echo 'NO Results';
		    }
		}
	    

	?>

	

	<?php

		// function run_crime(){
		if(isset($_POST['yesCrime'])){

			echo '<div class="container"';
		    // echo "<center>";
	        echo '<center><b><u><h3><font color="red">Please Scroll down to fill Required details</font></h3></u></b></center>
	        <br><h3>NewsArticle Id: '.$_SESSION['NewsArticleId'];
	        echo "</h3><br><h4><b>NewsArticle Title: </b>".$_SESSION['NewsArticleTitle'];
	        echo "</h4><br><h6><b>NewsArticle Text: </b>".$_SESSION['NewsArticleText'];
	        echo "</h6><br><b>NewsArticle Date(YYYY-MM-DD HH:MM:SS): </b>".$_SESSION['NewsArticleDate'];
	        echo "<br><b>NewsArticle Url: </b>".$_SESSION['NewsArticleUrl'];
	        echo '</div>';

	  //	   echo "<b><u>NewsArticle Id: </u>".$_SESSION['NewsArticleId'];
	  //       echo "<br><u>NewsArticle Title: </u>".$_SESSION['NewsArticleTitle'];
	  //       echo "<br><u>NewsArticle Text: </u></b>".$_SESSION['NewsArticleText'];
	  //       echo "<br><b><u>NewsArticle Date(YYYY-MM-DD HH:MM:SS): </u></b>".$_SESSION['NewsArticleDate'];
	  //       echo "<br><b><u>NewsArticle Url: </u></b>".$_SESSION['NewsArticleUrl'];

	        // echo "</center>";

	        $text = $_SESSION['NewsArticleTitle']." ".$_SESSION['NewsArticleText'];
	        $text = str_replace('"', '', $text);

		    $command = escapeshellcmd('/home/2016CSB1059/Crime_analysis/SummerProject/bin/entityExtraction.py "'.$text.'"');

		    $row = shell_exec($command);
			//print($row);
			$exploded = explode(';',$row);
			 //echo $exploded;

			// $num = $num+1;/

	        echo "<center>";

			echo '<form method="post" action="insert_crime.php?name='.$name.'"  onsubmit="setFormSubmitting()">';
			

			function validate_alphanumeric_underscore($str) {

			    return preg_match('/^[a-zA-Z0-9_ ]+$/',$str);
			}
			$count = 0;
			
			function makeEntityTable($entityType, $entities){

				
				echo '<table border="5" align="left">';
				$_SESSION[$entityType] = $entities;

				echo   '<tr>
						<th> '.$entityType.' </th>
						<th> Yes </th>
						<th> No </th>
						</tr>';

				

				$explodedEntities = explode('|', $entities);
				sort($explodedEntities);
				foreach ($explodedEntities as $key) {

					// echo $key;

					if(!validate_alphanumeric_underscore($key)){
						continue;
					}

					echo   '<tr>
							<td>'.$key.'</td>';

					$key = str_replace(" ", "_", $key);
					$key = $entityType.$key;

					echo   '<td> <input type="radio" value="yes" name="'.$key.'" > YES </td>
							<td> <input type="radio" value="no" name="'.$key.'" checked="checked"> No </td>
							</tr>';
				}
				echo "</table>";
				
			}

			$Names = $exploded[0];
			$Locations = $exploded[1];
			$crimeWordsList = $exploded[2];

			// echo '<div class="col-container">';
			// echo '<div class="col">';
			echo "<br><b>Please check Yes for those entities which you think belongs to correct table.</b><br><br>";
			makeEntityTable("Criminals", $Names);
			// echo '</div>';
			// echo '<div class="col">';
			makeEntityTable("Victims", $Names);
			// echo '</div>';
			// echo '</div>';
			makeEntityTable("CrimeLocations", $Locations);
			makeEntityTable("CrimeWordList", $crimeWordsList);
			

			
			// echo '<br>Extra Criminals: <textarea rows="4" cols="50" name="extraCriminalNames"></textarea><br><br>';
			// echo '<br>Extra Victims: <textarea rows="4" cols="50" name="extraVictimNames"></textarea><br><br>';
			// echo '<br>Extra location: <textarea rows="4" cols="50" name="extraLocations"></textarea><br><br>';
			// echo '<br>Extra crime-word-list: <textarea rows="4" cols="50" name="extraCrimeWordList"></textarea><br><br>';
			// echo 'Rate the severity of crime on a scale of(0-5): <input type="number" name="severity" step="0.1" min="0.0" max="5.0">';

			// echo '<br>If you able to figure DATE from the NEWS except from the published date please mention(Otherwise mention NA - FORMAT: YYYY/MM/DD): <input type="text" name="date">';

			// echo '<br>How old the news is from the published date: ';
			// echo '<br><input type="radio" name="articleAge" value="one day">One Day
			// 		<br><input type="radio" name="articleAge" value="one week">One Week
			// 		<br><input type="radio" name="articleAge" value="one month">One Month
			// 		<br><input type="radio" name="articleAge" value="less than a year">Less than a year
			// 		<br><input type="radio" name="articleAge" value="one year">One Year
			// 		<br><input type="radio" name="articleAge" value="more than one year">More than One year';

			// echo '<br><input type="submit">';


			// echo "</form>";

	        echo "</center>";


	        
			echo '<br>

			<div class="container">
				<form>

				  <div class="form-group">
				    <label for="Extra Criminal Names"><b>Extra Criminal Names: </b>(use \'|\' to separate two names instead of spaces eg. Ram Nath and Shyam should be written as Ram Nath|Shyam)</label>
				    <textarea class="form-control" id="exampleFormControlTextarea1" rows="2" name="extraCriminalNames"></textarea>
				  </div>

				  <div class="form-group">
				    <label for="Extra Victim Names"><b>Extra Victim Names: </b>(use \'|\' to separate two names instead of spaces)</label>
				    <textarea class="form-control" id="exampleFormControlTextarea1" rows="2" name="extraVictimNames"></textarea>
				  </div>

				  <div class="form-group">
				    <label for="Extra Locations"><b>Extra Crime Locations: </b>(use \'|\' to separate two locations instead of spaces)</label>
				    <textarea class="form-control" id="exampleFormControlTextarea1" rows="3" name="extraLocations"></textarea>
				  </div>

				  <div class="form-group">
				    <label for="Extra Crime Words"><b>Extra Crime Words: </b>(use \'|\' to separate two words instead of spaces)</label>
				    <textarea class="form-control" id="exampleFormControlTextarea1" rows="3" name="extraCrimeWordList"></textarea>
				  </div>

				  <div class="form-group">
				    <label for="published date"><b>How old the news is from the published date</b></label>
				    <select class="form-control" id="exampleFormControlSelect1" name="articleAge">
				      <option>One Day</option>
				      <option>Less than a week</option>
				      <option>One Week</option>
				      <option>Less than a month</option>
				      <option>One Month</option>
				      <option>Less than half year</option>
				      <option>Less than a year</option>
				      <option>One Year</option>
				      <option>More than one year</option>
				      <option>More than two year</option>
				      <option>Cannot say</option>
				    </select>
				  </div>


				

				  <div class="form-group">
				    <label for="Extra Date"><b>If you able to figure DATE from the NEWS except from the published date please mention<br></b>(FORMAT: any(YYYY/MM/DD or YYYY/MM or YYYY))</label>
				    <textarea class="form-control" id="exampleFormControlTextarea1" rows="1" name="date">NA</textarea>
				  </div>

				  <div class="form-group row">
				    <div class="col-sm-10">
				      <button type="submit" class="btn btn-primary">Submit</button>
				    </div>
				  </div>

				</form>
			</div>	

			';

			// echo '
			// 	<center>
			// 	<br>
		 //    	<button type="button" class="btn btn-primary btn-lg">One Day</button>
			// 	<button type="button" class="btn btn-primary btn-lg">One Week</button>
		 //    	<button type="button" class="btn btn-primary btn-lg">One Month</button>
			// 	<button type="button" class="btn btn-primary btn-lg">Less than a year</button>
		 //    	<button type="button" class="btn btn-primary btn-lg">One Year</button>
			// 	<button type="button" class="btn btn-primary btn-lg">More than one year</button>
			// 	</center>
			// 	<br>
			// 	';
			

			// $_SESSION['text'] = NULL;

			
		}
		if(isset($_POST['noCrime'])){
			// $id1 = $_SESSION['id'];
			// echo $id;
			$sql = "SELECT * from NewsArticles";
			if ($conn->query($sql) === TRUE) {
			    // echo "2Record updated successfully";
			} else {
			    // echo "2Error updating record: " . $conn->error;
			}
			$sql = "UPDATE NewsArticles SET NewsType = 'non-crime' WHERE NewsArticleID = '$prevID'";
			if ($conn->query($sql) === TRUE) {
			    // echo "Record updated successfully";
			} else {
			    // echo "Error updating record: " . $conn->error;
			}
			// $conn->commit();
			unset($_POST['noCrime']);
			header("Location: summer.php?name=$name");
			$_SESSION['text'] = NULL;
		}

		function non_crime(){
			if(isset($_POST['noCrime'])){
				// $id1 = $_SESSION['id'];
				// echo $id;
				$sql = "SELECT * from NewsArticles";
				if ($conn->query($sql) === TRUE) {
				    // echo /"2Record updated successfully";
				} else {
				    // echo "2Error updating record: " . $conn->error;
				}
				$sql = "UPDATE NewsArticles SET NewsType = 'non-crime' WHERE NewsArticleID = '$id'";
				if ($conn->query($sql) === TRUE) {
				    // echo "Record updated successfully";
				} else {
				    // echo "Error updating record: " . $conn->error;
				}
				// $conn->commit();
				unset($_POST['noCrime']);
				// $_SESSION['text'] = NULL;
				header("Location: summer.php?name=$name");
			}
		}

		$conn->close();

	?>





</body>
</html>
