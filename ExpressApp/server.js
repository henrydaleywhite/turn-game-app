var express = require('express')
var app = require('express')()
var http = require('http').Server(app)
var io = require('socket.io')(http)
var session = require('express-session');
const bodyParser = require('body-parser');
var request = require('request-promise');


app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({secret: 'secret'}));

app.set('views', './views')
app.set('view engine', 'pug')

const games = [
    { id: 1, name: 'chess' },
    { id: 2, name: 'tic-tac-toe' },
    { id: 3, name: 'pong' }
]

//Render index at root '/'
app.get('/', (req, res)=>{
    res.render('index')
})

var sess;

//get login info from flask side
app.post('/login', async function (req, res) {
    

    const gameList = { game1: { 
                            name: 'Zombie-Dice',
                            img: 'dice.png',
                            pk: '1'
                        },
                        game2: {
                            name: 'Tic-Tac-Toe',
                            img: 'tictactoe.png',
                            pk: '2'
                        }
                    }

    var options = {
        method: 'GET',
        uri: 'http://127.0.0.1:5000/',
        body:req.body,
        json: true 
    };
    //console.log(req.body)

    var returndata;
    var recieverequest = await request(options)
    .then(function (parsedBody) {
        //console.log(parsedBody.user_info); // parsedBody contains the data sent back from the Flask server
        returndata = parsedBody.user_info; // do something with this data, here I'm assigning it to a variable.
    })
    .catch(function (err) {
        console.log(err);
    });
    
    if(returndata) {
        sess = req.session;
        
        sess.display_name = returndata['display_name'];
        sess.email = returndata['email'];
        sess.pk = returndata['pk'];
        sess.username = returndata['username'];

        //console.log("info")
        //console.log(sess.display_name)
        //console.log(sess.email)
        //console.log(sess.pk)
        //console.log(sess.username)
        //console.log(returndata);
        //returndata contains userinfo 
        res.render('select', { gameList: gameList , display_name: returndata['display_name']})

    } else{
        res.render('index',{message:"Try again!"})

    }
   
});

//get registration from flask back
app.post('/register', async function (req, res) {
    var options = {
        method: 'POST',
        uri: 'http://127.0.0.1:5000/registration',
        body:req.body,
        json: true 
    };

    console.log(req.body)

    var returndata;
    var recieverequest = await request(options)
    .then(function (parsedBody) {
        returndata = parsedBody.status; // do something with this data, here I'm assigning it to a variable.
    })
    .catch(function (err) {
        console.log(err);
    });

    if(returndata) {
        //console.log(returndata);
        var userdata = req.body
        res.render('index');

    } else{
        res.send("Try again!!");

    };
});




app.post('/select', async function (req, res) {
    sess= req.session;
    console.log(sess.display_name);
    console.log(sess.pk)
    console.log("Game")
    console.log(req.body)

    var sendata = { "game_pk":req.body.Game,
    "user_info":{
        "display_name": sess.display_name,
        "email":sess.email,
        "pk":sess.pk,
        "username":sess.username }
    };

    console.log(sendata)

    var options = {
        method: 'GET',
        uri: 'http://127.0.0.1:5000/setup',
        body:sendata,
        json: true 
    };

    var options_cont = {
        method: 'GET',
        uri: 'http://127.0.0.1:5000/select_continue',
        body:sendata,
        json: true 
    };

    if(req.body.switch) {
        var returndata;
        var recieverequest = await request(options)
        .then(function (parsedBody) {
            returndata = parsedBody.game_params; // do something with this data, here I'm assigning it to a variable.
        })
        .catch(function (err) {
            console.log(err);
         });
        sess.game_params= returndata;
        console.log(sess.game_params)
        console.log(returndata);

        var playerList = new Array(returndata['maximum_num_players'])
        console.log(playerList)

        res.render('start_new' , { playerList: playerList });
    }
    //TODO fix else statement...
    else {

        var returndata;


        var recieverequest = await request(options_cont)
            .then(function (parsedBody) {
                console.log('CHECKBELOWFOR FLASKRESPOSE')
                returndata = parsedBody;
                console.log(returndata) // do something with this data, here I'm assigning it to a variable.
            })
            .catch(function (err) {
                console.log(err);
             });

        // var returndata;

        // console.log("123")
        // console.log(sendata)
        // var recieverequest = await request(options_cont)
        // .then(function (parsedBody) {
        //     console.log(parsedBody)
        //     returndata = parsedBody; // do something with this data, here I'm assigning it to a variable.
        // })
        // .catch(function (err) {
        //     console.log(err);
        //  });

        // sess.game_params= returndata;
        // console.log("info u need")
        // console.log(sess.game_params)

        // console.log('-------------dw-adwadwada------------')
        // console.log(returndata.save_states);
        // console.log(returndata.room_info);
        
        res.render('continue',{  saveStates: returndata.save_states, roomInfo: returndata.room_info  })};
    // }   {  saveStates: returndata.save_states, roomInfo: returndata.room_info  }



app.post('/continue', async function (req, res) {
    sess= req.session;
    // console.log(sess.display_name);
    // console.log(sess.pk)
    // console.log("Game")
    console.log('HIIHIHIHIHIHIHI')
    console.log(req.body.selectedState)
    console.log('HIIHIHIHIHIHIHI')

    sess.game_id = req.body.selectedState;
    var sendata = { "game_id":sess.game_id,
    "user_info":{
        "display_name": sess.display_name,
        "email":sess.email,
        "pk":sess.pk,
        "username":sess.username }
    };

    console.log(sendata)

    var options = {
        method: 'GET',
        uri: 'http://127.0.0.1:5000/gamepage',
        body:sendata,
        json: true 
    };

    
    var returndata;
    var recieverequest = await request(options)
    .then(function (parsedBody) {
        console.log(parsedBody)
        returndata = parsedBody.html; // do something with this data, here I'm assigning it to a variable.
    })
    .catch(function (err) {
        console.log(err);
     });

    var buff = new Buffer.from(returndata)
    var base64data = buff.toString('base64')
    console.log(base64data)

    //res.send(gameHTML)
  
    //console.log();

    
    res.render('game' , { gameHTML: base64data});


    });


});


