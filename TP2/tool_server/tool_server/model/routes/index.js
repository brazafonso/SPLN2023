var express = require('express');
var router = express.Router();
var threads = 1
const { Worker } = require('worker_threads')
const worker = new Worker('./workers/command_process.js', { workerData: { threads } })
// worker.on('error', (err) => { throw err })
worker.on('message', worker_message_callback)

// Callback de receber mensagem de worker
function worker_message_callback (data) {
  queue_place = data.queue_place
  console.log('Spot in queue: ' + queue_place)
}

// Envia comando para o worker processar
function process_command(req){
  command = req.body.command
  worker.postMessage({
    msg: 'command',
    data: req.body
  })
}

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

module.exports = router;
