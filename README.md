# National Sites Information 

&nbsp;
## Data Sources

**Data Source 1**: the information regarding 100 biggest cities in the United States by popluation.
https://ballotpedia.org/Largest_cities_in_the_United_States_by_population

**Data Source 2**: YELP Fusion API. 
Instructions for getting an application id and an application key:

1. Create a yelp account, or log in to your own
2. Visit the Create New App area of the Developer's section of Yelp
3. In the create new app form, enter information about your app, then agree to Yelp API Terms of Use and Display Requirements. Then click the Submit button.
	
You will now have an application id and an application key. Put them in a secrets.py file. 

&nbsp;
## Other Information 

Plotly is a graphing service that you can work with Python. Go ahead and regsiter an account on https://plot.ly/#/. 	In this project, specific commands will open webpage with plot. 

&nbsp;
## Structure of My Code

**1. Data access**: Use get_100_biggest_cities function and class Cities to get information for cities. 
Use search function, class Yelp, and search_using_100_biggest_cities function to get information for restaurants in 	    yelp. 

**2. Data storage**: Use yelp_data function to create table Yelp and Cities. Insert data into table Yelp and Cities. 

**3. Data processing**: Four functions for data presentation: plot_100_restaurants_maps, plot_bar_chart_by_types, plot_box_plot_by_types and 	     plot_bar_chart_top_five_restaurants. 


&nbsp;
## User Guide

1. Build your own secrets.py 
2. Put "python3 nationalsties-api.py" in the command line and run it 
3. Enter "help" to see specific instructions
4. Enter a city name and a state name from the list shown in the instructions. Notice that restaurants information 	in that city on yelp will be able to be displayed later. 
5. Choose any data presentation method you want.
* Enter "plot on a map". Then it will display the ratings of 100 restaurants on a map.
* Enter "plot bar chart by types". Then it will group the restaurants by types and display top six restaurants by a bar chart.
* Enter "plot box plot by types". Then it will group the restaurants by types and display top six restaurants by a box plot.
* Enter "plot bar chart top five ". Then it will display the ratings of top five restaurants by a bar chart.

&nbsp;
## Tools and Packages used
**Stack**
* Python
* Git 

**Web API:**
* API key authorization 

**Web Scraping:**
* requests
* Beautifulsoup
* urllib2
* json 

**Data Storage**
* cache 
* sqlite3

**Interactive Data Visualization:**
* Plotly

**Unit Testing**
