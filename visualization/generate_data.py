import csv, datetime, json, calendar

json_regions = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chattisgarh', 'NCT of Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Orissa', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']
json_cities = ['Durgapur', 'Jalpaiguri', 'Jamshedpur', 'Kolkata', 'Patna', 'Ranchi', 'Guwahati', 'Itanagar', 'Ahmedabad', 'Aurangabad', 'Bharuch', 'Jalgaon', 'Kolhapur', 'Mumbai', 'Nagpur', 'Pune', 'Rajkot', 'Solapur', 'Vadodara', 'Agra', 'Ballabhgarh', 'Bareilly', 'Barnala', 'Bhopal', 'Bilaspur', 'Chandigarh', 'Dehradun', 'Dera Bassi', 'Gorakhpur', 'Gurgaon', 'Jaipur', 'Jammu', 'Jodhpur', 'Kota', 'Kullu', 'Lalru', 'Delhi', 'Panipat', 'Rania', 'Rohtak', 'Srinagar', 'Bangalore', 'Chennai', 'Chirala', 'Coimbatore', 'Hyderabad', 'Kochi', 'Machilipatnam', 'Madurai', 'Mangalore', 'Ongole', 'Palakkad', 'Vellore', 'Vijayawada', 'Visakhapatnam', 'Cuttack', 'Padra', 'Kottayam', 'Jamtara', 'Thiruvananthapuram', 'Howrah', 'Mandi', 'Ballia', 'Bhadrawati']
cities_list = ['kochi', 'hyderabad', 'madurai', 'chandigarh', 'bhadrawati', 'dehradun', 'jamshedpur', 'ballia', 'guwahati', 'bangalore', 'agra', 'durgapur', 'mumbai', 'vadodara', 'patna', 'itanagar', 'kolkata', 'mandi', 'bhopal', 'coimbatore', 'gurgaon', 'chennai', 'rajkot', 'palakkad', 'jammu', 'howrah', 'delhi', 'thiruvananthapuram', 'vijayawada', 'aurangabad', 'jamtara', 'jodhpur', 'srinagar', 'ahmedabad', 'kottayam', 'kota', 'padra', 'pune', 'jaipur', 'nagpur', 'cuttack', 'vellore', 'jalpaiguri', 'ranchi', 'bharuch', 'jalgaon', 'kolhapur', 'solapur', 'ballabhgarh', 'bareilly', 'barnala', 'bilaspur', 'dera bassi', 'gorakhpur', 'kullu', 'lalru', 'panipat', 'rania', 'rohtak', 'chirala', 'machilipatnam', 'mangalore', 'ongole', 'visakhapatnam']

def getArrayFromCsv(csvFileName):
	content = []
	headers = None

	f = open(csvFileName, "rU")
	reader=csv.reader(f)
	for row in reader:
		if reader.line_num == 1:
			headers = row[0:]
		else:
			content.append(dict(zip(headers, row[0:])))
	f.close()
	return content

def getOriginName(lowerName):
	for region in json_regions:
		if region.lower() == lowerName:
			return region

def getCityOriginName(lowerName):
	for region in json_cities:
		if region.lower() == lowerName:
			return region

def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return datetime.datetime(year,month,day)

full_cities = getArrayFromCsv("indian-cities1.csv")

all_regions = []
pops = {}
pop_states = getArrayFromCsv('india_population.csv')
for s in pop_states:
	pops[s['Region']] = int(s['Population'])

cities = []
count = 0
hits = []

