/* globals Chart:false, feather:false */

(function () {
    'use strict'
  
    feather.replace()
    
    
  
   
    var historylist = [];
    var listpointer = 0;

    var getHistorylist = function(e){
        $.getJSON('/gethistorylist',{   
        },function(return_dict){     
            historylist = return_dict.historylist;
            for( var i in historylist){
                if(i == 8){
                    $("#btn_nextpage").show();
                    break;
                }
                $("#t"+i).show();
                //$("#t"+i).removeClass("hide");
                $("#t"+i+"num").text(parseInt(i)+1);    
                $("#t"+i+"name").text(historylist[i].name); 
                $("#t"+i+"type").text(historylist[i].type_of_record); 
                $("#t"+i+"time").text(historylist[i].time);
                listpointer = i; 
            }
        }); 
    };
   

    $('#btn_nextpage').on('click', function(e){
        $("#btn_lastpage").show();
        var pointer_save = listpointer
        for( var i in historylist){ 
            if(i == 8){
                break;
            }
            //$("#t"+i).removeClass("hide");
            if(parseInt(i)+parseInt(pointer_save) < historylist.length ){
                $("#t"+i).show();
                $("#t"+i+"num").text(parseInt(i)+1+parseInt(pointer_save));    
                $("#t"+i+"name").text(historylist[parseInt(i)+parseInt(pointer_save)].name); 
                $("#t"+i+"type").text(historylist[parseInt(i)+parseInt(pointer_save)].type_of_record); 
                $("#t"+i+"time").text(historylist[parseInt(i)+parseInt(pointer_save)].time);
                listpointer = parseInt(i)+parseInt(pointer_save); 
            }else{
                $("#btn_nextpage").hide();
                $("#t"+i).hide();
            }
        }
    });
    
    $('#btn_lastpage').on('click', function(e){
        $("#btn_nextpage").show();
        var pointer_save = listpointer;
        if(listpointer%7 == 0){
            pointer_save -= 14;
        }
        else{
            pointer_save -= listpointer%7;
            pointer_save -= 7;
        }
        if(pointer_save == 0){
            $("#btn_lastpage").hide();
        }
        
        for( var i in historylist){ 
            if(i == 8){
                break;
            }
            $("#t"+i).show();
            $("#t"+i+"num").text(parseInt(i)+1+parseInt(pointer_save));    
            $("#t"+i+"name").text(historylist[parseInt(i)+parseInt(pointer_save)].name); 
            $("#t"+i+"type").text(historylist[parseInt(i)+parseInt(pointer_save)].type_of_record); 
            $("#t"+i+"time").text(historylist[parseInt(i)+parseInt(pointer_save)].time);
            listpointer = parseInt(i)+parseInt(pointer_save); 
        }
    });

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

    getHistorylist();
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
  
  
  
  
  
  
  
  