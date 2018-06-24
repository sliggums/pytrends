# pytrends

Download CSV data from Google Trends queries. Either use as executable or import at library. The master branch is implemented in python 3. For python 2, check the associated branch.

## Binary
```
./pytrends <keywords> time=<time> title=<title>
```

 * **keywords** (required): comma separated list
   - `"Google,Microsoft,Apple"`
 
 * **title** (optional): comma separated list
   - `"Interest over time,Interest by region,Related topics,Related queries"`
   - `"Interest over time"` (default)
 
 * **time** (optional): pick one of the following
   - `"all"` (default)
   - `"now+%d-H" % hours`
   - `"now+%d-d" % days`
   - `"today+%d-m" % months`
   - `"today+%d-y" % years`
   - `"[%s,%s]" % (start, end)`
     - start,end: 
       - `"[%d,%d,%d]" % (year, month, day)`
       - `"[%d,%d,%d,%d,%d,%d]" % (year, month, day, hour, minute, second)`

### Examples
```
./pytrends.py coat,jacket time="[[2017,1,1],[2018,1,1]]" title="Interest over time,Interest by region"
./pytrends.py blockchain time="today+5-y"
./pytrends.py Google,Microsoft,Apple title="Related queries"
```

## Library

```
from pytrends import pytrends
trends = pytrends()

keywords = ["coat", "jacket"]
titles = ["Interest over time","Related queries"]
time = "all"
for title in titles:
  print(trends.download_report(keywords, title, time))
```