def get_data_by_good():
	rice_data = getArrayFromCsv("shark_out/shark_out_rice.csv")

	for rice in rice_data:
		rice['date_obj'] = datetime.datetime.strptime(rice['date'], '%Y-%m-%d')

	rice_data = sorted(rice_data, key=lambda x: x['date_obj'])

	vals = [[] for x in xrange(len(json_regions))]

	# For js export
	dthandler = lambda obj: (
		obj.isoformat()
		if isinstance(obj, datetime.datetime)
		or isinstance(obj, datetime.date)
		else None)

	# Daily
	results = dict(zip(json_regions, vals))
	starttime = datetime.datetime.strptime('2008-1-1', '%Y-%m-%d')
	endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
	timecount = starttime
	loopcount = 0
	ricecount = 0
	while timecount <= endtime:
		print '-----------------------'
		print timecount
		while ricecount < len(rice_data) and rice_data[ricecount]['date_obj'] <= timecount:
			rice = rice_data[ricecount]
			print '+++++++++++++++'
			print rice['date_obj']
			print rice['state']
			print getOriginName(rice['state'])
			if getOriginName(rice['state']) != None:
				results[getOriginName(rice['state'])].append(int(rice['num_tweets']))
			ricecount += 1

		for state in json_regions:
			if len(results[state]) == loopcount:
				results[state].append(0)

		timecount += datetime.timedelta(days=1)
		loopcount += 1

	# Monthly
	monthly_results = {}
	for region in json_regions:
		monthly_results[region] = {'name': 'rice', 'data': []}
	starttime = datetime.datetime.strptime('2008-6-1', '%Y-%m-%d')
	endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
	timecount = starttime
	acount = 0
	while timecount <= endtime:
		new_timecount = add_months(timecount, 1)
		days = int((new_timecount - timecount).total_seconds() / 3600 / 24)
		if acount + days > len(results[json_regions[0]]):
			days = len(results[json_regions[0]]) - acount
		print '-------days-------'
		print days
		for region in json_regions:
			monthly_results[region]['data'].append([timecount, sum(results[region][acount:acount+days])])
		timecount = new_timecount
		acount += days

	for region in json_regions:
		print region
		print monthly_results[region]['data']
	with open("twitter_rice.json", "w") as outfile:
		json.dump(results, outfile, default=dthandler)

		if row["Longitude"] and row["Latitude"]:
			cities.append({"type": "Feature", "id": row["City"],
				"geometry": { "type": "Point",
				"coordinates": [float(row["Longitude"]), float(row["Latitude"])]}
				})

def check_chingchia():
	hits = []
	count = 0
	for c in chingchia_cities:
		if c.lower() in cities_list:
			hits.append(c)
			count += 1
	print len(chingchia_cities)
	print count
	print hits
	# print [item for item in chingchia_cities if item not in hits]
	# print [item for item in json_regions if item not in hits]
	# with open("cities_temp.json", "w") as outfile:
	# 	json.dump(cities, outfile)

def get_all_twitter_city():
	tweet_data = getArrayFromCsv("tweets_cities_regions_daily.csv")

	for d in tweet_data:
		d['date_obj'] = datetime.datetime.strptime(d['date'], '%d-%m-%Y')

	tweet_data = sorted(tweet_data, key=lambda x: x['date_obj'])
	print tweet_data[0]

	vals = [[] for x in xrange(len(json_cities))]

	# Daily
	results = dict(zip(json_cities, vals))
	starttime = datetime.datetime.strptime('2007-1-1', '%Y-%m-%d')
	endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
	timecount = starttime
	loopcount = 0
	tweetcount = 0
	while timecount <= endtime:
		print '-----------------------'
		print timecount
		while tweetcount < len(tweet_data) and tweet_data[tweetcount]['date_obj'] <= timecount:
			row = tweet_data[tweetcount]
			if row['type'] == 'cities':
				print '+++++++++++++++'
				print row['date_obj']
				print row['location_name']
				print getCityOriginName(row['location_name'])
				if getCityOriginName(row['location_name']) != None:
					if len(results[getCityOriginName(row['location_name'])]) <= loopcount:
						results[getCityOriginName(row['location_name'])].append(int(row['num_tweets']))
					else:
						results[getCityOriginName(row['location_name'])][-1] += int(row['num_tweets'])
			tweetcount += 1

		for state in json_cities:
			if len(results[state]) == loopcount:
				results[state].append(0)

		timecount += datetime.timedelta(days=1)
		loopcount += 1

	# Monthly
	monthly_results = []
	starttime = datetime.datetime.strptime('2007-1-1', '%Y-%m-%d')
	endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
	timecount = starttime
	acount = 0
	while timecount <= endtime:
		monthly_results.append({'year': timecount.year, 'month': timecount.month, 'values': []})

		new_timecount = add_months(timecount, 1)
		days = int((new_timecount - timecount).total_seconds() / 3600 / 24)
		if acount + days > len(results[json_cities[0]]):
			days = len(results[json_cities[0]]) - acount
		print '-------days-------'
		print days
		for region in json_cities:
			monthly_results[-1]['values'].append({'id': region, 'num_tweets': sum(results[region][acount:acount+days])})
		timecount = new_timecount
		acount += days

	print monthly_results[0]
	print monthly_results[-1]

	with open("twitter_data_cities.json", "w") as outfile:
		json.dump(monthly_results, outfile)
	with open("twitter_data_by_city.json", "w") as outfile:
		json.dump(results, outfile)


