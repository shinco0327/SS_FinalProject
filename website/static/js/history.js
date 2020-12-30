/* globals Chart:false, feather:false */

(function () {
    'use strict'
  
    feather.replace()
    
    $(".table tbody tr").click(function(){
        $("#tablePage").hide();
        $("#detailPage").show();
        $("#recrodname").text("Record Name: "+historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].record_name); 
        $("#subjectname").text("Subject Name: "+historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].subject_name); 
        if(historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].heartrate > 50){
            $("#heartrate").text("Heartrate: "+historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].heartrate.toFixed(2)); 
        }else{
            $("#heartrate").text("Heartrate: Did Not Measure"); 
        }
        $("#time").text("Time: "+historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].time); 
        if(historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].remarks != ""){
            $("#remarks").show();
            $("#remarks").text("Remarks: "+historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].remarks);}
        else{
            $("#remarks").hide();
        }
        is_playing.reset_graph(); 
        is_playing.new_record(historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8]._id,
        historylist[parseInt($(this).attr('id').substring(1))+parseInt(page)*8].count);
        //alert($(this).attr('id'));
    });

    $("#btn_backtable").on('click', function(e){
        is_playing.end();
        $("#tablePage").show();
        $("#detailPage").hide();
    });

    class PlayControl{
        constructor(btnplay, btnpause, btnrestart, ctx){
            this.btnplay = btnplay;
            this.btnpause = btnpause;
            this.btnrestrt = btnrestart;
            this.ctx = ctx;
            this.options = { 
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
        }
        new_record(record_oid, total_length){
            this.count = 0;
            this.data = {
                labels: [],
                datasets: [{
                    
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff',  
                data: []
                }]
            };
            this.past_seconds = -1;
            this.past_timestamp = 0;
            this.record_oid = record_oid;
            this.GraphMode = "RAW";
            this.comparemode = 'OFF';
            this.total_length = total_length;
            this.play_state = 0;
        }
        play(){
            this.btnplay.hide();
            this.btnpause.show();
            this.btnrestrt.show();
            this.play_state = 1;
        }
        pause(){
            this.btnplay.show();
            this.btnpause.hide();
            this.btnrestrt.show();
            this.play_state = 0;
        }
        is_continue(){
            if(this.count >0){
                return true;
            }
            else{
                return false;
            }
        }
        restart(){
            this.count = 0;
            this.past_seconds = -1;
            this.past_timestamp = 0;
            this.btnplay.show();
            this.btnpause.hide();
            this.btnrestrt.show();
            this.play_state = 0;
        }
        reset_graph(){
            this.data = {
                labels: [],
                datasets: [{
                    
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff',  
                data: []
                },{
                    lineTension: 0,
                    backgroundColor: 'transparent',
                    borderColor: '#FFA500',
                    borderWidth: 4,
                    pointBackgroundColor: '#FFA500',  
                    data: []
                    }]
            
            }
            
            var myLineChart = new Chart(this.ctx , {
                type: "line",
                data: this.data,
                options: this.options 
            });
        }
        compare_Graph(GraphMode){
            this.count = 0;
            this.past_seconds = -1;
            this.comparemode = GraphMode
            this.past_timestamp = 0;
            if(this.play_state == 1){
                this.btnplay.hide();
                this.btnpause.show();
                this.btnrestrt.show();
                this.play_state = 1;
            }else{
                this.btnplay.show();
                this.btnpause.hide();
                this.btnrestrt.hide();
                this.play_state = 0;
            }
        }
        change_GraphMode(GraphMode){
            this.count = 0;
            this.past_seconds = -1;
            this.GraphMode = GraphMode;
            this.past_timestamp = 0;
            if(this.play_state == 1){
                this.btnplay.hide();
                this.btnpause.show();
                this.btnrestrt.show();
                this.play_state = 1;
            }else{
                this.btnplay.show();
                this.btnpause.hide();
                this.btnrestrt.hide();
                this.play_state = 0;
            }
            if(GraphMode == "RAW"){
                this.options.scales.yAxes[0].ticks.min = 0;
                this.options.scales.yAxes[0].ticks.max = 1000;
              }else if(GraphMode == "DCF"){
                this.options.scales.yAxes[0].ticks.min = -5;
                this.options.scales.yAxes[0].ticks.max = 10;
              }else if(GraphMode.substring(0,3) == "LPF"){
                this.options.scales.yAxes[0].ticks.min = -2;
                this.options.scales.yAxes[0].ticks.max = 5;
              }
              else{
                this.options.scales.yAxes[0].ticks.min = 0;
                this.options.scales.yAxes[0].ticks.max = 1000;
              }
    
        }
        can_update(){
            if(this.record_oid != "" && (this.count < this.total_length) && this.play_state == 1){
                return true;
            }else if(this.record_oid != "" && (this.count >= this.total_length)){
                this.btnplay.hide();
                this.btnpause.hide();
                this.btnrestrt.show();
            }
            return false;   
        }
        new_chart(return_dict){
            var timelist = return_dict.time;
            this.count = return_dict.count;
            var label = []
            if(this.play_state == 0){
                return false;
            }
            for(var i=0; i<timelist.length; i++){
                if(this.past_seconds < 0){
                    this.past_seconds = 0;
                    label.push(this.past_seconds);
                    this.past_timestamp = timelist[i];
                }
                else if(timelist[i] - this.past_timestamp >= 1){
                    this.past_seconds += 1;
                    label.push(this.past_seconds);
                    this.past_timestamp = timelist[i];
                }else{
                    label.push('');
                }
            }
            console.log(label);
            console.log(return_dict.value);
            var compare_list = []
            if(this.comparemode != 'OFF'){
                compare_list = return_dict.comparevalue;
            }
            this.data = {
                labels: label,
                datasets: [{  
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff',  
                data: return_dict.value
                }, 
                {
                    lineTension: 0,
                    backgroundColor: 'transparent',
                    borderColor: '#FFA500',
                    borderWidth: 4,
                    pointBackgroundColor: '#FFA500',  
                    data: compare_list
                    }]
            };
            
            var myLineChart = new Chart(this.ctx , {
                type: "line",
                data: this.data,
                options: this.options 
            });
        }
        update_graph(return_dict){
            if(return_dict == {} || this.count == 0){
                return false;
            }
            var timelist = return_dict.time;
            this.count = return_dict.count;
            var label = []
            for(var i=0; i<timelist.length; i++){
                if(this.past_seconds < 0){
                    this.past_seconds = 0;
                    label.push(this.past_seconds);
                    this.past_timestamp = timelist[i];
                }
                else if(timelist[i] - this.past_timestamp >= 1){
                    this.past_seconds += 1;
                    label.push(this.past_seconds);
                    this.past_timestamp = timelist[i];
                }else{
                    label.push('');
                }
            }

            if(label != []){
                
                this.data.labels.push.apply(this.data.labels, label);
                if(this.data.labels.length > 500){
                    this.data.labels.splice(0, 70);
                }
            }
            if(return_dict.value != []){
                this.data.datasets[0].data.push.apply(this.data.datasets[0].data, return_dict.value); 
                if(this.data.datasets[0].data.length > 500){
                    this.   data.datasets[0].data.splice(0, 70);
                }
            }
            if(return_dict.comparevalue != [] && this.comparemode != 'OFF'){
                this.data.datasets[1].data.push.apply(this.data.datasets[1].data, return_dict.comparevalue); 
                if(this.data.datasets[1].data.length > 500){
                    this.   data.datasets[1].data.splice(0, 70);
                }
            }
            
            
            var myLineChart = new Chart(this.ctx , {
                type: "line",
                data: this.data,
                options: this.options 
            });
            
        }
        gettoJson(){
            return {record_oid: this.record_oid, count: this.count, graphmode: this.GraphMode, comparemode: this.comparemode,interval:0.5}
        }
        end(){
            this.count = 0;
            this.record_oid = '';
            this.btnplay.show();
            this.btnpause.hide();
            this.btnrestrt.hide();
        }
    };

    var is_playing = new PlayControl($("#btnplay"), $("#btnpause"), $("#btnrestart"), document.getElementById("myChart").getContext("2d"));
    
    
    $("#btnplay").on('click', function(e){
        is_playing.play();
        $.getJSON('/gethistorygraph', is_playing.gettoJson()
        ,function(return_dict){ 
            if(is_playing.is_continue() == true){
                is_playing.update_graph(return_dict);
            }else{
                is_playing.new_chart(return_dict);
            }
        });
    }); 
    $("#btnpause").on('click', function(e){
        is_playing.pause();
    });
    $("#btnrestart").on('click', function(e){
        is_playing.restart();
        is_playing.reset_graph();
        //$.getJSON('/gethistorygraph', is_playing.gettoJson()
        //,function(return_dict){ 
        //    is_playing.new_chart(return_dict);
        //});
    });

    //Choose to show
    $('#typeofgraph a').on('click', function(e){
        var selText = $(this).text();
        var last3 = selText.slice(-3);
        if(last3 == '-pt'){
            $("#btntypegraph").text("Graph Type: FIR/"+ selText);
            is_playing.change_GraphMode("LPFpt"+selText.substring(0, selText.length - 3));
        }else if(selText == "Butterworth"){
            is_playing.change_GraphMode("LPFButter");
            $("#btntypegraph").text("Graph Type: "+ selText);
        }else if(selText == "DC Filted"){
            is_playing.change_GraphMode("DCF");
            $("#btntypegraph").text("Graph Type: "+ selText);
        }else{
            is_playing.change_GraphMode("RAW");
            $("#btntypegraph").text("Graph Type: "+ selText);
        }
        $.getJSON('/gethistorygraph', is_playing.gettoJson()
            ,function(return_dict){ 
                is_playing.reset_graph();
                is_playing.new_chart(return_dict);
        });
      });

    //Compare with
    //Choose to show
    $('#typecompare a').on('click', function(e){
        var selText = $(this).text();
        var last3 = selText.slice(-3);
        if(last3 == '-pt'){
            $("#btncompare").text("Compare with: FIR/"+ selText);
            is_playing.compare_Graph("LPFpt"+selText.substring(0, selText.length - 3));
        }else if(selText == "Butterworth"){
            is_playing.compare_Graph("LPFButter");
            $("#btncompare").text("Compare with: "+ selText);
        }else if(selText == "DC Filted"){
            is_playing.compare_Graph("DCF");
            $("#btncompare").text("Compare with: "+ selText);
        }else if(selText == "RAW"){
            is_playing.compare_Graph("RAW");
            $("#btncompare").text("Compare with: "+ selText);
        }else{
            is_playing.compare_Graph("OFF");
            $("#btncompare").text("Compare with: OFF");
        }
        $.getJSON('/gethistorygraph', is_playing.gettoJson()
            ,function(return_dict){ 
                is_playing.reset_graph();
                is_playing.new_chart(return_dict);
        });
      });
  
   
    var historylist = [];
    var listpointer = 0;
    var page = 0;
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
                $("#t"+i+"recordname").text(historylist[i].record_name); 
                $("#t"+i+"subjectname").text(historylist[i].subject_name); 
                $("#t"+i+"time").text(historylist[i].time);
                if(historylist[i].heartrate > 50){
                    $("#t"+i+"heartrate").text(historylist[i].heartrate.toFixed(2)); 
                }else{
                    $("#t"+i+"heartrate").text("Didn't Measure"); 
                }
                listpointer = i; 
            }
        }); 
    };
   

    $('#btn_nextpage').on('click', function(e){
        page ++;
        $("#btn_lastpage").show();
        var pointer_save = listpointer;
        pointer_save ++;
        for( var i in historylist){ 
            if(i == 8){
                if(parseInt(i)+parseInt(pointer_save) >= historylist.length ){
                    $("#btn_nextpage").hide();
                    $("#t"+i).hide();
                }
                break;
            }
            //$("#t"+i).removeClass("hide");
            if(parseInt(i)+parseInt(pointer_save) < historylist.length ){
                $("#t"+i).show();
                $("#t"+i+"num").text(parseInt(i)+1+parseInt(pointer_save));    
                $("#t"+i+"recordname").text(historylist[parseInt(i)+parseInt(pointer_save)].record_name); 
                $("#t"+i+"subjectname").text(historylist[parseInt(i)+parseInt(pointer_save)].subject_name); 
                $("#t"+i+"time").text(historylist[parseInt(i)+parseInt(pointer_save)].time);
                if(historylist[parseInt(i)+parseInt(pointer_save)].heartrate > 50){
                    $("#t"+i+"heartrate").text(historylist[parseInt(i)+parseInt(pointer_save)].heartrate.toFixed(2)); 
                }else{
                    $("#t"+i+"heartrate").text("Didn't Measure"); 
                }
                listpointer = parseInt(i)+parseInt(pointer_save); 
            }else{
                $("#btn_nextpage").hide();
                $("#t"+i).hide();
            }
        }
    });
    
    $('#btn_lastpage').on('click', function(e){
        page --;
        $("#btn_nextpage").show();                               
        var pointer_save = listpointer; 
        console.log(pointer_save)
        if(listpointer%8 == 0){
            pointer_save -= 16;
            if(pointer_save < 0){
                pointer_save = 0;
            }
        }
        else{
            pointer_save -= listpointer%8;
            pointer_save -= 8;
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
            $("#t"+i+"recordname").text(historylist[parseInt(i)+parseInt(pointer_save)].record_name); 
            $("#t"+i+"subjectname").text(historylist[parseInt(i)+parseInt(pointer_save)].subject_name); 
            $("#t"+i+"time").text(historylist[parseInt(i)+parseInt(pointer_save)].time);
            if(historylist[parseInt(i)+parseInt(pointer_save)].heartrate > 50){
                $("#t"+i+"heartrate").text(historylist[parseInt(i)+parseInt(pointer_save)].heartrate.toFixed(2)); 
            }else{
                $("#t"+i+"heartrate").text("Didn't Measure"); 
            }
            listpointer = parseInt(i)+parseInt(pointer_save); 
        }
    });
    

    

    getHistorylist();
    //check device alive
    var  heartrate_store = [];
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
                    $("#Heartcol").css("background-color", 'rgba(255,255,255,' + 1 + ')');
                    $('#heartbpm').hide();
                }
                else if(data.heartrate.mode == 'standby'){
                    $('#heartpresent').text('Standby...');
                    $("#Heartcol").css("background-color", 'rgba(255,255,255,' + 1 + ')');
                    $('#heartbpm').hide();
                }
                else if(data.heartrate.mode == 'measuring'){
                    $('#heartpresent').text('Measuring...');
                    heartrate_store = [];
                    $("#Heartcol").css("background-color", 'rgba(255,255,255,' + 1 + ')');
                    $('#heartbpm').hide();
                  }
                else if(data.heartrate.mode == 'done'){
                    $('#heartpresent').text(data.heartrate.heartrate +" bpm");
                    $('#heartbpm').show();
                    heartrate_store.push(data.heartrate.heartrate);
                    if(heartrate_store.length > 25){
                      heartrate_store.splice(0, 1);
                      var temporary = data.heartrate;
                      var total = 0;
                      for(var i in heartrate_store){
                        total += parseInt(heartrate_store[i]);
                        if(Math.abs(temporary - heartrate_store[i]) >= 5){
                          break;
                        }
                        if(i == heartrate_store.length - 1){
                          $("#Heartcol").css("background-color", 'rgba(22,161,22,' + 0.58 + ')');
                        }
                      }
                    }
                }
            });
        }
        });
    };
    check_alive();
    //auto refresh
    setInterval(function () {
        if(is_playing.can_update() == true){
            $.getJSON('/gethistorygraph', is_playing.gettoJson()
            ,function(return_dict){ 
                is_playing.update_graph(return_dict);
            });
        }
        check_alive();
    }, 500);
  })()
  
  
  
  
  
  
  
  