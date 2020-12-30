/* globals Chart:false, feather:false */

(function () {
    'use strict'
  
    feather.replace()
    
    
    class PlayControl{
        constructor(ctx){
            this.ctx = ctx;
            this.count = 0;
            this.past_seconds = -1;
            this.past_timestamp = 0;
            this.start_oid = '';
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
                      min: -2,
                      max: 5
                    }
                  }]
                },
                legend: {
                  display: false
                }
              };
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
        new_chart(return_dict){
            var timelist = return_dict.time;
            this.count = return_dict.count;
            this.start_oid = return_dict.start_oid;
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
            console.log(label);
            console.log(return_dict.value);

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
                    data: return_dict.peak
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
                    this.data.datasets[0].data.splice(0, 70);
                }
            }
            if(return_dict.peak != []){
                this.data.datasets[1].data.push.apply(this.data.datasets[1].data, return_dict.peak); 
                if(this.data.datasets[1].data.length > 500){
                    this.data.datasets[1].data.splice(0, 70);
                }
            }
            
            
            var myLineChart = new Chart(this.ctx , {
                type: "line",
                data: this.data,
                options: this.options 
            });
            
        }
        is_init(){
            if(this.count == 0){
                return true;
            }
            else{
                return false;
            }
        }
        gettoJson(){
            return {count: this.count, start_oid: this.start_oid}
        }
        end(){
            this.count = 0;
            this.start_oid = '';
          
        }
    };

    var is_playing = new PlayControl(document.getElementById("myChart").getContext("2d"));
    
    
   
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
        if(is_playing.is_init() == true){
            $.getJSON('/peakfinder', is_playing.gettoJson(),
            function(data){     
            is_playing.new_chart(data); 
            });
        }else{
            $.getJSON('/peakfinder', is_playing.gettoJson(),
            function(data){    
                is_playing.update_graph(data); 
            });
        }
        check_alive();
    }, 750);
  })()
  
  
  
  
  
  
  
  