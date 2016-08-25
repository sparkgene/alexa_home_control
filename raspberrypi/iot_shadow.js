var awsIot = require('aws-iot-device-sdk');
var exec = require('child_process').exec;

var shadowName = "alexa_home"
var thingShadows = awsIot.thingShadow({
   keyPath: "/opt/alexa_home_control/raspberrypi/certs/private.pem.key",
  certPath: "/opt/alexa_home_control/raspberrypi/certs/certificate.pem.crt",
    caPath: "/opt/alexa_home_control/raspberrypi/certs/ca.pem",
  clientId: "alexa_home",
    region: "ap-northeast-1"
});

var clientTokenGet, clientTokenUpdate, command_counter=0, requested_command;

var control_home_device = function(command, counter){
  console.log("counter:" + counter);
  if(command_counter == 0 || command_counter == counter){
    // reset local command counter
    command_counter = counter;
    return;
  }

  // execute command
  if(command !== undefined){
    requested_command = command;
  }
  console.log("execute:" + requested_command);
  exec("irsend SEND_ONCE living_light " + requested_command, function(err, stdout, stderr){
    if (err) {
      console.log(err);
      return;
    }
    console.log(stdout);
    // update shadow
    clientTokenUpdate = thingShadows.update(shadowName, {
      "state":{
        "reported": {
          "counter": counter,
          "command": command,
        }
      }
    });
  });
}

thingShadows.on('connect', function() {
    console.log('connected');
    thingShadows.register( shadowName );
    console.log('registered');
    setTimeout( function() {
       clientTokenGet = thingShadows.get(shadowName);
    }, 1000 );
});

thingShadows.on('status', function(thingName, stat, clientToken, stateObject) {
    console.log('received ' + stat + ' on ' + thingName + ': ' + JSON.stringify(stateObject));
    if( stat == "accepted" ){
      if( clientTokenGet == clientToken ){
        if(requested_command === undefined){
          requested_command = stateObject.state.desired.command;
        }
        // result of get event
        control_home_device(stateObject.state.desired.command, stateObject.state.desired.counter);
      }
      else if( clientTokenUpdate == clientToken){
        // result of update event
        console.log("update accepted");
      }
    }
});

thingShadows.on('delta', function(thingName, stateObject) {
    console.log('received delta on ' + thingName + ': ' + JSON.stringify(stateObject));
    control_home_device(stateObject.state.command, stateObject.state.counter);
});

thingShadows.on('timeout', function(thingName, clientToken) {
     console.log('received timeout on ' + operation + ': ' + clientToken);
});

process.on('SIGINT', function() {
  process.exit();
});
