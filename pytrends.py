#!/usr/bin/python

import http.client as httplib
import urllib
import requests
import simplejson as json
import sys
import ast

class pytrends:
	def __init__(self):
		self.cj = requests.get("https://trends.google.com/").cookies
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [("Referrer", "https://trends.google.com/trends/explore"),
							('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21'),
							("Accept", "text/plain")]

	def encode_time(self, *args):
		if len(args) == 3:
			return "%04d-%02d-%02d" % args
		elif len(args) == 6:
			return "%04d-%02d-%02dT%02d\\:%02d\\:%02d" % args
		else:
			return "all"

	def encode_params(self, params, page):
		params["req"] = json.dumps(params["req"],separators=(',', ':'))
		params = urllib.parse.urlencode(params)
		if page=="explore":
			params = params.replace('%3A', ':').replace('%2C', ',')
		elif page=="csv":
			params = params.replace("+", "%20")
		return params

	def get_params(self, keywords, title="Interest over time", time="all"):
		params = {
			"hl": "en-US",
			"tz": 240,
			"req": {
			"comparisonItem": [
				{
					"keyword": keyword,
					"geo":"",
					"time": self.encode_time(*(time[0])) + " " + self.encode_time(*(time[1])) if isinstance(time, (list, tuple)) else "all"
				}
				for keyword in keywords ],
				"category": 0,
				"property": ""
			}
		}

		#print "https://trends.google.com/trends/api/explore?" + params

		data = self.opener.open("https://trends.google.com/trends/api/explore?" + self.encode_params(params, "explore")).read().decode('utf8')
		data = data[data.find("{"):]
		data = json.loads(data)

		for widget in data["widgets"]:
			if widget["title"] == title:
				return {"token":widget["token"], "req":widget["request"], "tz":240}

		return dict()

	def download_report(self, keywords, title="Interest over time", time="all"):
		params = self.get_params(keywords, title, time)

		#print 'https://trends.google.com/trends/api/widgetdata/multiline/csv?' + params
		return self.opener.open('https://trends.google.com/trends/api/widgetdata/multiline/csv?' + self.encode_params(params, "csv")).read()
		

if __name__ == "__main__":
	"""
	keywords: word,word,word
	title: pick one of [
		"Interest over time",
		"Interest by region",
		"Related topics",
		"Related queries"
	]

	time: pick one of [
		"all",
		"now+%d-H" % hours,
		"now+%d-d" % days,
		"today+%d-m" % months,
		"today+%d-y" % years,
		[
			[year, month, day] # start time
			[year, month, day] # end time
		],
		[
			[year, month, day, hour, minute, second] # start time
			[year, month, day, hour, minute, second] # end time
		]
	]
	"""

	keywords=sys.argv[1].split(",")
	title="Interest over time"
	time="all"
	for i in range(2, len(sys.argv)):
		arg = sys.argv[i].split('=')
		if arg[0] == "title":
			title = arg[1]
		elif arg[0] == "time":
			time = arg[1]
			if time[0] == '[':
				time = ast.literal_eval(time)
	
	trends = pytrends()
	print(trends.download_report(keywords, title, time).decode('utf8'))

