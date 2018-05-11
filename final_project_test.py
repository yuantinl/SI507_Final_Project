from final_project import *
import unittest

class TestYelpSearch(unittest.TestCase):

	# Dababase is correctly constructed and can satisfy necessay queries 
	def test_data_storage(self):
		DBNAME = 'yelp.db'
		try:
			conn = sqlite3.connect(DBNAME)
			cur = conn.cursor()
		except:
			print("Fail to create Database 'yelp.db'")

		# Test that these two tables have 100 records 
		yelp_data("Dallas, TX")
		cur.execute("select count(*) from Yelp")  
		self.assertEqual(list(cur)[0][0], 100)

		cur.execute("select count(*) from Cities")  
		self.assertEqual(list(cur)[0][0], 100)


	# Show that I am able to access all data sources 
	def test_data_access(self):
		# Test that I am able to scrape the 100 biggest cities' data 
		city_test = get_100_biggest_cities()[8]
		self.assertEqual(city_test.rank, "9")
		self.assertEqual(city_test.name, "Dallas, Texas")
		self.assertEqual(city_test.population, "1,257,676")
		self.assertEqual(city_test.mayor, "Mike Rawlings (D)")
		self.assertEqual(city_test.budget, "$2,800,000,000")
		self.assertEqual(city_test.elections, "No")

		#Test that I am able to get the data from Yelp Fusion 
		yelp = search_using_100_biggest_cities("Dallas, TX")
		self.assertEqual(yelp[0].restaurant, "Pecan Lodge")
		self.assertEqual(yelp[8].rating, 4.0)
		self.assertEqual(yelp[16].review, 741)
		self.assertEqual(yelp[23].city, "Dallas")
		self.assertEqual(yelp[88].state, "TX")
		self.assertEqual(yelp[43].categories, "japanese")
		self.assertEqual(yelp[2].latitude, 32.7879)
		self.assertEqual(yelp[20].longitude, -96.82703)


	#Data processing produces the results and data structures you need for presentation
	def test_data_processing(self):
	 	try: 
	 		plot_100_restaurants_maps()
	 	except:
	 		self.fail()

	 	try:
	 		plot_bar_chart_by_types()
	 	except:
	 		self.fail()

	 	try:
	 		plot_box_plot_by_types()
	 	except:
	 		self.fail()

	 	try:
	 		plot_bar_chart_top_five_restaurants()
	 	except:
	 		self.fail()


unittest.main(verbosity=2)