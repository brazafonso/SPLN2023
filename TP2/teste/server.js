const express = require('express');
const multer = require('multer');
const engines = require('consolidate');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');
const socketio = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketio(server);
const upload = multer({ dest: 'uploads/' });

app.use(express.static(path.join(__dirname, 'public')));
app.set('views', __dirname + '/views');
app.engine('html', engines.mustache);
app.set('view engine', 'html');



app.get('/', (req, res) => {
  res.render('index.html');
});

app.post('/executar-comando', upload.single('arquivo'), (req, res) => {
  const comando = req.body.comando;
  const arquivo = req.file;
  const nomeArquivoSaida = req.body.nomeArquivoSaida;

  if (!comando) {
    return res.status(400).json({ erro: 'Comando não especificado' });
  }

  if (!arquivo) {
    return res.status(400).json({ erro: 'Arquivo não enviado' });
  }

  //const caminhoArquivo = path.join('uploads', arquivo.filename);
  const caminhoArquivo = 'uploads\\' + arquivo.filename;
  //const caminhoArquivoSaida = path.join('uploads', nomeArquivoSaida);
  const caminhoArquivoSaida = 'uploads\\' + nomeArquivoSaida;

  const comandoCompleto = `${comando} ${caminhoArquivo} > ${caminhoArquivoSaida}`;
  console.log('Comando a ser executado:', comandoCompleto);

  // Emitir evento para o cliente informando o status do processamento
  io.emit('status', 'Processando comando...');

  exec(comandoCompleto, (error, stdout, stderr) => {
    if (error) {
      console.error(`Erro ao executar o comando: ${error}`);
      res.json({ resultado: `Erro ao executar o comando: ${error}` });
      return;
    }
    console.log(`Resultado: ${stdout}`);
    console.error(`Erros: ${stderr}`);

    if (fs.existsSync(caminhoArquivoSaida)) {
      console.log(`Arquivo existe! em ${caminhoArquivoSaida}`)
      res.setHeader('Content-Disposition', `attachment; filename="${nomeArquivoSaida}"`);
      res.setHeader('Content-Type', 'application/octet-stream');

      const fileStream = fs.createReadStream(caminhoArquivoSaida);
      fileStream.pipe(res);

      fileStream.on('end', () => {
        fs.unlinkSync(caminhoArquivoSaida);
      });
    } else {
      console.error('Arquivo de saída não encontrado');
      res.json({ resultado: 'Arquivo de saída não encontrado' });
    }
  });
});

// Lidar com conexões dos clientes
io.on('connection', (socket) => {
  console.log('Novo cliente conectado');

  // Enviar mensagem de boas-vindas ao cliente
  socket.emit('status', 'Conexão estabelecida');

  // Lidar com desconexões dos clientes
  socket.on('disconnect', () => {
    console.log('Cliente desconectado');
  });
});

server.listen(3000, () => {
  console.log('Servidor em execução na porta 3000');
});
