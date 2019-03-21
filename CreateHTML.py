import os
import datetime
import json

# Since datetime is a built-in module, can just use its properties to get previous day's date.
#previous_date= datetime.date(day=18, month=3, year=2019)
previous_date= datetime.date.today()- datetime.timedelta(1)
first_date= datetime.date(day=1,month=previous_date.month,year=previous_date.year)
if previous_date.month ==12:
    last_date= datetime.date(day=31,month=previous_date.month,year=previous_date.year)
else:
    last_date= datetime.date(day=1,month=previous_date.month+1,year=previous_date.year)-datetime.timedelta(1)
day= previous_date.strftime('%d')
month= previous_date.strftime('%m')
month_words= previous_date.strftime('%b')
year= previous_date.strftime('%Y')
year_2numbers= previous_date.strftime('%y')

#Check all the IHL's names and the filepath
## Load config file from ihlconfig.json which contains details of the IHLs.
config= json.load(open('ihlconfig.json'))
ihlNames=[ihl.upper() for ihl in config if ihl != 'etlr']
print(ihlNames)
filepath='html files/'

"""Creates the html template of the usage statistics for the IHL and the data visualisation tool."""
def createHTML(ihlName,day,month,year):
	header="""<!DOCTYPE html>
	<html xmlns="http://www.w3.org/1999/xhtml">
	  <head>
	<meta http-equiv="encoding" content="text/html" charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
	<style>
	body{
	  background-color: #fffff8;	  
	}
	div{
	  margin:auto;
	  width:60%;
	  padding: 10px;
	}
	</style>
	<title>
	  """+ihlName+""" Eduroam Stats
	</title>
	<script src="d3.min.js"></script>
    <script src="dimple.v2.1.3.min.js"></script>
	</head>
	<body>
	<h1>"""+ihlName+"""</h1>
	<b>Local Users</b> : """+ihlName+""" staff/students using eduroam outside of """+ihlName+""".<br>
	<b>Visitors</b>  :  Users from other IHLs and Foreign exchange users who are using eduroam in """+ihlName+""".<br>
	<b>Rejected</b> : Includes all rejected local users and visitors in """+ihlName+"""<br><br>
	The statistics here do not include local users using eduroam in their own facilities.<br><br>
	"""
	## Daily chart ###
	dailychart="""<div id="chart1">
	<script type="text/javascript">
		// Add an 800 x 600 pixel area for daily chart
	var day = dimple.newSvg("#chart1",800,600);
	d3.csv("Daily"""+month+year+""".csv", function (data) {
	  data = dimple.filterData(data, "IHL", \""""+ihlName+"""\")
	  var myChart = new dimple.chart(day, data);
	  myChart.setBounds(60, 40, 600, 400);
	  var x = myChart.addTimeAxis("x", "Date","%d%b%y","%d %b");
	  //set min and max for x-axis
	  x.overrideMin = """+"d3.time.format('%Y-%m-%d').parse('"+str(first_date)+"""');
	  x.overrideMax = """+"d3.time.format('%Y-%m-%d').parse('"+str(last_date)+"""');
	  x.timePeriod= d3.time.days;
	  x.timeInterval= 7;
	  var y =myChart.addMeasureAxis("y", "Users");
//      y.titleShape.text("Unique Users");
      y.tickFormat="6d";
	  myChart.addSeries("Category", dimple.plot.line);
	  myChart.addSeries("Category",dimple.plot.scatter);
	  myChart.assignColor("Rejected","rgb(204,37,41)");
	  myChart.assignColor("LocalUsers","rgb(132,186,92)");
	  myChart.assignColor("Visitors","rgb(218,124,48)");
	  myChart.addLegend(70, 10, 600, 400, "right");
	  myChart.draw(1000);
	  // Add a title with some d3
	day.append("text")
	   .attr("x", myChart._xPixels() + myChart._widthPixels() / 2)
	   .attr("y", myChart._yPixels() - 20)
	   .style("text-anchor", "middle")
	   .style("font-family", "sans-serif")
	   .style("font-weight", "bold")
	   .text("Daily Chart")
	   
	});
	</script></div>
	"""
	## Monthly chart ###
	monthlychart="""<div id="chart2">
	<script type="text/javascript">
	var month= dimple.newSvg("#chart2",800,600);
	d3.csv("Monthly"""+year+""".csv", function (data) {
	  data = dimple.filterData(data, "IHL", \""""+ihlName+"""\")
	  var myChart = new dimple.chart(month, data);
	  myChart.setBounds(60, 40, 600,400);
	  var x = myChart.addCategoryAxis("x", "Month");
	  var order=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
	  x.addOrderRule(order);
	  var y= myChart.addMeasureAxis("y", "UniqueUsers");
      y.tickFormat="6d";
	  var series= myChart.addSeries("Category", dimple.plot.bar);
	   // Using the afterDraw callback means this code still works with animated
	  // draws (e.g. myChart.draw(1000))
	  series.afterDraw = function (shape, data) {
		// Get the shape as a d3 selection
		var s = d3.select(shape),
		  rect = {
			x: parseFloat(s.attr("x")),
			y: parseFloat(s.attr("y")),
			width: parseFloat(s.attr("width")),
			height: parseFloat(s.attr("height"))
		  };
		// Only label bars where the text can fit
		if (rect.height >= 8) {
		  // Add a text label for the value
		  month.append("text")
			// Position in the centre of the shape (vertical position is
			// manually set due to cross-browser problems with baseline)
			.attr("x", rect.x + rect.width / 2)
			.attr("y", rect.y + rect.height / 2 + 3.5)
			// Centre align
			.style("text-anchor", "middle")
			.style("font-size", "10px")
			.style("font-family", "sans-serif")
			// Format the number: no decimal places
			.text(d3.format("1d")(data.yValue));
		}
	  };
	  myChart.assignColor("Accepted","rgb(132,186,92)");
	  myChart.assignColor("Rejected","rgb(224,15,41)");
	  myChart.addLegend(70, 10, 600,400, "right");
	  myChart.draw(1000);
	  // Add a title with some d3
	month.append("text")
	   .attr("x", myChart._xPixels() + myChart._widthPixels() / 2)
	   .attr("y", myChart._yPixels() - 20)
	   .style("text-anchor", "middle")
	   .style("font-family", "sans-serif")
	   .style("font-weight", "bold")
	   .text("Monthly Chart")
	});
	</script></div>
	"""
	## Yearly chart###
	yearlychart="""<div id="chart3">
	<script type="text/javascript">
	var year= dimple.newSvg("#chart3",800,600);
	d3.csv("Yearly.csv", function (data) {
	  data = dimple.filterData(data, "IHL", \""""+ihlName+"""\")
	  var myChart = new dimple.chart(year, data);
	  myChart.setBounds(60, 40, 600, 400);
	  var x = myChart.addCategoryAxis("x", "Year");
	  x.addOrderRule("Year");
	  var y= myChart.addMeasureAxis("y", "UniqueUsers");
      y.tickFormat="6d";
	  var series= myChart.addSeries("Category", dimple.plot.bar);
	   // Using the afterDraw callback means this code still works with animated
	  // draws (e.g. myChart.draw(1000))
	  series.afterDraw = function (shape, data) {
		// Get the shape as a d3 selection
		var s = d3.select(shape),
		  rect = {
			x: parseFloat(s.attr("x")),
			y: parseFloat(s.attr("y")),
			width: parseFloat(s.attr("width")),
			height: parseFloat(s.attr("height"))
		  };
		// Only label bars where the text can fit
		if (rect.height >= 8) {
		  // Add a text label for the value
		   year.append("text")
			// Position in the centre of the shape (vertical position is
			// manually set due to cross-browser problems with baseline)
			.attr("x", rect.x + rect.width / 2)
			.attr("y", rect.y + rect.height / 2 + 3.5)
			// Centre align
			.style("text-anchor", "middle")
			.style("font-size", "11px")
			.style("font-family", "sans-serif")
			// Format the number: no decimal places
			.text(d3.format("1d")(data.yValue));
		}
	  };
	  myChart.assignColor("Accepted","rgb(132,186,92)");
	  myChart.assignColor("Rejected","rgb(224,15,41)");
	  myChart.addLegend(70, 10, 600, 400, "right");
	  myChart.draw(1000);
	  // Add a title with some d3
	year.append("text")
	   .attr("x", myChart._xPixels() + myChart._widthPixels() / 2)
	   .attr("y", myChart._yPixels() - 20)
	   .style("text-anchor", "middle")
	   .style("font-family", "sans-serif")
	   .style("font-weight", "bold")
	   .text("Yearly Chart")
	});
	</script>
	</div>
	"""
	return header+dailychart+monthlychart+yearlychart+"</body></html>"
  
#### Writing to html files for each IHL.
for ihl in ihlNames:
	with open(filepath+ihl.lower()+'.html','w') as htmlout:
		htmlout.write(createHTML(ihl,day,month_words,year))
print("Finished writing html files for all IHLs!")
