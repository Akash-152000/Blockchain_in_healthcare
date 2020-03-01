$(document).ready(function() {
    $.ajax({
        type: "GET",
        url: "../data/ecg.csv",
        dataType: "text",
        success: function(data) {processData(data);}
     });
});

function processData(allText) {
    var allTextLines = allText.split(/\r\n|\n/);
    var headers = allTextLines[0].split(',');
    var lines = [];
	var labs = [];

    for (var i=1; i<allTextLines.length; i++) {
        var data = allTextLines[i].split(',');
        if (data.length == headers.length) {
            lines.push(data[0]);
			labs.push('.');
        }
    }
    // alert(lines);
	const CHART = document.getElementById("lineChart");
	let lineChart = new Chart(CHART, {
	type: 'line',
	data: {
        labels: labs,
        datasets: [{
			fill: false,
            label: 'My First dataset',
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
			borderWidth: 1,
			pointRadius: 0,
            data: lines
        }]
    },

    // Configuration options go here
    options: {
		responsive: false,
	}
});
setInterval(function(){
		lineChart.data.labels.pop();
		lineChart.data.datasets.forEach((dataset) => {
			dataset.data.shift();
		});
		lineChart.update();
		lineChart.data.labels.push('.');
		lineChart.data.datasets.forEach((dataset) => {
			dataset.data.push(290);
		});	
		lineChart.update();
	},1000);
}

