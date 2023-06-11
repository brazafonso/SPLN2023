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

function datesEqual(a, b) {
  return a.getTime() === b.getTime();
}

/**
 * Funcao para correr um comando
 */
function run_command(){
  request_path = request.path
  command = request.command
  console.log('LOG: Worker ' + id +' with request '+request.number + 'running command: ' + command)
  try{
    // executar comando
    out = execSync(command,{
      cwd: request_path
    })
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

  //verifico se os ficheiros de inputs foram alterados, caso não são eliminados
  files_times = request.files_times
  for(filepath in files_times){
    old_mtime = files_times[filepath]
    stats = fs.statSync(filepath)
    new_mtime = stats.mtime

    if(datesEqual(old_mtime,new_mtime)){
      fs.unlinkSync(filepath) //elimino o input
    }
  }

  console.log('LOG: Worker ' + id + ' done' )
}
  