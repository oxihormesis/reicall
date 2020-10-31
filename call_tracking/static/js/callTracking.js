// Renders the charts on the home page using Chart.js

// Make all charts responsive
Chart.defaults.global.responsive = true;

// Configure the leadsBySource bar chart
$.get("/leads-by-source", function(data) {
  var chartData = [];
  for (var i = 0; i < data.length; i++) {
    chartData.push({
      value: data[i]["lead__count"],
      label: data[i]["name"]
    });
  }

  var ctx = document.getElementById("leadsBySource").getContext("2d");
  var leadsBySource = new Chart(ctx).Pie(chartData);
});

// Configure the leadsByCity bar chart
$.get("/leads-by-city", function(data) {
  var chartData = [];
  for (var i = 0; i < data.length; i++) {
    chartData.push({
      value: data[i]["id__count"],
      label: data[i]["city"]
    });
  }

  var ctx = document.getElementById("leadsByCity").getContext("2d");
  var leadsByCity = new Chart(ctx).Pie(chartData);
});

// Configure the leadsByZipcode pie chart
$.get("/leads-by-zipcode", function(data) {
  var chartData = [];
  for (var i = 0; i < data.length; i++) {
    chartData.push({
      value: data[i]["id__count"],
      label: data[i]["zipcode"]
    });
  }

  var ctx = document.getElementById("leadsByZipcode").getContext("2d");
  var leadsByZipcode = new Chart(ctx).Pie(chartData);
});
