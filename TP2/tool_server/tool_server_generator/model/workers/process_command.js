const { parentPort, workerData } = require('worker_threads')
const  {execSync}  = require('child_process')
const { id,request } = workerData
const fs = require('fs')
const path = require('path')

parentPort.on('message', (msg) => {
    if (msg === 'start') {
        run_command()
        message = 'Work Done'
        request_id = request.number
        // avisar parent que terminou de processar a request
        parentPort.postMessage({ id, message,request_id })
        return
    }
    throw new Error(`Unknown message: ${msg}`)
  })

/**
 * Funcao para correr um comando
 */
function run_command(){
  request_path = request.path
  command = request.command
  console.log('Worker ' + id +' with request '+request.number + 'running command: ' + command)
  try{
    // executar comando
    out = execSync(command,{
      cwd: request_path
    })
    console.log(out.toString());
    // Escrever ficheiros com output de terminal na pasta da request
    out_file = path.join(request_path,`request_${request.number}_${Date.parse(request.date)}_stdout.txt`)
    fs.writeFileSync(out_file,out.toString())
  }
  catch(err){
    error = err.stderr.toString()
    console.log('Error:' + err);
    console.log('Stderr:' + error);
    err_file = path.join(request_path,`request_${request.number}_${Date.parse(request.date)}_stderr.txt`)
    fs.writeFileSync(err_file,error)
  }
  console.log('Worker ' + id + ' done' )
}
  