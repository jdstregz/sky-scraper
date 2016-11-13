# sky-scraper
For all of your cloud-based-service price scraping needs

The example_output directory shows different approaches for the scraping results

Dependencies:
	- sudo pip install scrapy
	- sudo pip install psycopg2
	(possibly splash)

To run a spider

	1. Go into a prototype directory (aws example)
	2. run scrapy command with spider name:
		scrapy crawl aws
	3. results should appear after that (different for each prototype atm)


To run Postgres database: (this will eventually be dockerized for convenience)

(on osx) - $ sudo launchctl start com.edb.launchd.postgresql-9.6

To connect to postgres database:

psql -U (whatever user you initialized)
(enter password)

To stop Postgres instance:

(on osx) - $ sudo launchctl stop com.edb.launchd.postgresql-9.6

Sprint 2 completions

- got the schema
- went over dependencies and other methods of scraping
- went over dependencies for postgres database insertion
- started formulating a dockerized postgres container to avoid host-machine dependency
- started implementing psycopg2 dependency for postgres database insertion 
- successfully connected with postgres database and began testing proper insertion based on given schema

To do: 
- meet with stefan to go over details with database insertion and management
- go over retrieval and presentation of data once inserted
- begin learning on how to package python program into command line interface

Blockers:
- google cloud services changed their pricing pages (so scrapy has to be reformulated for that service)
- some data does not exist for postgres schema, and so stefan will have to look over alternative model 
