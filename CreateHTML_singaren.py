import os
import datetime

# Since datetime is a built-in module, can just use its properties to get previous day's date.
#previous_date= datetime.date(day=21, month=5, year=2015)
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

#check filepath- IMPORTANT!
filepath='html files/'

"""Creates the html template of the total usage statistics for all the institutes and the data visualisation tool."""
def createSingArenHTML(day,month,year):
	header="""<!DOCTYPE html>
	<html xmlns="http://www.w3.org/1999/xhtml">
	<html>
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
		Total Eduroam Stats
	</title>
	<script src="d3.min.js"></script>
	<script src="dimple.v2.1.3.min.js"></script>
	
	</head>
	<body>
	<h1>Total Eduroam stats for SingAren staff</h1>
	The following statistics reflect the amount of requests handled by the eduroam server for all IHLs on a hourly, daily 
	and monthly basis.<br><br>
	<b>Accepted</b>: Consists of all accepted requests to access eduroam<br>
	<b>Rejected</b>: Consists of all rejected requests to access eduroam<br><br>
	"""
	## Hourly chart ##
	hourlychart="""<div id="chart0">
	<script type="text/javascript">
		// Add an 800 x 600 pixel area for daily chart
	var hourly = dimple.newSvg("#chart0",800,600);
	d3.csv("ServerLoad"""+year+""".csv", function (data) {
	  var data_for_day= dimple.filterData(data,"Date",'"""+"".join([day,month_words,year_2numbers])+"""');
	  var myChart = new dimple.chart(hourly, data_for_day);
	  myChart.setBounds(60, 40, 600, 400);
	  var x = myChart.addTimeAxis("x", "Hour","%X","%H:%M");
	  var y = myChart.addMeasureAxis("y", "Requests");
	  y.tickFormat="6d";
	  myChart.addSeries("Category", dimple.plot.area);
	  myChart.assignColor("Rejected","rgb(224,15,41)");
	  myChart.assignColor("Accepted","rgb(132,186,92)");
	  myChart.addLegend(70, 10, 600, 400, "right");
	  myChart.draw(1000);
	  // Add a title with some d3
	hourly.append("text")
	   .attr("x", myChart._xPixels() + myChart._widthPixels() / 2)
	   .attr("y", myChart._yPixels() - 20)
	   .style("text-anchor", "middle")
	   .style("font-family", "sans-serif")
	   .style("font-weight", "bold")
	   .text("Hourly Chart for """ +" ".join([day,month,year])+""" \");
	   
	});
	</script></div>
	"""
	## Daily chart ###
	dailychart="""<div id="chart1">
	<script type="text/javascript">
		// Add an 800 x 600 pixel area for daily chart
	var day = dimple.newSvg("#chart1",800,600);
	d3.csv("ServerLoad"""+year+""".csv", function (data) {
	  data= dimple.filterData(data,"Month",'"""+str(month_words)+"""');
	  var myChart = new dimple.chart(day, data);
	  myChart.setBounds(60, 40, 600, 400);
	  var x = myChart.addTimeAxis("x", "Date","%d%b%y","%d %b");
	  //set min and max for x-axis
	  x.overrideMin = """+"d3.time.format('%Y-%m-%d').parse('"+str(first_date)+"""');
	  x.overrideMax = """+"d3.time.format('%Y-%m-%d').parse('"+str(last_date)+"""');
	  x.timePeriod= d3.time.days;
	  x.timeInterval= 7;
	  var y=myChart.addMeasureAxis("y", "Requests");
	  y.tickFormat="6d";
	  myChart.addSeries("Category", dimple.plot.area);
	  myChart.assignColor("Rejected","rgb(224,15,41)");
	  myChart.assignColor("Accepted","rgb(132,186,92)");
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
	d3.csv("ServerLoad"""+year+""".csv", function (data) {
    data= dimple.filterData(data,"Category",["Accepted","Rejected"]);
	  var myChart = new dimple.chart(month, data);
	  myChart.setBounds(60, 40, 600,400);
	  var x = myChart.addCategoryAxis("x", "Month");
	  var order=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
	  x.addOrderRule(order);
	  var y=myChart.addMeasureAxis("y", "Requests");
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
	
	return header+hourlychart+dailychart+monthlychart+"</body></html>"

with open(filepath+'total.html','w') as htmlout:
	htmlout.write(createSingArenHTML(day,month_words,year))
print("Total Eduroam stats html file written!")