app.post('/game_start', async function (req, res) {
    
    console.log(req.body)
    sess= req.session;
    console.log(sess)

    console.log(sess.display_name);
    console.log(sess.pk)
    console.log("Game game_start")
    console.log(sess.game_params['pk'])
 
    var sendata = { 
    "user_info":{
        "display_name": sess.display_name,
        "email":sess.email,
        "pk":sess.pk,
        "username":sess.username },
    "game_params":{ "game_pk":sess.game_params['pk'], "user_list": req.body.playerNames}
    };

    console.log(sendata)

    var options = {
        method: 'POST',
        uri: 'http://127.0.0.1:5000/setup',
        body:sendata,
        json: true 
    };

    var returndata;
    var recieverequest = await request(options)
    .then(function (parsedBody) {
        returndata = parsedBody.game_id; // do something with this data, here I'm assigning it to a variable.
    })
    .catch(function (err) {
        console.log(err);
     });



    sess.game_id= returndata;
    console.log(sess.game_id)
    console.log(returndata);

    
    var sendata1 = { 
    "user_info":{
        "display_name": sess.display_name,
        "email":sess.email,
        "pk":sess.pk,
        "username":sess.username },
    "game_id":sess.game_id
    };

    var options = {
        method: 'GET',
        uri: 'http://127.0.0.1:5000/gamepage',
        body:sendata1,
        json: true 
    };

    var returndata;
    var recieverequest = await request(options)
    .then(function (parsedBody) {
        returndata = parsedBody.html; // do something with this data, here I'm assigning it to a variable.
    })
    .catch(function (err) {
        console.log(err);
     });


    var buff = new Buffer.from(returndata)
    var base64data = buff.toString('base64')
    //console.log(base64data)

    //res.send(gameHTML)
  
    //console.log();
    
    res.render('game' , { gameHTML: base64data});


});


