from secrets import *
import secrets
import requests
import argparse
import json
import pprint
import requests
import sys
import urllib
from bs4 import BeautifulSoup
import sqlite3
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go

# Reference: https://github.com/Yelp/yelp-fusion/blob/master/fusion/python/sample.py
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

app_id = secrets.APP_ID 
app_key = secrets.APP_KEY 

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
SEARCH_LIMIT = 50

DBNAME = 'yelp.db'

CACHE_FNAME = 'yelp.json'


def get_unique_key(url):
	return url 

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() 
        return CACHE_DICTION[unique_ident]

class Cities():
    def __init__(self, rank, name, population, mayor, budget, elections):
        self.rank = rank
        self.name = name
        self.population = population
        self.mayor = mayor
        self.budget = budget
        self.elections = elections

# Get the name of 100 largest cities by population. The city names will be used as a search term for yelp.
# Scrape the information for table Cities. In addition to city names, other columns include: rank, population(2013), mayor, budget, elections in 2018
def get_100_biggest_cities():
    base_url = "https://ballotpedia.org/Largest_cities_in_the_United_States_by_population"
    resp = make_request_using_cache(base_url)
    soup = BeautifulSoup(resp, 'html.parser')

    all_info = soup.find_all('td')[7:607]
    
    cities_lst = []
    rank_lst = []
    name_lst = []
    population_lst = []
    mayor_lst = []
    budget_lst = []
    elections_lst = []
    num = 0
    for item in all_info:
        if num%6 == 0:
            rank_lst.append(item.text.strip())
        elif num%6 == 1:
            name_lst.append(item.text.strip())
        elif num%6 == 2:
            population_lst.append(item.text.strip())
        elif num%6 == 3:
            mayor_lst.append(item.text.strip())
        elif num%6 == 4:
            budget_lst.append(item.text.strip())
        elif num%6 == 5:
            elections_lst.append(item.text.strip())
        num += 1

    count = 0 
    while count < len(rank_lst):
        cities = Cities(rank_lst[count], name_lst[count], population_lst[count], mayor_lst[count], budget_lst[count], elections_lst[count])
        count += 1
        cities_lst.append(cities)
    return cities_lst 

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def get_from_yelp_using_cache(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    unique_ident = params_unique_combination(url, url_params)
    #print(unique_ident)

    try:
       cache_file = open(CACHE_FNAME, 'r')
       cache_contents = cache_file.read()
       CACHE_DICTION = json.loads(cache_contents)
       cache_file.close()
    except:
       CACHE_DICTION= {}

    ## first, look in the cache to see if we already have this data 
    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    else:
        #print("Making a request for new data...")
        response = requests.request('GET', url, headers=headers, params=url_params)
        CACHE_DICTION[unique_ident] = json.loads(response.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME, "w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

def search(api_key, location, SEARCH_LIMIT, offset):
    url_params = {
        #'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset': offset
    }
    return get_from_yelp_using_cache(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

class Yelp():
    def __init__(self, restaurant, rating, review, city, state, categories, latitude, longitude):
        self.restaurant = restaurant 
        self.rating = rating
        self.review = review 
        self.city = city
        self.state = state 
        self.categories = categories
        self.latitude = latitude
        self.longitude = longitude

def search_using_100_biggest_cities(city_state):
    offset1 = 0
    offset2 = 51
    search(app_key, city_state, SEARCH_LIMIT, offset1)
    #print("1")
    search(app_key, city_state, SEARCH_LIMIT, offset2)
    #print("1")
    with open('yelp.json') as json_data:
        yelp_data = json.load(json_data)

    restaurant_lst = []
    rating_lst = []
    review_lst = []
    city_lst = []
    state_lst = []
    categories_lst = []
    latitude_lst = []
    longitude_lst = []
    city_state = city_state.replace(" ", "+")
    search_url1 = 'https://api.yelp.com/v3/businesses/searchlimit-50_location-' + city_state + '_offset-0'
  
    for i in yelp_data[search_url1]['businesses']:
        restaurant_lst.append(i['name'])
        rating_lst.append(i['rating'])
        review_lst.append(i['review_count'])
        city_lst.append(i['location']['city'])
        state_lst.append(i['location']['state'])
        categories_lst.append(i['categories'][0]['alias'])
        latitude_lst.append(i['coordinates']['latitude'])
        longitude_lst.append(i['coordinates']['longitude'])

    search_url2 = 'https://api.yelp.com/v3/businesses/searchlimit-50_location-' + city_state + '_offset-51'
    for i in yelp_data[search_url2]['businesses']:
        restaurant_lst.append(i['name'])
        rating_lst.append(i['rating'])
        review_lst.append(i['review_count'])
        city_lst.append(i['location']['city'])
        state_lst.append(i['location']['state'])
        categories_lst.append(i['categories'][0]['alias'])
        latitude_lst.append(i['coordinates']['latitude'])
        longitude_lst.append(i['coordinates']['longitude'])

    yelp_lst = []
    count = 0 
    while count < len(restaurant_lst):
        yelp = Yelp(restaurant_lst[count], rating_lst[count], review_lst[count], city_lst[count], state_lst[count], categories_lst[count], latitude_lst[count], longitude_lst[count])
        count += 1
        yelp_lst.append(yelp)

    return yelp_lst

#search_using_100_biggest_cities("New York, New York")
#print(search_using_100_biggest_cities("Chicago, Illinois"))
#print(search_using_100_biggest_cities("Los Angeles, California"))

try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
except:
        print("Fail to create Database 'yelp.db'")

def yelp_data(city_state):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to create Database 'yelp.db'")

    statement = '''
        DROP TABLE IF EXISTS 'Yelp';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Cities';
    '''
    cur.execute(statement)

    # Create Yelp table 
    statement = '''
    CREATE TABLE 'Yelp' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT, 
        'Rating' REAL,
        'ReviewCount' INTEGER,
        'City' TEXT,  
        'State' TEXT, 
        'Alias' TEXT,
        'Latitude' REAL,
        'Longitutde' REAL
        );
    '''
    cur.execute(statement)
    conn.commit()

    yelp = search_using_100_biggest_cities(city_state)

    for yelp_object in yelp:
        insertion = (None, yelp_object.restaurant, yelp_object.rating, yelp_object.review, yelp_object.city, yelp_object.state, yelp_object.categories, yelp_object.latitude, yelp_object.longitude)
        insert = '''
            INSERT INTO Yelp
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(insert, insertion)
        conn.commit()

    #create Cities table 
    statement = '''
    CREATE TABLE 'Cities' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT, 
        'Rank' INTEGER,
        'Name' TEXT,
        'Population' INTEGER,
        'Mayor' TEXT,
        'BUDGET' TEXT,
        'ELECTIONS' TEXT, 
        FOREIGN KEY(Name) REFERENCES Yelp(City)
    )
    '''
    cur.execute(statement)
    conn.commit()

    # add data to the Cities table 
    cities = get_100_biggest_cities()
    for city_object in cities:
        insertion = (None, city_object.rank, city_object.name, city_object.population, city_object.mayor, city_object.budget, city_object.elections)
        insert = '''
            INSERT INTO Cities
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(insert, insertion)
        conn.commit()

# Display ratings for different restaurants in a city using scatter plots on  maps
def plot_100_restaurants_maps():
    statement = '''
        SELECT Latitude FROM Yelp 
    '''
    cur.execute(statement)
    conn.commit()

    lat_vals = []
    for i in cur:
        lat_vals.append(i[0])

    statement = '''
        SELECT Longitutde FROM Yelp
    '''
    cur.execute(statement)
    conn.commit()

    lon_vals = []
    for i in cur:
        lon_vals.append(i[0])
    #print(lon_vals)

    statement = '''
        SELECT Rating FROM Yelp
    '''
    cur.execute(statement)
    conn.commit()

    text_vals = []
    for i in cur:
        text_vals.append(i[0])

    statement = '''
        SELECT City FROM Yelp
    '''
    cur.execute(statement)
    conn.commit()
    for i in cur:
        city_name = i[0]

    data = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lon_vals,
        lat = lat_vals,
        text = text_vals,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'star',
            )
        )
    ]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v 
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat)/2
    center_lon = (max_lon+min_lon)/2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
        title = '100 Restaurants in ' + city_name,
        geo = dict(
            scope = 'usa',
            projection = dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center = {'lat': center_lat, 'lon': center_lon},
            countrywidth = 3,
            subunitwidth = 3
            ),
        )

    fig = dict(data=data, layout=layout )
    py.plot( fig, validate=False, filename='plot_100_restaurants')

