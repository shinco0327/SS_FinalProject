/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()
  
  var intervel_10 = 0;
  var dps = []; // dataPoints
  // Graphs
  var ctx = document.getElementById("myChart");

  var data = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [{
      
      lineTension: 0,
      backgroundColor: 'transparent',
      borderColor: '#007bff',
      borderWidth: 4,
      pointBackgroundColor: '#007bff',  
      data: []
    } /*, {
      label: "My Second dataset",
      fillColor: "rgba(151,187,205,0.2)",
      strokeColor: "rgba(151,187,205,1)",
      pointColor: "rgba(151,187,205,1)",
      pointStrokeColor: "#fff",
      pointHighlightFill: "#fff",
      pointHighlightStroke: "rgba(151,187,205,1)",
      data: [87, 87, 87,87 ,87,87,87]
    } */]
  };
  var options = {
    animation: false,
    //Boolean - If we want to override with a hard coded scale
    scaleOverride: true,
    //** Required if scaleOverride is true **
    //Number - The number of steps in a hard coded scale
    scaleSteps: 10,
    //Number - The value jump in the hard coded scale
    scaleStepWidth: 10,
    //Number - The scale starting value
    scaleStartValue: 0,
    elements: {
      point:{
          radius: 0
      }},
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: false
        }
      }]
    },
    legend: {
      display: false
    }
  };

  //var myLineChart = new Chart(ctx).Line(data, options);
  var myLineChart = new Chart(ctx , {
    type: "line",
    data: data,
    options: options 
});

  

  function setLabels(labels) {
    var nextMonthIndex = months.indexOf(labels[labels.length - 1]) + 1;
    var nextMonthName = months[nextMonthIndex] != undefined ? months[nextMonthIndex] : "January";
    labels.push(nextMonthName);
    labels.shift();
  }

  function setData(data) {
    data.push(Math.floor(Math.random() * 100) + 1);
    data.shift();
  }
  
  function convertMonthNameToNumber(monthName) {
    var myDate = new Date(monthName + " 1, 2016");
    var monthDigit = myDate.getMonth();
    return isNaN(monthDigit) ? 0 : (monthDigit + 1);
  }
  
  var months = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];


  /*
  // eslint-disable-next-line no-unused-vars
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
      ],
      datasets: [{
        data: [
          15339,
          21345,
          18483,
          24003,
          23489,
          24092,
          12034
        ],
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#007bff',
        borderWidth: 4,
        pointBackgroundColor: '#007bff'
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: false
          }
        }]
      },
      legend: {
        display: false
      }
    }
  })
  */

  //FFT page
  $("#btnFFT").click(function(){
    if($("#choosefft").hasClass("collapse") && !$("#choosefft").hasClass("show") ){
      $.getJSON('/getfiltertype',{   
      },function(data){     
        //get all filter name   
        var listfilter = data.listfilter;
        //append to drop down menu  
        //var ul = document.getElementById('fftnamecontainer');
        //var str1 = ''
        for(var i in listfilter){
          //str1 += '<li><a class="dropdown-item">'+listfilter[i]+'</a></li>';
          //var li = document.createElement("li");
          //var a = document.createElement("a");
          //a.className = "dropdown-item";
          //a.appendChild(document.createTextNode(listfilter[i]));
          //li.appendChild(a);
          //ul.appendChild(li);
          var locate = parseInt(i)+ 1;
          $('#'+'d'+locate).removeClass("hide");
          $('#'+'d'+locate).text(listfilter[i]);
        }
        //ul.innerHTML = str1;
        console.log(listfilter);
        //open dropdown
        if ($('.dropdown').find('.dropdown-menu').is(":hidden")){
          $('.dropdown-toggle').dropdown('toggle');
        }
      });
    }
  });

 
  
  
  $('#fftnamecontainer a').on('click', function(e){
    var selText = $(this).text();
    alert(selText);
  });

  //auto refresh
  setInterval(function () {
    sync_time();
    setData(data.datasets[0].data);
    //setData(data.datasets[1].data);
    setLabels(data.labels);
    var myLineChart = new Chart(ctx , {
      type: "line",
      data: data,
      options: options 
    });
    intervel_10 += 1;
    if(intervel_10 == 9){
      intervel_10 = 0;
      check_alive();
    }
  
  }, 1000);


  //Change_current_time
  var sync_time=function(e){ //
    $.getJSON('/gettstamp',{   
    },function(data){     
        var time = new Date(data.timestamp *1000);
        var hours, minutes, seconds;
        if(time.getHours() <= 9){
          hours = '0' + time.getHours();
        }else{
          hours = time.getHours();
        }
        if(time.getMinutes() <= 9){
          minutes = '0' + time.getMinutes();
        }else{
          minutes = time.getMinutes();
        }
        if(time.getSeconds() <= 9){
          seconds = '0' + time.getSeconds();
        }else{
          seconds = time.getSeconds();
        }
        $('#currentTime').text('Current Time ' + hours + ' : ' + minutes + ' : '+ seconds);
    });
  };

  //check device alive
  var check_alive=function(e){
    //$('#showoffline').hide();
    $.getJSON('/checkalive',{   
    },function(data){     
      console.log(data.alive);
      if(data.alive == false){ $('#showoffline').show();}
      else{ $('#showoffline').hide();}
    });
  };
  check_alive()
})()







