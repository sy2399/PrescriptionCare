/**
 *  m4876_01
 */
function drawChartUrl_m4876_01(chartDiv, chartWidth, chartHeight, chartURL, chartParam) {
	d3.json(chartURL, function(error, chartData) {
	    if (error) {
	    	console.error(error);
			return;
	    }
	    
		drawChartData_m4876_01(chartDiv, chartWidth, chartHeight, chartData);
	}); 
	//.header("Content-Type", "application/json")
	//.post(JSON.stringify(chartParam));
}

function drawChartData_m4876_01(chartDiv, chartWidth, chartHeight, chartData) {
	var days = ["일요일","월요일", "화요일", "수요일", "목요일", "금요일", "토요일"],
		daymap = {"일요일":1, "월요일":2, "화요일":3, "수요일":4, "목요일":5, "금요일":6, "토요일":7 },
		times = d3.range(24); //["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"];

	var margin = { top: 0, right: 0, bottom: 100, left: 50 },
		width = chartWidth - margin.left - margin.right,
		height = chartHeight - margin.top - margin.bottom,
		gridWidthSize = Math.floor(width / times.length),
		gridHeightSize = Math.floor(height/7),
		legendElementWidth = gridWidthSize*2;
		//buckets = 9,
		//colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
	var svg = d3.select(chartDiv).append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	var colorScale = d3.scale.linear()
						.domain([chartData.colorrange.minvalue, chartData.colorrange.color[0].maxvalue, chartData.colorrange.color[1].maxvalue])
						.range(["#" + chartData.colorrange.code, "#" + chartData.colorrange.color[0].code, "#" + chartData.colorrange.color[1].code]);


	

	var dayLabels = svg.selectAll(".dayLabel")
		.data(days)
		.enter().append("text")
			.text(function (d) { return d; })
			.attr("x", 0)
			.attr("y", function (d, i) { return i * gridHeightSize; })
			.style("text-anchor", "end")
			.style("font-size", 10)
			.style("font-family", "Verdana,sans")
			.attr("transform", "translate(-6," + gridHeightSize / 1.5 + ")");
			
	var timeLabels = svg.selectAll(".timeLabel")
		.data(times)
		.enter().append("text")
			.text(function(d) { return d; })
			.attr("x", function(d, i) { return i * gridWidthSize; })
			.attr("y", height + 20)
			.style("text-anchor", "middle")
			.style("font-size", 10)
			.style("font-family", "Verdana,sans")
			.style("font-weight", "normal")
			.style("font-style", "normal")
			.attr("transform", "translate(" + gridWidthSize / 2 + ", 0)")
			//.attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });
/*
	var colorScale = d3.scale.quantile()
		.domain([0, buckets - 1, d3.max(chartData.dataset[0].data, function (d) {
			return +d.value; 
		})])
		.range(colors);*/

	var tip = d3.tip()
				.attr("class", "d3-tip")
				.offset([-10, 0])
				.html(function(d) {
					return "<span style='color:orange'>" + numberWithCommas(d.value) + "</span>";
				})
			
	svg.call(tip);
			
	var cards = svg.append("g").attr("transform", "translate(" + gridWidthSize + ",0)").selectAll(".hour")
	.data(chartData.dataset[0].data, function(d) {
		return d.rowid + ':' + d.columnid;
	});

	cards.append("title");
	
	cards.enter().append("rect")
		.attr("x", function(d) { return (d.columnid - 1) * gridWidthSize; })
		.attr("y", function(d) { return (daymap[d.rowid] - 1) * gridHeightSize; })
		.attr("class", "hour bordered")
		.attr("width", gridWidthSize)
		.attr("height", gridHeightSize)
		.style("fill", function(d){ return colorScale(+d.value); })
		.on("mouseover", tip.show)
		.on("mouseout", tip.hide);
	
	cards.enter().append("text").style({
		"fill": "white",
		"text-anchor": "middle",
		"font-size": "8px"
			})
			.attr("x", function(d) { return (d.columnid - 1) * gridWidthSize + gridWidthSize/2; })
			.attr("y", function(d) { return (daymap[d.rowid] - 1) * gridHeightSize + gridHeightSize/2; }).text(function(d){ return d.value})
			.attr("dy", ".35em")
			.text(function(d) { return d.value; });
	
	/*    legendsvg.append("text")
	.attr("class", "legendTitle")
	.attr("x", 0)
	.attr("y", -legendHeight/4)
	.text("Number of logins");*/
	
	
	cards.transition().duration(1000).select("rect")
		.style("fill", function(d) { return colorScale(d.value); });

	//cards.select("title").text(function(d) { return d.value; });
	
	cards.exit().remove();
	
	var valueScale = d3.scale.linear()
						.domain([0, d3.max(chartData.dataset[0].data, function(d){ return +d.value; })])
						.range([0, width]);

	var numStops = 10,
		valueRange = valueScale.domain();
	
	valueRange[2] = valueRange[1] - valueRange[0];
	
	var valuePoint = [];
	for(var i = 0; i < numStops; i++)
	{
		valuePoint.push(i * valueRange[2]/(numStops - 1) + valueRange[0]);
	}
	
	svg.append("defs")
		.append("linearGradient")
		.attr("id", "legend-login")
		.attr("x1", "0%").attr("y1", "0%")
		.attr("x2", "100%").attr("y2", "0%")
		.selectAll("stop")
		.data(d3.range(numStops))
		.enter().append("stop")
		.attr("offset", function(d, i){ return valueScale( valuePoint[i])/width; })
		.attr("stop-color", function(d, i){ return colorScale(valuePoint[i]); });
		
	
	
    var topPadding = 16,
    	leftPadding = 16,
		rightPadding = 54,
    	legendWidth  = gridWidthSize * 24 - leftPadding - rightPadding,
    	legendHeight = gridHeightSize/3;
    	
    var legendsvg = svg.append("g")
    					.attr("class", "legendWrapper")
    					.attr("transform", "translate(0," + (gridHeightSize * days.length + 20) + ")");
    
    legendsvg.append("rect")
    			.attr("class", "legendRect")
    			.attr("x", 0)
    			.attr("y", legendHeight)
    			.attr("width", legendWidth)
    			.attr("height", legendHeight)
    			.style("fill", "url(#legend-login)")
    			.attr("transform", "translate(" + leftPadding + "," + topPadding + ")");
    
    
    var xScale = d3.scale.linear()
    				.range([0, legendWidth])
    				.domain([0, d3.max(chartData.dataset[0].data, function(d){ return +d.value; })]);
    
    var xAxis = d3.svg.axis()
    				.orient("bottom")
    				.tickValues([0, chartData.colorrange.color[0].maxvalue, chartData.colorrange.color[1].maxvalue])
    				//.style("font-size", 10)
    				.scale(xScale);
    				//.selectAll("text")
    				//.style("font-size", 10);
    
    //svg.selectAll("text").style("font-size", "10px");
    
    legendsvg.append("g")
    			.attr("class", "axis")
    			.attr("transform", "translate(" + leftPadding + "," + (3 * legendHeight) + ")" )
    			.call(xAxis);
    
};

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}