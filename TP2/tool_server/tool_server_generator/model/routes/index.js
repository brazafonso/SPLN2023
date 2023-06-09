var express = require('express');
var fs = require('fs');
var path = require('path');
var AdmZip = require('adm-zip');

var router = express.Router();
var threads = $threads
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

router.get('/', function(req, res, next) {
  res.redirect('/requests');
});

// pagina das requests
router.get('/requests', function(req, res, next) {
  res.render('requests', { title: 'Requests', queue: pending_requests,completed:completed_requests });
});

// rota para enviar o zip com os resultados de um pedido
router.get('/requests/:id', function(req, res, next) {
  id = req.params.id
  request = completed_requests[id]
  var zip = new AdmZip();
  // add local file
  zip.addLocalFolder(`./requests/${id}`);
  // get everything as a buffer
  var zipFileContents = zip.toBuffer();
  const fileName = `request_${id}.zip`;
  const fileType = 'application/zip';
  res.writeHead(200, {
      'Content-Disposition': `attachment; filename="${fileName}"`,
      'Content-Type': fileType,
    })
  res.end(zipFileContents)
});

// Rota para enviar o out de um pedido
router.get('/requests/out/:id', function(req, res, next) {
  id = req.params.id
  request = completed_requests[id]
  text = ''
  // ler out
  stdout_file = path.join(request.path,`request_${id}_${Date.parse(request.date)}_stdout.txt`)
  stderr_file = path.join(request.path,`request_${id}_${Date.parse(request.date)}_stderr.txt`)
  if(fs.existsSync(stdout_file)){
    text = fs.readFileSync(stdout_file).toString()
  }
  // se out vazio, ler err
  else if(fs.existsSync(stderr_file)){
    text = fs.readFileSync(stderr_file).toString()
  }
  res.json({id:id,mensagem:text})
});

router.post('/requests/delete/:id', function(req, res, next) {
  id = req.params.id
  delete completed_requests[id]
  fs.rmSync(path.join(`requests/${id}`), { recursive: true, force: true })
  res.redirect('/requests')
});


module.exports = router;
