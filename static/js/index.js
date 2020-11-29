document.body.style.position = 'relative';

var container = document.getElementById('tvchart');
document.body.appendChild(container);

var width = 1000;
var height = 500;

var chart = LightweightCharts.createChart(container, {
	width: width,
	height: height,
	rightPriceScale: {
		scaleMargins: {
			top: 0.2,
			bottom: 0.2,
		},
		borderVisible: false,
	},

    timeScale:{
      timeVisible:true,
      secondsVisible:false,
      borderVisible:false
    },

	layout: {
		backgroundColor: '#ffffff',
		textColor: '#333',
	},
	grid: {
		horzLines: {
			color: '#eee',
		},
		vertLines: {
			color: '#ffffff',
		},
	},
});

var areaSeries = chart.addAreaSeries({
  topColor: 'rgba(255, 82, 82, 0.56)',
  bottomColor: 'rgba(255, 82, 82, 0.04)',
  lineColor: 'rgba(255, 82, 82, 1)',
  lineWidth: 2,
	symbol: 'AAPL',
});


function businessDayToString(businessDay) {
	return businessDay.year + '-' + businessDay.month + '-' + businessDay.day;
}

var toolTipWidth = 100;
var toolTipHeight = 80;
var toolTipMargin = 15;

var toolTip = document.createElement('div');
toolTip.className = 'floating-tooltip-2';
container.appendChild(toolTip);

// update tooltip
chart.subscribeCrosshairMove(function(param) {
	if (!param.time || param.point.x < 0 || param.point.x > width || param.point.y < 0 || param.point.y > height) {
		toolTip.style.display = 'none';
		return;
	}

	var dateStr = LightweightCharts.isBusinessDay(param.time)
		? businessDayToString(param.time)
		: new Date(param.time * 1000).toLocaleDateString();

	toolTip.style.display = 'block';
	var price = param.seriesPrices.get(areaSeries);
	toolTip.innerHTML = '<div style="color: rgba(255, 70, 70, 1)">INFY</div>' +
		'<div style="font-size: 24px; margin: 4px 0px">' + Math.round(price * 100) / 100 + '</div>' +
		'<div>' + param.time + '</div>';

	var y = param.point.y;

	var left = param.point.x + toolTipMargin;
	if (left > width - toolTipWidth) {
		left = param.point.x - toolTipMargin - toolTipWidth;
	}

	var top = y + toolTipMargin;
	if (top > height - toolTipHeight) {
		top = y - toolTipHeight - toolTipMargin;
	}

	toolTip.style.left = left + 'px';
	toolTip.style.top = top + 'px';
});
  
fetch(`http://127.0.0.1:5000/api/GetDataForChart?name=INFY`)
  .then(res => res.json())
  .then(data => {
    console.log(data)
    const cdata = data
	areaSeries.setData(cdata);
	a=1606491223

  })
  .catch(err => console.log(err))
a=1606491223
//series.setData(data);
function yourFunction(){
	// do whatever you like here
	b=Math.floor((Math.random() * 100) + 1000);
	data={'time':a,'value':b}
	console.log(data)
	areaSeries.update(data);
	a=a+60
    setTimeout(yourFunction, 3000);
}
yourFunction();


