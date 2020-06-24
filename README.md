# CrimeAnalysis
## python virtual env and how to execute

In order to run the framework, first prepare your python virtualenv and download the required modules.
Use following commands to create virtual env. and download required modules.

***Commands are specific to CentOS, commands which doesn't works for your system you can find similar commands for them on internet. 
--

1. Create virtual env.
	$ python3.7 -m venv env_name

2. Activate the env and download the required modules using requirements.txt file present in download_requirements folder.
	$ pip install -r ./download_requirements/requirements.txt 

	**(provided you are inside Crime-Analysis-BTP folder or provide path of requirements.txt file.)
3. Run the below command to download pretranined statistical models for English
	$ python -m spacy download en

4. Run following command to downoad NLTK dependencies with your env active.
	$ python ./download_requirements/nltk_downloads.py

With this your python virtual env is ready.

To run the framework do the following.
	1. Find the path of your python bin folder of python virtual env.
		will look like : "/home/2016CSB1059/project_env/bin/python"
			i.e. {path_to_env_folder}/{env_folder_name}/bin/python
	2. paste this path in the first line of part1.py file, should look like:
		#!/home/2016CSB1059/project_env/bin/python

Now you are ready to run the framework. 

Run the run.sh file in the Crime-Analysis-BTP folder.
	$ ./run.sh

***run this file from Crime-Analysis-BTP only, if you aim to run this file from another folder then change the line no. 9 and 11 in run.sh file. Instead of part1.py make them the {absolute_path_to_part1.py}/part1.py
--
Apart from this, One more dependency is there, and it is Stanford Taggers.
There are three stanford zip files that needed to be downloaded from here: https://nlp.stanford.edu/software/
Names are:
	1) stanford-ner-2015-04-20.zip
	2) stanford-parser-full-2015-04-20.zip
	3) stanford-postagger-full-2015-04-20.zip

Once you download this, unzip them in some folder and then change in run.sh file in line number 3.
STANFORDTOOLSDIR="path_of_folder_containing_extracted_zip_files"


## DATABASE

The name of DB : CRIME_ANALYSIS

To see database details, follow below steps:
	$ mysql -u root -p
	 -- it will ask for password. (Password if "root").

	--Change to our DB.
	mysql> use CRIME_ANALYSIS

	--To see tables.
	mysql> show tables;

	+--------------------------+
	| Tables_in_CRIME_ANALYSIS |
	+--------------------------+
	| Articles                 |
	| CrimeNewsDetails         |
	| LocationInfo             |
	| MaxScore                 |
	| NewsArticles             |
	| NonCrimeArticles         |
	| words                    |
	+--------------------------+

	** These are the tables used in this project.

	"Articles" - old table to store News Articles crawled from net.
	This is now shifted to "NewsArticles" table.

	"CrimeNewsDetails" - This table stores tagged data of crime articles.
	"LocationInfo"     - This table stores geo-coordinates, crimescore and other info of locations.
	"MaxScore"         - This table stores max crime score from LocationInfo table.
	"words"			   - This table stores words and their misspellings.

	To see columns and more details of tables use below command:
	mysql> desc table_name;



## API Details

We have used 2 APIs in this project:
	1. BING spell check
	2. LocationIQ

APIs.py in Crime-Analysis-BTP folder contains class for both apis to make request to respective api as required.
Look APIs.py for more details.

-- BING spell check API has limited request for single account therefore we store each made request in our DB.
-- LocationIQ API has daily limit therefore DB is mainitained, also if daily request exceeds we sleep make the framework to sleep till next day to make new request. 

***Both API class in APIs.py has API-KEY and endpoint mentioned. Youca n change the API-KEY for both APIs in respective class.


## Interface

We have created an interface to see the crime score of locations using Flask and python.

Crime-Analysis-BTP/web_query_api contains all the files of web interface. 

To run the interface on browser run the "location_details_api.py" in background, then use the following url:
	172.26.5.254:5000/
	172.26.5.254 - IP of the server
	5000 		 - PORT at which the framework is runnning.
	--- You can also see this IP and port details by running "location_details_api.py" file in caseit changes.



## Crime Data Tagging 

We made a system to tag crime news details. 
We used PHP for this purpose. 
There are two php files in /var/www/html folder, namely "login.php" and "summer.php"

login.php - Just a user data system that takes the name of the user that is about to tag data.
summer.phph - Has the actual logic to run and execute tagging.

Apart from this two more python file is involved that returns the entities for tagging so that tagging becomes more convinient. (CrimeCheck_v2.py and entityExtraction.py)

If you want to do tagging
go to your browser and type following URL:
	172.26.5.254/login.php
	172.26.5.254 - IP of the server

These files are also present in Crime-Analysis-BTP/crime_tagging_files folder.
Also in summer.php line no. 207, where command is made for exec, change the filepath(i.e. absolute path of entityExtraction.py file). 
Also in entityExtraction.py, in first line change the python env that you made for this project(as directed in python virtual env section of this README). 
that looks like : #!/home/2016CSB1059/project_env/bin/python



