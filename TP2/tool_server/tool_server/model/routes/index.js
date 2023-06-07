var express = require('express');
var router = express.Router();
var threads = 1 //TODO: modificar
const { Worker } = require('worker_threads')
const worker = new Worker('./workers/request_listener.js', { workerData: { threads } })
// worker.on('error', (err) => { throw err })
worker.on('message', worker_message_callback)

var completed_requests = {}
var pending_requests = {}

// pedir update do estado
setInterval(function(){
  worker.postMessage({
    msg:"status"
  });
},1000);

// Callback de receber mensagem de worker
function worker_message_callback (data) {
  if(data.msg == 'status'){
    completed_requests = data.completed_requests
    pending_requests = data.pending_requests
  }
}

// Envia comando para o worker processar
function process_command(req){
  command = req.body.command
  worker.postMessage({
    msg: 'command',
    data: req.body,
    files: req.files
  })
}

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

router.get('/requests', function(req, res, next) {
  res.render('requests', { queue: pending_requests });
});

module.exports = router;
