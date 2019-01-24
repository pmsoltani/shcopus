# SHcopus

*Pooria Soltani, Sharif University of Technology*

This is an attempt to work with the raw bibliometric data obtained from Scopus.
For the moment, it can process Scopus data to retrieve contact information of international co-authors.

To do that, the script iterates through each paper and for each author, it will work from outside-in:

* Detect the country
	* is the author affiliated with Iran?
* Detect the institution & Department (fuzzy matching)
	* is the author affiliated with Sharif?
	* if so, is he a faculty member?
	* if so, what is (are) his/her department(s)
* Create a profile for the author and list all collaborators, number of collaborations in each year along with DOI of the papers if found.
* Is the email of the author mentioned anywhere in the database?
	* if found, this saves a lot of time!
* Export the results to a csv file

There are some comments for each function in the main script (`fuzzy_func2.py`)

# 2Do (rather long!)

1. Visualize the bigger picture: a set of functions and methods that can extract information from keywords, abstracts, citations, and grant data
2. Think about how the pieces can fit together in an orderly collection along with the script at hand.
3. Use O-O programming
4. Seriously, work on better documentation!
5. See how you can implement a more generalized solution; one that can obtain contact info for other universities
6. Change the file names to be more meaningful
