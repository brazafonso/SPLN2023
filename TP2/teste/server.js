const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const path = require('path');

const { exec } = require('child_process');


app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Rota para exibir a página
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Rota para receber o comando do cliente
app.post('/executar-comando', (req, res) => {
  const comando = req.body.comando;

  // Executa o comando no servidor
  exec(comando, (error, stdout, stderr) => {
    if (error) {
      console.error(`Erro ao executar o comando: ${error}`);
      res.json({ resultado: `Erro ao executar o comando: ${error}` });
      return;
    }
    console.log(`Resultado: ${stdout}`);
    console.error(`Erros: ${stderr}`);

    // Retorna o resultado para o cliente
    res.json({ resultado: stdout });
  });
});

// Inicia o servidor na porta 3000
app.listen(3000, () => {
  console.log('Servidor iniciado na porta 3000');
});