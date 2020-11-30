# Repository Description
The code here is the data collection and database upload/design code for an app. The objective of the app was to show what legislation senators and house members have/had voted for. This repository will include one of the crawlers I built, the database interface class, and some of the code that uploaded to the database from the locally stored files. The database was deployed using Google Firebase

## Structure Notes
firebase_database.py contains the primary class definitions used for uploading data to the database, and the class that handles the database interface. /main contains the files that automated crawling, updating the local files, then uploading changes to the database. /web_crawlers contains several different crawlers, and /utils contains several miscellaneous functions to keep code elsewhere clean.