#plot_100_restaurants_maps()
def plot_bar_chart_by_types():
    statement = '''
        SELECT AVG(Rating), Alias
        FROM Yelp
        GROUP BY Alias
        ORDER BY AVG(Rating) DESC
        LIMIT 6
    '''
    cur.execute(statement)
    conn.commit()

    x_vals = []
    y_vals = []
    for i in cur:
        y_vals.append(round(i[0], 2))
        x_vals.append(i[1])
    
    data = [go.Bar(
                x=x_vals,
                y=y_vals,
                text=x_vals,
                textposition = 'auto',
                marker=dict(
                    color='rgb(158, 202, 225)',
                    line=dict(
                        color='rgb(8, 48, 107)',
                        width=1.5),
                ),
                opacity=0.6
    )]

    py.plot(data, filename='plot_bar_chart_by_types')

def plot_box_plot_by_types():
    statement = '''
        SELECT AVG(Rating), Alias
        FROM Yelp
        GROUP BY Alias
        ORDER BY AVG(Rating) DESC
        LIMIT 6
    '''
    cur.execute(statement)
    conn.commit()

    x_vals = []
    y_vals = []
    for i in cur:
        y_vals.append(round(i[0], 2))
        x_vals.append(i[1])  

    colors = ['rgba(93, 164, 214, 0.5)', 'rgba(255, 144, 14, 0.5)', 'rgba(44, 160, 101, 0.5)', 'rgba(255, 65, 54, 0.5)', 'rgba(207, 114, 255, 0.5)', 'rgba(127, 96, 0, 0.5)'] 

    traces = []

    for xd, yd, cls in zip(x_vals, y_vals, colors):
        traces.append(go.Box(
            y=yd,
            name=xd,
            boxpoints='all',
            jitter=0.5,
            whiskerwidth=0.2,
            fillcolor=cls,
            marker=dict(
                size=2,
            ),
            line=dict(width=1),
        ))

    layout = go.Layout(
        title='Six Types of Restaurants with Highest Average Ratings',
        yaxis=dict(
            autorange=True,
            showgrid=True,
            zeroline=True,
            dtick=5,
            gridcolor='rgb(255, 255, 255)',
            gridwidth=1,
            zerolinecolor='rgb(255, 255, 255)',
            zerolinewidth=2,
        ),
        margin=dict(
            l=40,
            r=30,
            b=80,
            t=100,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
        showlegend=False
    )

    fig = go.Figure(data=traces, layout=layout)
    py.plot(fig)

def plot_bar_chart_top_five_restaurants():
    statement = '''
        SELECT Name, Rating 
        FROM Yelp
        Order By Rating Desc
        Limit 5 
    '''
    cur.execute(statement)
    conn.commit()

    name_lst = []
    rating_lst = []
    for i in cur:
        name_lst.append(i[0])
        rating_lst.append(i[1])

    data = [go.Bar(
            x=name_lst,
            y=rating_lst,
            text=name_lst,
            textposition = 'auto',
            marker=dict(
                color='rgb(158, 202, 225)',
                line=dict(
                    color='rgb(8, 48, 107)',
                    width=1.5),
                ),
            opacity=0.6
    )]
    py.plot(data, filename='plot_bar_chart_by_top_five_restaurants')

city_name_lst = ['New York, New York', 'Los Angeles, California', 'Chicago, Illinois', 'Houston, Texas', 'Philadelphia, Pennsylvania', 'Phoenix, Arizona', 'San Antonio, Texas', 'San Diego, California', 'Dallas, Texas', 'San Jose, California', 'Austin, Texas', 'Indianapolis, Indiana', 'Jacksonville, Florida', 'San Francisco, California', 'Columbus, Ohio', 'Charlotte, North Carolina', 'Fort Worth, Texas', 'Detroit, Michigan', 'El Paso, Texas', 'Memphis, Tennessee', 'Seattle, Washington', 'Denver, Colorado', 'Washington, D.C.', 'Boston, Massachusetts', 'Nashville, Tennessee', 'Baltimore, Maryland', 'Oklahoma City, Oklahoma', 'Louisville, Kentucky', 'Portland, Oregon', 'Las Vegas, Nevada', 'Milwaukee, Wisconsin', 'Albuquerque, New Mexico', 'Tucson, Arizona', 'Fresno, California', 'Sacramento, California', 'Long Beach, California', 'Kansas City, Missouri', 'Mesa, Arizona', 'Virginia Beach, Virginia', 'Atlanta, Georgia', 'Colorado Springs, Colorado', 'Omaha, Nebraska', 'Raleigh, North Carolina', 'Miami, Florida', 'Oakland, California', 'Minneapolis, Minnesota', 'Tulsa, Oklahoma', 'Cleveland, Ohio', 'Wichita, Kansas', 'Arlington, Texas', 'New Orleans, Louisiana', 'Bakersfield, California', 'Tampa, Florida', 'Honolulu, Hawaii', 'Aurora, Colorado', 'Anaheim, California', 'Santa Ana, California', 'St. Louis, Missouri', 'Riverside, California', 'Corpus Christi, Texas', 'Lexington, Kentucky', 'Pittsburgh, Pennsylvania', 'Anchorage, Alaska', 'Stockton, California', 'Cincinnati, Ohio', 'St. Paul, Minnesota', 'Toledo, Ohio', 'Greensboro, North Carolina', 'Newark, New Jersey', 'Plano, Texas', 'Henderson, Nevada', 'Lincoln, Nebraska', 'Buffalo, New York', 'Jersey City, New Jersey', 'Chula Vista, California', 'Fort Wayne, Indiana', 'Orlando, Florida', 'St. Petersburg, Florida', 'Chandler, Arizona', 'Laredo, Texas', 'Norfolk, Virginia', 'Durham, North Carolina', 'Madison, Wisconsin', 'Lubbock, Texas', 'Irvine, California', 'Winston-Salem, North Carolina', 'Glendale, Arizona', 'Garland, Texas', 'Hialeah, Florida', 'Reno, Nevada', 'Chesapeake, Virginia', 'Gilbert, Arizona', 'Baton Rouge, Louisiana', 'Irving, Texas', 'Scottsdale, Arizona', 'North Las Vegas, Nevada', 'Fremont, California', 'Boise, Idaho', 'San Bernardino, California', 'Birmingham, Alabama']

while True:
    user_input = str(input('Enter command (or "help" for options): '))
    if user_input == 'exit':
        print("Bye!")
        break
    elif (user_input == 'help'):
        print('''
            <city Name, state name>
                Choose one city name from the lists below and input it exactlly as it is shown below 
                ['New York, New York', 'Los Angeles, California', 'Chicago, Illinois', 'Houston, Texas', 'Philadelphia, Pennsylvania', 'Phoenix, Arizona', 'San Antonio, Texas', 'San Diego, California', 'Dallas, Texas', 'San Jose, California', 'Austin, Texas', 'Indianapolis, Indiana', 'Jacksonville, Florida', 'San Francisco, California', 'Columbus, Ohio', 'Charlotte, North Carolina', 'Fort Worth, Texas', 'Detroit, Michigan', 'El Paso, Texas', 'Memphis, Tennessee', 'Seattle, Washington', 'Denver, Colorado', 'Washington, D.C.', 'Boston, Massachusetts', 'Nashville, Tennessee', 'Baltimore, Maryland', 'Oklahoma City, Oklahoma', 'Louisville, Kentucky', 'Portland, Oregon', 'Las Vegas, Nevada', 'Milwaukee, Wisconsin', 'Albuquerque, New Mexico', 'Tucson, Arizona', 'Fresno, California', 'Sacramento, California', 'Long Beach, California', 'Kansas City, Missouri', 'Mesa, Arizona', 'Virginia Beach, Virginia', 'Atlanta, Georgia', 'Colorado Springs, Colorado', 'Omaha, Nebraska', 'Raleigh, North Carolina', 'Miami, Florida', 'Oakland, California', 'Minneapolis, Minnesota', 'Tulsa, Oklahoma', 'Cleveland, Ohio', 'Wichita, Kansas', 'Arlington, Texas', 'New Orleans, Louisiana', 'Bakersfield, California', 'Tampa, Florida', 'Honolulu, Hawaii', 'Aurora, Colorado', 'Anaheim, California', 'Santa Ana, California', 'St. Louis, Missouri', 'Riverside, California', 'Corpus Christi, Texas', 'Lexington, Kentucky', 'Pittsburgh, Pennsylvania', 'Anchorage, Alaska', 'Stockton, California', 'Cincinnati, Ohio', 'St. Paul, Minnesota', 'Toledo, Ohio', 'Greensboro, North Carolina', 'Newark, New Jersey', 'Plano, Texas', 'Henderson, Nevada', 'Lincoln, Nebraska', 'Buffalo, New York', 'Jersey City, New Jersey', 'Chula Vista, California', 'Fort Wayne, Indiana', 'Orlando, Florida', 'St. Petersburg, Florida', 'Chandler, Arizona', 'Laredo, Texas', 'Norfolk, Virginia', 'Durham, North Carolina', 'Madison, Wisconsin', 'Lubbock, Texas', 'Irvine, California', 'Winston-Salem, North Carolina', 'Glendale, Arizona', 'Garland, Texas', 'Hialeah, Florida', 'Reno, Nevada', 'Chesapeake, Virginia', 'Gilbert, Arizona', 'Baton Rouge, Louisiana', 'Irving, Texas', 'Scottsdale, Arizona', 'North Las Vegas, Nevada', 'Fremont, California', 'Boise, Idaho', 'San Bernardino, California', 'Birmingham, Alabama']
            plot on a map
                displays the ratings of 100 restaurants on a map
            plot bar chart by types 
                groups the restaurants by types and displays top six restaurants by a bar chart 
            plot box plot by types 
                groups the restaurants by types and displays top six restaurants by a box plot 
            plot bar chart top five 
                displays the ratings of top five restaurants by a bar chart 
            ''')
    elif (user_input in city_name_lst): 
        yelp_data(user_input)
    elif (user_input == "plot on a map"):
        plot_100_restaurants_maps()
    elif (user_input == "plot bar chart by types"):
        plot_bar_chart_by_types()
    elif (user_input == "plot box plot by types"):
        plot_box_plot_by_types()
    elif (user_input == "plot bar chart top five"):
        plot_bar_chart_top_five_restaurants()
    else:
        print('''
            Input error. Please enter command following the instructions below.
            <city Name, state name>
                choose one city name from the lists below and input it exactlly as it is shown below 
                ['New York, New York', 'Los Angeles, California', 'Chicago, Illinois', 'Houston, Texas', 'Philadeßlphia, Pennsylvania', 'Phoenix, Arizona', 'San Antonio, Texas', 'San Diego, California', 'Dallas, Texas', 'San Jose, California', 'Austin, Texas', 'Indianapolis, Indiana', 'Jacksonville, Florida', 'San Francisco, California', 'Columbus, Ohio', 'Charlotte, North Carolina', 'Fort Worth, Texas', 'Detroit, Michigan', 'El Paso, Texas', 'Memphis, Tennessee', 'Seattle, Washington', 'Denver, Colorado', 'Washington, D.C.', 'Boston, Massachusetts', 'Nashville, Tennessee', 'Baltimore, Maryland', 'Oklahoma City, Oklahoma', 'Louisville, Kentucky', 'Portland, Oregon', 'Las Vegas, Nevada', 'Milwaukee, Wisconsin', 'Albuquerque, New Mexico', 'Tucson, Arizona', 'Fresno, California', 'Sacramento, California', 'Long Beach, California', 'Kansas City, Missouri', 'Mesa, Arizona', 'Virginia Beach, Virginia', 'Atlanta, Georgia', 'Colorado Springs, Colorado', 'Omaha, Nebraska', 'Raleigh, North Carolina', 'Miami, Florida', 'Oakland, California', 'Minneapolis, Minnesota', 'Tulsa, Oklahoma', 'Cleveland, Ohio', 'Wichita, Kansas', 'Arlington, Texas', 'New Orleans, Louisiana', 'Bakersfield, California', 'Tampa, Florida', 'Honolulu, Hawaii', 'Aurora, Colorado', 'Anaheim, California', 'Santa Ana, California', 'St. Louis, Missouri', 'Riverside, California', 'Corpus Christi, Texas', 'Lexington, Kentucky', 'Pittsburgh, Pennsylvania', 'Anchorage, Alaska', 'Stockton, California', 'Cincinnati, Ohio', 'St. Paul, Minnesota', 'Toledo, Ohio', 'Greensboro, North Carolina', 'Newark, New Jersey', 'Plano, Texas', 'Henderson, Nevada', 'Lincoln, Nebraska', 'Buffalo, New York', 'Jersey City, New Jersey', 'Chula Vista, California', 'Fort Wayne, Indiana', 'Orlando, Florida', 'St. Petersburg, Florida', 'Chandler, Arizona', 'Laredo, Texas', 'Norfolk, Virginia', 'Durham, North Carolina', 'Madison, Wisconsin', 'Lubbock, Texas', 'Irvine, California', 'Winston-Salem, North Carolina', 'Glendale, Arizona', 'Garland, Texas', 'Hialeah, Florida', 'Reno, Nevada', 'Chesapeake, Virginia', 'Gilbert, Arizona', 'Baton Rouge, Louisiana', 'Irving, Texas', 'Scottsdale, Arizona', 'North Las Vegas, Nevada', 'Fremont, California', 'Boise, Idaho', 'San Bernardino, California', 'Birmingham, Alabama']
            plot on a map
                displays the ratings of 100 restaurants on a map
            plot bar chart by types 
                groups the restaurants by types and displays top six restaurants by a bar chart 
            plot box plot by types 
                groups the restaurants by types and displays top six restaurants by a box plot 
            plot bar chart top five 
                displays the ratings of top five restaurants by a bar chart 
            ''')