app.post('/gamepage', async function (req, res) {
    console.log('hellloooo')

    sess = req.session;

    //var roomInfo = sess.game_params['room_info']
    //var saveStates = sess.game_params['save_states']
    var gameId = sess.game_id
    var nextState = req.body.next_state

    console.log(sess)
    //console.log(roomInfo)
    //console.log(saveStates)
    //console.log(nextState)
    console.log(gameId)
    console.log(sess.display_name)
    console.log(sess.email)
    console.log(sess.pk)
    console.log(sess.username)

    var sendata = { "game_params": {
                        "game_id": gameId,
                        "next_state": nextState},
                    "user_info": {
                        "display_name": sess.display_name,
                        "email":sess.email,
                        "pk":sess.pk,
                        "username":sess.username }
                }

    // SEND GAME PARAMS AND USER INFO
    // TO FLASK ENDPOINT @ :5000/gamepage
    var optionPost = {
        method: 'POST',
        uri: 'http://127.0.0.1:5000/gamepage',
        body:sendata,
        json: true }

    var recievePost = await request(optionPost)
        .then( function(parsedBody) {
            console.log('8====D')
            console.log(parsedBody)
            console.log('8====D')
        })
        .catch(function (err) {
            console.log(err);
         });

    var sendata1 = { 
        "user_info":{
        "display_name": sess.display_name,
        "email":sess.email,
        "pk":sess.pk,
        "username":sess.username },
        "game_id":sess.game_id
    };

    var optionGet = {
        method: 'GET',
        uri: 'http://127.0.0.1:5000/gamepage',
        body: sendata1,
        json: true 
    };

    var returndata;
    var recieveGet = await request(optionGet)
        .then( function(parsedBody) {
            returndata = parsedBody.html;
            console.log('8====D')
            console.log(parsedBody.html)
            console.log('8====D')
        })
        .catch(function (err) {
            console.log(err);
         });

    var buff = new Buffer.from(returndata)
    var base64data = buff.toString('base64')

    res.render('game',{ gameHTML: base64data})


        // sess= req.session;
        // console.log(sess.display_name);
        // console.log(sess.pk)
        // console.log("Game buttuon")
        // console.log(req.body.next_state)
        // console.log(sess.game_params)
        // var sendata = { "game_params":{"game_id":sess.game_params['room_info'][0]['playthrough_id'], "next_state":req.body.next_state},
        // "user_info":{
        //     "display_name": sess.display_name,
        //     "email":sess.email,
        //     "pk":sess.pk,
        //     "username":sess.username }
        // };

        // console.log(sendata)

        // var options = {
        //     method: 'POST',
        //     uri: 'http://127.0.0.1:5000/gamepage',
        //     body:sendata,
        //     json: true 
        // };

        
        // var returndata;
        // var recieverequest = await request(options)
        // .then(function (parsedBody) {
        //     console.log(parsedBody)
        //     returndata = parsedBody; // do something with this data, here I'm assigning it to a variable.
        // })
        // .catch(function (err) {
        //     console.log(err);
        //  });

        // // var buff = new Buffer.from(returndata)
        // // var base64data = buff.toString('base64')
        // // if (returndata.win === false ) {

        //     // sess.game_id= returndata;
        //     // console.log(sess.game_id)
        //     // console.log(returndata);

        
        //     // var sendata1 = { 
        //     //     "user_info":{
        //     //     "display_name": sess.display_name,
        //     //     "email":sess.email,
        //     //     "pk":sess.pk,
        //     //     "username":sess.username },
        //     //     "game_id":sess.game_id
        //     // };

        //     // var options = {
        //     //     method: 'GET',
        //     //     uri: 'http://127.0.0.1:5000/gamepage',
        //     //     body:sendata1,
        //     //     json: true 
        //     // };

        //     // var returndata;
        //     // var recieverequest = await request(options)
        //     // .then(function (parsedBody) {
        //     //     returndata = parsedBody.html; // do something with this data, here I'm assigning it to a variable.
        //     // })
        //     // .catch(function (err) {
        //     //     console.log(err);
        //     // });


        // var buff = new Buffer.from(returndata)
        // var base64data = buff.toString('base64')
        // //console.log(base64data)

        // //res.send(gameHTML)
      
        // //console.log();


        // res.render('game' , { gameHTML: base64data});
    // }
    // else{
    //     res.send('U win')
    // }
   

    
    //res.render('game' , { gameHTML: base64data});


    });


app.post('/', (req, res)=>{
    var usernameLogin = req.body.usernameLogin
    var passwordLogin = req.body.passwordLogin
    var usernameRegister = req.body.usernameRegister
    var passwordRegister= req.body.passwordRegister
    var email = req.body.email
    var nickname = req.body.nickname

    console.log(usernameLogin)
    console.log(passwordLogin)
    console.log(usernameRegister)
    console.log(passwordRegister)
    console.log(email)
    console.log(nickname)
})

app.get('/select', (req, res)=>{


    const gameList = { game1: { 
                            name: 'Zombie-Dice',
                            img: 'dice.png',
                            pk: '1'
                        },
                        game2: {
                            name: 'Tic-Tac-Toe',
                            img: 'tictactoe.png',
                            pk: '2'
                        }
                    }

    res.render('select', { gameList: gameList })
})

// app.get('/start-new', (req, res)=>{

//     // User initiates a new room and enters user's to connect

//     const players = ['player1', 'player2', 'player3']
//     res.render('start_new', { playerList: players }); 
// })

// app.get('/continue', (req, res)=>{

//     // Continue games from a saved state

//     const saveStates = ['State1', 'State2', 'State3']

//     const roomInfo = { invite1: {
//                             invitingUser: 'chase', 
//                             gamename: 'tictactoe',
//                             pk: '12' 
//                         },
//                         invite2: {
//                             invitingUser: 'henry', 
//                             gamename: 'zombiedice',
//                             pk: '24'
//                         }
//                     }

//     res.render('continue', { saveStates: saveStates, roomInfo: roomInfo  });
// })

// app.get('/game', (req, res)=>{

//     res.render('game');
// })

// app.post('/start-new', (req, res)=>{
//     var usernames = body.req
//     console.log(usernames)

//     res.render('select', {  title: 'Hey' })

// })

// app.post('/select', (req, res)=>{
//     var toggleValue = req.body.switch
//     var gameName = req.body.game
//     console.log(req.body)

// })

// app.post('/continue', (req, res)=>{
//     var states = req.body
//     console.log(states)
// })


// app.get('/games', (req, res) =>{
//     res.send(games);
// })


//Create Socket for Chat Connection
io.on('connection', (socket)=>{
    socket.on('chat', (msg)=>{
        io.emit('chat', msg)
    })
})

io.on('disconnect', function(){
    console.log('User Disconnected')
})

app.use(express.static('public'))

//PORT
const port = process.env.PORT || 3001;
http.listen(port, ()=>{
    console.log(`listening to port: ${port}`)
})