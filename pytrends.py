#!/usr/bin/python

import http.client as httplib
import urllib
import requests
import json
import sys
import ast

class pytrends:
	def __init__(self):
		self.cj = requests.get("https://trends.google.com/").cookies
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [
			("Referrer", "https://trends.google.com/trends/explore"),
			('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21'),
			("Accept", "text/plain")
		]
		self.api = {
			"Interest over time": 'https://trends.google.com/trends/api/widgetdata/multiline/csv?',
			"Interest by region": 'https://trends.google.com/trends/api/widgetdata/comparedgeo/csv?',
			"Related topics" : 'https://trends.google.com/trends/api/widgetdata/relatedsearches/csv?',
			"Related queries": 'https://trends.google.com/trends/api/widgetdata/relatedsearches/csv?'
		}
		self.widgets = None
		self.widget_params = []

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

	def get_widgets(self, keywords, time="all"):
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
		self.widgets = data["widgets"]
		self.widget_params = [keywords, time]

	def get_params(self, keywords, title="Interest over time", time="all"):
		if not self.widget_params or self.widget_params != [keywords, time]:
			self.get_widgets(keywords, time)

		for widget in self.widgets:
			if widget["title"] == title:
				#if title in ["Related queries"]:
				#	widget["request"]["restriction"]["geo"]["country"] = "US"
				return {
					"req":widget["request"],
					"token":widget["token"],
					"tz":240
				}

		return dict()

	def download_report(self, keywords, title="Interest over time", time="all"):
		params = self.get_params(keywords, title, time)
		
		url = self.api[title] + self.encode_params(params, "csv")
		return self.opener.open(url).read().decode('utf8')
		

if __name__ == "__main__":
	"""
	Examples:
	./pytrends.py coat,jacket time="[[2017,1,1],[2018,1,1]]" title="Interest over time,Interest by region"
	./pytrends.py blockchain time="today+5-y"
	./pytrends.py Google,Microsoft,Apple title="Related queries"

	keywords: comma separated list
		word,word,word

	title: comma separated list
	"Interest over time,Interest by region,Related topics,Related queries"

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
	titles=["Interest over time"]
	time="all"
	for i in range(2, len(sys.argv)):
		arg = sys.argv[i].split('=')
		if arg[0] == "title":
			titles = arg[1].split(",")
		elif arg[0] == "time":
			time = arg[1]
			if time[0] == '[':
				time = ast.literal_eval(time)
	
	trends = pytrends()
	for title in titles:
		print(trends.download_report(keywords, title, time))

