const { parentPort, workerData } = require('worker_threads')
const  child  = require('child_process')
const { id,request } = workerData


parentPort.on('message', (msg) => {
    if (msg === 'start') {
        run_command()
        message = 'Work Done'
        request_id = request.id
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
    full_command = command.split(' ').filter(word => word.length > 0)
    console.log('Running command: ' + full_command)
    console.log(full_command)
    // TODO: modificar dependendo do sistema operativo
    c = child.spawnSync("wsl", full_command, {
    cwd: process.cwd() + `\\${request_path}`
    })
    console.log(c.stdout.toString());
    console.log(c.stderr.toString());
    console.log('Worker ' + id + 'done' )
  }