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

// criar pasta de requests se nao houver
if(!fs.existsSync(path.join(requests_folder)))
    fs.mkdirSync(path.join(requests_folder))

// criar lista de workers
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
        // processar pedido para ser mais facilmente usado por um worker
        process_command(fields,files)
        // tenta mandar pedido para um worker
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
  // enquanto que houver workers tenta distribuir pedidos
  while(available_workers.length > 0){
    // se houver pedidos, distribui para um worker
    if(queue.length > 0){
      id = available_workers.pop()
      request = queue.pop()
      console.log(`Request ${id} delivered to worker`)
      // criar worker
      worker = new Worker('./workers/process_command.js', { workerData: { id, request} })
      workers[id] = worker
      // callback para quando receber mensagem do worker
      worker.on('message', worker_callback)
      // iniciar worker
      worker.postMessage('start')
    }else{
      break
    }
  }
}

/**
 * Callback de quando recebe mensagem de termino do worker
 * @param {*} data 
 */
function worker_callback(data) {
  id = data.id
  request_id = data.request_id
  message = data.message
  // trocar request de pending para completed
  completed_requests[request_id] = pending_requests[request_id]
  delete pending_requests[request_id]
  console.log('Worker message:' + message)
  // remover worker
  workers[id].removeListener('message',worker_callback)
  workers[id].unref()
  workers[id] = null
  // adicionar um slot de worker disponivel
  available_workers.push(id)
  // tenta distribuir nova request
  send_request()
}



/**
 * Processa o comando, verificando inputs e outputs
 * criando a pasta para o pedido e os ficheiros se necessario
 * @param {*} data dados do comando (comando,inputs,outputs) 
 */
function process_command(data,files){
  r_folder = path.join(requests_folder,request_n.toString())
  // cria pasta para request se nao houver
  if(!fs.existsSync(r_folder))
    fs.mkdirSync(r_folder)
  inputs = {}
  input_re = /INPUT\d+/g
  // pega inputs do form
  for(d in data){
    if(d.match(input_re)){
      value = data[d]
      if(value.split(' ').length > 1){ // tornar string se tiver espacos
        value = `"${value}"`
      }
      inputs[d] = value
    }
  }
  // pega inputs (tipo ficheiro) do post
  for(file in files){
    oldpath = files[file][0].path
    filename_original = files[file][0]['originalname']
    newpath = `requests/${request_n}/${filename_original}`
    fs.renameSync(oldpath,newpath)
    inputs[file] = filename_original
  }
  command = data.command
  // troca o valor dos inputs no comando
  for(input in inputs){
    command = command.replace(input,inputs[input])
  }
  // adicionar request na queue de requests e dicionario de pending requests
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

