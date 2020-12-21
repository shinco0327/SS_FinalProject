/* globals Chart:false, feather:false */

(function () {
    'use strict'
  
    feather.replace()
    
    
  
   
    
    
   
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
  var interval_10 = 0;
  setInterval(function () {
    

    
    interval_10 += 1;
    if(interval_10 >= 1){
      interval_10 = 0;
      sync_time();
    }
    
  }, 500);
  })()
  
  
  
  
  
  
  
  