/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()
  
  var interval_10 = 0;
  var interval_100 = 0;
  

  //---------------------------------------------------------
  // Graphs
  var ctx = document.getElementById("myChart");

  var data = {};
  /*
  var data = {
    labels: [],
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
    } ]
  };  */

  var options = { 
    animation: false,
    //Boolean - If we want to override with a hard coded scale
    
    
    elements: {
      point:{
          radius: 0
      }},
    scaleShowValues: true,  
    scales: {
      xAxes: [{
        ticks: {
          autoSkip: false
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true,
          min: 0,
          max: 1000
        }
      }]
    },
    legend: {
      display: false
    }
  };

  //var myLineChart = new Chart(ctx).Line(data, options);
  /*
  var myLineChart = new Chart(ctx , {
    type: "line",
    data: data,
    options: options 
});
*/

  

  function setLabels(old_labels, new_labels) {
    if(new_labels != []){
      old_labels.push.apply(old_labels, new_labels)
      if(old_labels.length > 500){
        old_labels.splice(0, 70);
      }
      new_labels = [];
    }
  }

  function setData(old_data, new_data) {
    //console.log("Old data: " + old_data.length)
    //console.log("data: "+new_data.length)
    if(new_data != []){
      /*
      var a = old_data.length/10
      var b = ~~a; //boom!
      old_data.splice(0, b);
      */
      old_data.push.apply(old_data, new_data); 
      if(old_data.length > 500){
        old_data.splice(0, 70);
      }
      new_data = [];
      //console.log("New data: "+old_data.length);
    }
  }
  
  
  var update_chart = function(e){
    if($("#rawcollapse").hasClass("show")){
      if(data != {}){
        $.getJSON('/getrawdata',{start_oid: start_oid, count: count}
        ,function(return_dict){ 
          console.log(return_dict.start_oid); 
          console.log(return_dict.count);   
          console.log(return_dict.value);
          start_oid = return_dict.start_oid;
          count = return_dict.count;
          var timelist = return_dict.time;
          var label = [];    
          for(var i=0; i<timelist.length; i++){
            if(past_seconds < 0){
              past_seconds = 0;
              label.push(past_seconds);
              past_timestamp = timelist[i];
            }
            else if(timelist[i] - past_timestamp >= 1){
              past_seconds += 1;
              label.push(past_seconds);
              past_timestamp = timelist[i];
            }else{
              label.push('');
            }
            
          }
          //alert("value: "+ return_dict.value.length +"\ntime: "+ label.length);
          
          
          setData(data.datasets[0].data, return_dict.value);
          setLabels(data.labels, label);
        });

        //setData(data.datasets[0].data);
        //setData(data.datasets[1].data);
        //setLabels(data.labels);
        
        var myLineChart = new Chart(ctx , {
          type: "line",
          data: data,
          options: options 
        });
      }
    }
  };

 //---------------------------------------------------------

  //FFT page
  $("#btnFFT").click(function(){
    if($("#choosefft").hasClass("collapse") && !$("#choosefft").hasClass("show") ){
      $.getJSON('/getfiltertype',{   
      },function(data){     
        //get all filter name   
        var listfilter = data.listfilter;
        //append to drop down menu  
        
        for(var i in listfilter){
          
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

  var start_oid;
  var count = 0;
  var past_timestamp = 0;
  var past_seconds = -1;
  //Raw page
  $("#btnRaw").click(function(){
    if(is_recording){
      stop_record();
    }
    if($("#rawcollapse").hasClass("collapse") && !$("#rawcollapse").hasClass("show") ){
      console.log("count: 0");
      count = 0;
      past_seconds = -1;
      $.getJSON('/getrawdata',{start_oid: start_oid, count: count}
      ,function(return_dict){ 
        //console.log(return_dict.start_oid); 
        //console.log(return_dict.count);   
        //console.log(return_dict.value);
        start_oid = return_dict.start_oid;
        count = return_dict.count;
        var timelist = return_dict.time;
        var label = [];    
        for(var i=0; i<timelist.length; i++){
          if(past_seconds < 0){
            past_seconds = 0;
            label.push(past_seconds);
            past_timestamp = timelist[i];
          }
          if(timelist[i] - past_timestamp >= 1){
            past_seconds += 1;
            label.push(past_seconds);
            past_timestamp = timelist[i];
          }else{
            label.push('');
          }
        }
        
        
        //data['datasets']['data'] = return_dict.value;
        data = {
          labels: label,
          datasets: [{
            
            lineTension: 0,
            backgroundColor: 'transparent',
            borderColor: '#007bff',
            borderWidth: 4,
            pointBackgroundColor: '#007bff',  
            data: return_dict.value
          }]};
        console.log(data)
        var myLineChart = new Chart(ctx , {
          type: "line",
          data: data,
          options: options 
        });


        });
      }
  });
 

  
  
  
  $('#fftnamecontainer a').on('click', function(e){
    var selText = $(this).text();
    alert(selText);
  });

  //auto refresh
  setInterval(function () {
    

    update_chart();

    interval_10 += 1;
    if(interval_10 >= 1){
      interval_10 = 0;
      sync_time();
    }
    
    
    
    interval_100 += 1;
    if(interval_100 >= 19){
      interval_100 = 0;
      check_alive();
    }

    if(is_recording == true){
      $("#btn_record").hide();
      $("#btn_recording").show();
    }
    else{
      $("#btn_record").show();
      $("#btn_recording").hide();
    }
  
  }, 500);

 
  
  //---------------------------------------------------------
  //Record raw
  var is_recording = false;
  var record_start_position = 0;
  $('#btn_record').on('click', function(e){
    is_recording = true;
    if(data.datasets[0].data != []){
      record_start_position = count - data.datasets[0].data.length;
    }
    else{
      record_start_position = 0;
    }
  });
  $('#btn_recording').on('click', function(e){
    stop_record();
  });

  var stop_record =function(e){
    is_recording = false;
    var record_name = prompt("Please enter name of this record", "record"+Date.now());

    if (record_name == null || record_name == "") {
      alert("Canceled!");
    } else {
        //alert("start_oid: "+start_oid+"\n start_position: "+record_start_position+"\n endlength: "+count);
      $.getJSON('/savechartrecord',{reference_oid: start_oid, start_position: record_start_position, reference_end: count, type_of_record:"RAW", name:record_name}
      ,function(return_dict){ 
        if(return_dict.successful == true){
          alert("Saved!");
        }else{
          alert("Error!");
        }
        count = 0;
      });
    }  
  };
  //---------------------------------------------------------
 
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
      //console.log(data.alive);
      if(data.alive == false){ 
        $('#showoffline').show();
        count = 0;
      }
      else{ 
        $('#showoffline').hide();
    }
    });
  };
  check_alive()
})()







