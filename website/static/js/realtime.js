/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  // Graphs
  var ctx = document.getElementById('myChart')
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

})()







