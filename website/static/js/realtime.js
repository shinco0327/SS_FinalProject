/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()
  
  var interval_10 = 0;
  var interval_100 = 0;
  

  //---------------------------------------------------------
  // Graphs
  var ctx0 = document.getElementById("myChart0");
  var ctx1 = document.getElementById("myChart1");
  var ctxFreq = document.getElementById("FreqChart");

  var data = {};
  
  var options = { 
    animation: {
      duration: 0 // general animation time
    },
    //Boolean - If we want to override with a hard coded scale
    
    hover: {
      animationDuration: 0 // duration of animations when hovering an item
    },
    responsiveAnimationDuration: 0, // animation duration after a resize
    
    elements: {
      line: {
        tension: 0 // disables bezier curves
      },
      point:{
          radius: 0
      }},
    scaleShowValues: true,  
    maintainAspectRatio: true,
    scales: {
      xAxes: [{
        ticks: {
          autoSkip: false
        },
        scaleLabel: {
          display: true,
          labelString: 'Time (sec)'
        }
      }],
      yAxes: [{
        ticks: {
          //beginAtZero: true,
          min: 0,
          max: 1000
        }
      }]
    },
    legend: {
      display: false
    }
  };

  var options_spect = { 
    animation: {
      duration: 0 // general animation time
    },
    //Boolean - If we want to override with a hard coded scale
    
    hover: {
      animationDuration: 0 // duration of animations when hovering an item
    },
    responsiveAnimationDuration: 0, // animation duration after a resize
    
    elements: {
      line: {
        tension: 0 // disables bezier curves
      },
      point:{
          radius: 0
      }},
    scaleShowValues: true,  
    maintainAspectRatio: true,
    scales: {
      xAxes: [{
        ticks: {
          autoSkip: true
        },
        scaleLabel: {
          display: true,
          labelString: 'Frequency (Hz)'
        }
      }],
      yAxes: [{
        ticks: {
          //beginAtZero: true,
          min: 0,
          max: 150
        }
      }]
    },
    legend: {
      display: false
    }
  };

  

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
    if($("#Waveform_container").is(':visible') && $("#Graphcollapse").hasClass('show')){
      if(data != {}){
        $.getJSON('/getgraphdata',{start_oid: start_oid, count: count, graphmode:GraphMode}
        ,function(return_dict){ 
          //console.log(return_dict.start_oid); 
          //console.log(return_dict.count);   
          //console.log(return_dict.value);
          start_oid = return_dict.start_oid;
          count = return_dict.count;
          var timelist = return_dict.time;
          var label = [];    
          if(count == 0){
            past_seconds = -1;
            GraphProcessing();
            return false; 
          }
          
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
        var myLineChart = new Chart(ctx0 , {
          type: "line",
          data: data,
          options: options 
        });
     
      }
      else{
        GraphProcessing();
      }
    }
  };

  var update_spectrum = function(e){
    if($("#collapseSpectrum").hasClass("show")){ 
      $.getJSON('/getspectrum',{ graphmode:GraphMode
      },function(return_dict){     
        //console.log(return_dict);

        var data_spect = {
          labels: return_dict.freq,
          datasets: [{
            
            lineTension: 0,
            backgroundColor: 'transparent',
            borderColor: '#007bff',
            borderWidth: 4,
            pointBackgroundColor: '#007bff',  
            data: return_dict.value
          }]};
        
          var myLineChart1 = new Chart(ctx1 , {
            type: "line",
            data: data_spect,
            options: options_spect 
          });  
          options_spect.scales.yAxes[0].ticks.max = Math.max.apply(this,  return_dict.value) + 5;    
        
      });
    }
  };
  //--------------------------------------------------------
  $("#btnAbout").click(function(e){
    if(GraphMode.substring(0,3) == "LPF"){
      if(GraphMode == "LPFButter"){
        $("#aboutModaltitle").text("About Butterworth Filter");
        $("#plotz").hide();
      }else if(GraphMode.substring(3,5)=="pt"){
        $("#aboutModaltitle").text("About "+GraphMode.substring(5)+"-pt Average Filter");
        $("#graphz").attr("src", "static/images/zplot"+GraphMode.substring(5)+"pt.png");
        $("#plotz").show();
      }
    }
    $.getJSON('/getfreqresponse',{ graphmode:GraphMode
    },function(return_dict){     
      console.log(return_dict);
      var myLineChartFreq = new Chart(ctxFreq , {
        type: "line",
        data: {
          labels: return_dict.freq,
          datasets: [{ 
            lineTension: 0,
            backgroundColor: 'transparent',
            borderColor: '#007bff',
            borderWidth: 4,
            pointBackgroundColor: '#007bff',  
            data: return_dict.value
          }]},
        options: { 
          animation: {
            duration: 0 
          },          
          hover: {
            animationDuration: 0 
          },
          responsiveAnimationDuration: 0, 
          elements: {
            line: {
              tension: 0
            },
            point:{
                radius: 0
            }},
          scaleShowValues: true,  
          maintainAspectRatio: true,
          scales: {
            xAxes: [{
              ticks: {
                autoSkip: true,
                maxTicksLimit: 5
              },
              scaleLabel: {
                display: true,
                labelString: 'Frequency (Hz)'
              }
            }],
            yAxes: [{
              ticks: {
                min: 0,
                max: 1.5
              },
              scaleLabel: {
                display: true,
                labelString: 'Amplitude'
              }
            }]
          },
          legend: {
            display: false
          }
        }
      });
      
      
    });
    $("#aboutModal").modal("show");
  });


  $("#btnSpect").click(function(e){
    if(!$("#collapseSpectrum").hasClass("show")){ 
      $.getJSON('/getspectrum',{ graphmode:GraphMode
      },function(return_dict){     
        //console.log(return_dict);

        var data_spect = {
          labels: return_dict.freq,
          datasets: [{
            
            lineTension: 0,
            backgroundColor: 'transparent',
            borderColor: '#007bff',
            borderWidth: 4,
            pointBackgroundColor: '#007bff',  
            data: return_dict.value
          }]};
        
          var myLineChart1 = new Chart(ctx1 , {
            type: "line",
            data: data_spect,
            options: options_spect 
          });  
          options_spect.scales.yAxes[0].ticks.max = Math.max.apply(this,  return_dict.value) + 5;    
        
      });
    }
  });
 //---------------------------------------------------------
  //FFT page
  $("#btnLPF").click(function(){
    if($("#Graphcollapse").hasClass("show") && GraphMode.substring(0,3) == "LPF" && !$("#Waveform_container").is(':visible')){
      $("#Graphcollapse").collapse('hide');
    }
    else{
      $("#Graphcollapse").collapse('show');
      GraphMode = "LPF";
      $("#graphtype").text("Type: Low Pass Filter");
      $("#Waveform_container").hide();
      $("#Spectrum_container").hide();
      $("#btnAbout").hide();
      $("#LPFoption").show();
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
        //console.log(listfilter);
        //open dropdown
        //if ($('.dropdown').find('.dropdown-menu').is(":hidden")){
        //  $('.dropdown-toggle').dropdown('toggle');
        //}
      });
    }
  });

  //LPF
  $("#btnButter").click(function(){
    $("#Waveform_container").show();
    $("#Spectrum_container").show();
    $("#LPFoption").hide();
    $("#btnAbout").show();
    GraphMode = "LPFButter";
    $("#graphtype").text("Type: Low Pass Filter/Butterworth");
    GraphProcessing();
  });
  $('#fftnamecontainer a').on('click', function(e){
    var selText = $(this).text();
    $("#graphtype").text("Type: Low Pass Filter/"+selText);
    GraphMode = "LPF" + 'pt' +selText.replace("-pt",'');
    //alert(GraphMode);
    $("#Waveform_container").show();
    $("#Spectrum_container").show();
    $("#LPFoption").hide();
    $("#btnAbout").show();
    GraphProcessing();
  });


  var start_oid;
  var count = 0;
  var past_timestamp = 0;
  var past_seconds = -1;
  var GraphMode = '';
  //Raw page
  $("#btnRaw").click(function(){
    console.log(GraphMode);
    if($("#Graphcollapse").hasClass("show") && GraphMode == "RAW"){
      $("#Graphcollapse").collapse('hide');
    }else{
      $("#graphtype").text("Type: RAW");
      $("#btnAbout").hide();
      $("#Graphcollapse").collapse('show');
      $("#Waveform_container").show();
      $("#Spectrum_container").show();
      $("#LPFoption").hide();
      GraphMode = "RAW";
      GraphProcessing();
    }
  });

  //DCF page
  $("#btnDCF").click(function(){
    if($("#Graphcollapse").hasClass("show") && GraphMode == "DCF"){
      $("#Graphcollapse").collapse('hide');
    }else{
      $("#graphtype").text("Type: DC Filted");
      $("#Graphcollapse").collapse('show');
      $("#Waveform_container").show();
      $("#Spectrum_container").show();
      $("#btnAbout").hide();
      $("#LPFoption").hide();
      GraphMode = "DCF";
      GraphProcessing();
    }
  });
 

  var GraphProcessing = function(e){
    console.log(options);
    if(GraphMode == "RAW"){
      options.scales.yAxes[0].ticks.min = 0;
      options.scales.yAxes[0].ticks.max = 1000;
    }else if(GraphMode == "DCF"){
      options.scales.yAxes[0].ticks.min = -5;
      options.scales.yAxes[0].ticks.max = 10;
    }else if(GraphMode.substring(0,3) == "LPF"){
      options.scales.yAxes[0].ticks.min = -2;
      options.scales.yAxes[0].ticks.max = 5;
    }
    else{
      options.scales.yAxes[0].ticks.min = 0;
      options.scales.yAxes[0].ticks.max = 1000;
    }
    if(is_recording){
      stop_record();
    }
    console.log("count: 0");
    count = 0;
    if(count == 0){
      past_seconds = -1;
    }
    $.getJSON('/getgraphdata',{start_oid: start_oid, count: count, graphmode:GraphMode}
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
      console.log(data);
      
      var myLineChart = new Chart(ctx0 , {
        type: "line",
        data: data,
        options: options 
      });        
    });
    
  }
  
  
 

  //auto refresh
  setInterval(function () {
    

    update_chart();

    interval_10 += 1;
    if(interval_10 >= 1){
      interval_10 = 0;
      update_spectrum();
      check_alive();
      //sync_time();
    }
    if(is_recording == true){
      $("#btn_record0").hide();
      $("#btn_recording0").show();
    }
    else{
      $("#btn_record0").show();
      $("#btn_recording0").hide();
    }
  }, 500);

  //---------------------------------------------------------
  //Record Grpah
  var is_recording = false;
  var record_start_position = 0;
  var heartrate_store = [];
  var heartrate_stable = 0;
  $('#btn_record0').on('click', function(e){
    is_recording = true;
    heartrate_stable = 0;
    if(data.datasets[0].data != []){
      record_start_position = count - data.datasets[0].data.length;
      if(record_start_position < 0){
        record_start_position = 0;
      }
    }
    else{
      record_start_position = 0;
    }
  });
  $('#btn_recording0').on('click', function(e){
    stop_record();
  });


  var reference_end;
  var stop_record =function(e){
    $("#Heartcol").css("background-color", 'rgba(255,255,255,' + 1 + ')');
    is_recording = false;
    reference_end = count;
    $("#record_name").val("");
    $("#remarks").val("");
    $("#SaveModal").modal('show');
    $("#record_name").val("record"+Date.now());
  };
  $("#SaveModalsubmit").on('click', function(e){
    if($("#record_name").val() == '' || $("#record_name").val()== null){
      alert("Please enter record name");
      $("#record_name").css("background-color", "#EF9A9A");
    }else{
      //alert($("#record_name").val()+'\n'+ $("#subject_name").val()+'\n'+$("#remarks").val());
      $.getJSON('/savechartrecord',{reference_oid: start_oid, start_position: record_start_position, reference_end: reference_end, record_name:$("#record_name").val(),
       subject_name:$("#subject_name").val(), remarks:$("#remarks").val(), heartrate:heartrate_stable}
      ,function(return_dict){ 
        if(return_dict.successful == true){
          $("#SaveModal").modal('hide');
          $("#record_name").css("background-color", "#FFFFFF");
          alert("Saved!");
          count = 0;
          past_seconds = -1;
        }else{
          alert("Error!");
        }
      });
      
    }
    });

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
        $("#Heartcol").hide();
        count = 0;
      }
      else{ 
        $('#showoffline').hide();
        $("#Heartcol").show();
        $.getJSON('/getheartrate',{   
        },function(data){       
          if(data.heartrate.mode == 'disconnect'){
            $('#heartpresent').text('Internet Unstable');
          }
          else if(data.heartrate.mode == 'standby'){
            $('#heartpresent').text('Standby...');
            $("#Heartcol").css("background-color", 'rgba(255,255,255,' + 1 + ')');
          }
          else if(data.heartrate.mode == 'measuring'){
            $('#heartpresent').text('Measuring...');
            heartrate_store = [];
            $("#Heartcol").css("background-color", 'rgba(255,255,255,' + 1 + ')');
          }
          else if(data.heartrate.mode == 'done'){
            $('#heartpresent').text(data.heartrate.heartrate +" bpm");
            
            heartrate_store.push(data.heartrate.heartrate);
            if(heartrate_store.length > 5){
              heartrate_store.splice(0, 1);
              var temporary = data.heartrate;
              var total = 0;
              for(var i in heartrate_store){
                total += parseInt(heartrate_store[i]);
                if(Math.abs(temporary - heartrate_store[i]) >= 5){
                  heartrate_store = [temporary];
                  break;
                }
                if(i == heartrate_store.length - 1){
                  if(is_recording){
                    heartrate_stable = (
                      parseFloat(data.heartrate.heartrate) + 
                      parseFloat(heartrate_store[heartrate_store.length - 1]) + 
                      parseFloat(heartrate_store[heartrate_store.length - 2])
                      + 
                      parseFloat(heartrate_store[heartrate_store.length - 3]) + 
                      parseFloat(heartrate_store[heartrate_store.length - 4]))/5;
                  }
                  console.log("stable heartrate: "+(
                    parseFloat(data.heartrate.heartrate) + 
                    parseFloat(heartrate_store[heartrate_store.length - 1]) + 
                    parseFloat(heartrate_store[heartrate_store.length - 2])
                    + 
                    parseFloat(heartrate_store[heartrate_store.length - 3]) + 
                    parseFloat(heartrate_store[heartrate_store.length - 4]))/5+"\nlist: "+heartrate_store);
                  //$("#Heartcol").addClass("border-success");
                  $("#Heartcol").css("background-color", 'rgba(22,161,22,' + 0.58 + ')');
                }
              }
            }
            
          }
        });
    }
    });
  };
  check_alive()

  
  
})()







