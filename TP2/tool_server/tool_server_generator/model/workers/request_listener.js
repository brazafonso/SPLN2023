const { parentPort, workerData } = require('worker_threads')
const fs = require('fs')
const path = require('path');
const requests_folder = 'requests/'
const requests_folder_path = path.join(requests_folder)
const { threads } = workerData
const { Worker } = require('worker_threads');

var queue = [] // queue de pedidos
request_n = 0  // id do proximo pedido
available_workers = [] // lista com threads disponiveis
workers = {}  // dicionario dos workers ativos (serve para os poder terminar quando necessario)
completed_requests = {} // dicionario de todas as requests completas
pending_requests = {} // dicionario de todas as requests pending

// criar pasta de requests se nao houver
if(!fs.existsSync(requests_folder_path))
    fs.mkdirSync(requests_folder_path)
// verificar pedidos ja completos na pasta
else{
  requests_folders= fs.readdirSync(requests_folder)
  // pastas dentro de 'requests'
  for(r_f in requests_folders){
    r_f = requests_folders[r_f]
    try{
      id = parseInt(r_f)
      // ficheiro com nome numerico
      if(!isNaN(id)){
        request_path = path.join(requests_folder,r_f)
        request = request_path
        // ficheiro é uma pasta
        if(fs.lstatSync(request_path).isDirectory()){
          request_files = fs.readdirSync(request_path)
          // para cada pasta dentro da request
          for(file in request_files){
            file = request_files[file]
            re = new RegExp(`request_${id}_(\\d+)_info\.json`,"g")
            // procura por um ficheiro que tenha a nomenculatura do info de request
            if(re.exec(file)){
              info_json = fs.readFileSync(path.join(request_path,file))
              completed_requests[id] = JSON.parse(info_json)
              if(id >= request_n)
                request_n = id + 1
              break
            }
          }
        }
      }
    }
    catch(err){
      console.log('Erro : ' + err)
    }
  }
}



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
        console.log(`LOG: 
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
  console.log('LOG: Sending request')
  // enquanto que houver workers tenta distribuir pedidos
  while(available_workers.length > 0){
    // se houver pedidos, distribui para um worker
    if(queue.length > 0){
      id = available_workers.pop()
      request = queue.pop()
      pending_requests[request.number]['status'] = 'Processing'
      console.log(`LOG: Request ${request.number} delivered to worker ${id}`)
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
  completed_requests[request_id]['status'] = 'Completed'
  delete pending_requests[request_id]
  console.log('LOG: Worker message:' + message)
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
  files_times = {}
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

    stats = fs.statSync(newpath)
    files_times[newpath] = stats.mtime
  }
  command = data.command
  // troca o valor dos inputs no comando
  for(input in inputs){
    command = command.replace(input,inputs[input])
  }
  // adicionar request na queue de requests e dicionario de pending requests
  data = new Date().toISOString().substring(0,19)
  request_info = {
    number : request_n,
    command : command,
    inputs : inputs,
    date : data,
    path : r_folder,
    status : "Pending",
    files_times : files_times
  }

  queue.push(request_info)

  pending_requests[request_n] = request_info

  fs.writeFileSync(path.join(r_folder,`request_${request_n}_${Date.parse(data)}_info.json`),JSON.stringify(request_info))
}

