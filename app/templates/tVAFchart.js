function displaytVAF() {

  const DISPLAYTVAF = document.getElementById("tVAFChart")

  var color = Chart.helpers.color;
  let tVAFChart = new Chart(DISPLAYTVAF, {
    type: 'bar',
    barData2: {
      labels : [{% for item in labeltvaf %}
                     "{{item}}",
                 {% endfor %}],
      datasets : [{
               label:"tVAF",
               backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
               borderColor: window.chartColors.red,
               borderWidth: 1,
               data : [{% for item in tVAF %}
                         {{item}},
                       {% endfor %}]
                  }]
    },
    options: {
        responsive: true,
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: 'tVAF'
        }
    });
}
