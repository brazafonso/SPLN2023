const { parentPort, workerData } = require('worker_threads')
const fs = require('fs')
const path = require('path');
const requests_folder = 'requests/'
const { threads } = workerData
const { Worker } = require('worker_threads');
var queue = [] // queue de pedidos
request_n = 0  // id do proximo pedido
available_workers = [] // lista com threads disponiveis
workers = {}  // dicionario dos workers ativos (serve para os poder terminar quando necessario)
completed_requests = {} // dicionario de todas as requests completas
pending_requests = {} // dicionario de todas as requests pending




console.log('Creating worker list')
for(i=0;i<threads;i++){
  available_workers.push(i)
}

parentPort.on('message', (data) => {
    msg = data.msg
    if (msg == 'command'){
        fields = data.data
        command = fields.command
        files = data.files
        console.log(`
        Request Number: ${request_n}
        Command: ${command}
        Files : ${files}
        `)
        process_command(fields,files)
        send_request()
        request_n += 1
        return
    }
    else if (msg == 'status'){
      // apagar pedidos completos apagados
      for(id in completed_requests){
        if(!fs.existsSync(completed_requests[id].path))
          delete completed_requests[id]
      }
      parentPort.postMessage({msg:'status',pending_requests,completed_requests})
      return 
    }
    throw new Error(`Unknown message: ${msg}`)
  })


/**
 * Da uma request a um worker se possivel
 */
function send_request(){
  console.log('Sending request')
  while(available_workers.length > 0){
    console.log('Workers available')
    if(queue.length > 0){
      id = available_workers.pop()
      request = queue.pop()
      worker = new Worker('./workers/process_command.js', { workerData: { id, request} })
      workers[id] = worker
      worker.on('message', worker_callback)
      worker.postMessage('start')
    }else{
      break
    }
  }
  console.log('No workers')
}

/**
 * Callback de quando recebe mensagem de termino do worker
 * @param {*} data 
 */
function worker_callback(data) {
  id = data.id
  request_id = data.request_id
  message = data.message
  completed_requests[request_id] = pending_requests[request_id]
  delete pending_requests[request_id]
  console.log('Worker message:' + message)
  workers[id].removeListener('message',worker_callback)
  workers[id].unref()
  workers[id] = null
  available_workers.push(id)
  send_request()
}



/**
 * Processa o comando, verificando inputs e outputs
 * criando a pasta para o pedido e os ficheiros se necessario
 * @param {*} data dados do comando (comando,inputs,outputs) 
 */
function process_command(data,files){
  r_folder = path.join(requests_folder,request_n.toString())
  if(!fs.existsSync(r_folder))
    fs.mkdirSync(r_folder)
  inputs = {}
  input_re = /INPUT\d+/g
  for(d in data){
    if(d.match(input_re)){
      value = data[d]
      if(value.split(' ').length > 1){ // tornar string se tiver espacos
        value = `"${value}"`
      }
      inputs[d] = value
    }
  }
  for(file in files){
    oldpath = files[file][0].path
    filename_original = files[file][0]['originalname']
    newpath = `requests/${request_n}/${filename_original}`
    fs.renameSync(oldpath,newpath)
    inputs[file] = filename_original
  }
  command = data.command
  for(input in inputs){
    command = command.replace(input,inputs[input])
  }

  data = new Date().toISOString().substring(0,19)
  queue.push({
    id : request_n,
    command : command,
    inputs : inputs,
    date : data,
    path : r_folder
  })

  pending_requests[request_n] = {
    number : request_n,
    command : command,
    date : data,
    path: r_folder
  }
}

