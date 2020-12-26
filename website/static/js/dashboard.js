/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  
  //check device alive
  var check_alive_and_rate=function(e){
    //$('#showoffline').hide();
    $.getJSON('/checkalive',{   
    },function(data){     
      //console.log(data.alive);
      if(data.alive == false){ 
        $('#heartpresent').text('--');
        $('#heartpresent').addClass('text-black-50');
        $('#showoffline').show();
        $('#heartbpm').hide();
        $('#btnRealtime').addClass('disabled');
      }
      else{ 
        $.getJSON('/getheartrate',{   
        },function(data){     
          //console.log(data.heartrate);
          $('#showoffline').hide();
          $('#heartpresent').removeClass('text-black-50');
          $('#btnRealtime').removeClass('disabled');
          if(data.heartrate.mode == 'disconnect'){
            $('#heartpresent').text('Internet Unstable');
            $('#heartbpm').hide();
          }
          else if(data.heartrate.mode == 'standby'){
            $('#heartpresent').text('Standby...');
            $('#heartbpm').hide();
          }
          else if(data.heartrate.mode == 'measuring'){
            $('#heartpresent').text('Measuring...');
            $('#heartbpm').hide();
          }
          else if(data.heartrate.mode == 'done'){
            $('#heartpresent').text(data.heartrate.heartrate);
            $('#heartbpm').show();
          }
        });
        
        
      }
    });
  };
  check_alive_and_rate()


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


  //auto refresh
  setInterval(function () {
    check_alive_and_rate();
    sync_time();
  }, 500);
})()