def get_all_twitter_region():
	tweet_data = getArrayFromCsv("tweets_cities_regions_daily.csv")

	for d in tweet_data:
		d['date_obj'] = datetime.datetime.strptime(d['date'], '%d-%m-%Y')

	tweet_data = sorted(tweet_data, key=lambda x: x['date_obj'])
	print tweet_data[0]

	vals = [[] for x in xrange(len(json_regions))]

	# Daily
	results = dict(zip(json_regions, vals))
	starttime = datetime.datetime.strptime('2007-1-1', '%Y-%m-%d')
	endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
	timecount = starttime
	loopcount = 0
	tweetcount = 0
	while timecount <= endtime:
		print '-----------------------'
		while tweetcount < len(tweet_data) and tweet_data[tweetcount]['date_obj'] <= timecount:
			row = tweet_data[tweetcount]
			if row['type'] == 'regions':
				print '+++++++++++++++'
				# print row['date_obj']
				# print row['location_name']
				# print getOriginName(row['location_name'])
				if getOriginName(row['location_name']) != None:
					if len(results[getOriginName(row['location_name'])]) <= loopcount:
						results[getOriginName(row['location_name'])].append(int(row['num_tweets']) * 100000.0 / pops[getOriginName(row['location_name'])])
					else:
						results[getOriginName(row['location_name'])][-1] += int(row['num_tweets']) * 100000.0 / pops[getOriginName(row['location_name'])]
			tweetcount += 1

		for state in json_regions:
			if len(results[state]) == loopcount:
				results[state].append(0)

		timecount += datetime.timedelta(days=1)
		loopcount += 1

	# Monthly
	monthly_results = []
	starttime = datetime.datetime.strptime('2007-1-1', '%Y-%m-%d')
	endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
	timecount = starttime
	acount = 0
	while timecount <= endtime:
		monthly_results.append({'year': timecount.year, 'month': timecount.month, 'values': []})

		new_timecount = add_months(timecount, 1)
		days = int((new_timecount - timecount).total_seconds() / 3600 / 24)
		if acount + days > len(results[json_regions[0]]):
			days = len(results[json_regions[0]]) - acount
		print '-------days-------'
		print days
		for region in json_regions:
			monthly_results[-1]['values'].append({'id': region, 'num_tweets': sum(results[region][acount:acount+days])})
		timecount = new_timecount
		acount += days

	print monthly_results[0]
	print monthly_results[-1]

	with open("twitter_data_regions.json", "w") as outfile:
		json.dump(monthly_results, outfile)
	with open("twitter_data_by_region.json", "w") as outfile:
		json.dump(results, outfile)


get_all_twitter_region()
