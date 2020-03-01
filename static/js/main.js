/*
 * Parse the data and create a graph with the data.
 */
function parseData(createGraph) {
	Papa.parse("../data/ecg.csv", {
		download: true,
		complete: function(results) {
			createGraph(results.data);
		}
	});
}

function createGraph(data) {
	var years = [];
	//var silverMinted = ["Silver Minted"];

	for (var i = 1; i < data.length; i++) {
		years.push(data[i][0]);
		//silverMinted.push(data[i][2]);
	}

	console.log(years);
	//console.log(silverMinted);
	const CHART = document.getElementById("lineChart");
	console.log(CHART);
	let lineChart = new Chart(CHART, {
	type: 'line',
	data: {
 
        datasets: [{
            label: 'My First dataset',
			fill: false,
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data: years
        }]
    },
	options: {
                responsive: false
            }
});
	
}

parseData(createGraph);


