const { parentPort, workerData } = require('worker_threads')


const { threads } = workerData
queue = []
request = 0


parentPort.on('message', (data) => {
    msg = data.msg
    if (msg === 'start') {
      console.log('Worker working')
      return
    }else if (msg == 'command'){
        data = data.data
        command = data.command
        console.log(```
        Request Number: ${request}
        Command: ${command}
        ```)
        request += 1
        return
    }
    throw new Error(`Unknown message: ${msg}`)
  })

/**
 * Processa o comando, verificando inputs e outputs
 * criando a pasta para o pedido e os ficheiros se necessario
 * @param {*} data dados do comando (comando,inputs,outputs) 
 */
function process_command(data){

}