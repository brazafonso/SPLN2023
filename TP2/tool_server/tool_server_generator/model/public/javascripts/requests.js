// tabela de pedidos completos
completed_table = document.getElementById("completed_table")
i = 1 
// cada linha de pedido completo
while(i < completed_table.rows.length){
    id = completed_table.rows[i].id
    // listener para o botao de get do pedido
    document.getElementById(`get_out_${id}`).addEventListener('submit', function(event) {
        event.preventDefault();
        // get id de pedido atraves do id do elemento
        splits = event.currentTarget.id.split('_')
        id = splits[splits.length - 1]
        // pedir ao servidor resultado do out
        fetch('/requests/out/'+id, {
            method: 'GET'
        })
        .then(response => {
            if (response.ok) {
                response.json().then(
                    data =>{
                        // Mostar out
                        modal = document.getElementById("w3-modal").style.display='block'
                        modal_text = document.getElementById("w3-modal-text");
                        modal_text.textContent = data.mensagem;
                    }
                )
                
            } else {
            console.error('Erro:', response.statusText);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    });
    i+= 1
}