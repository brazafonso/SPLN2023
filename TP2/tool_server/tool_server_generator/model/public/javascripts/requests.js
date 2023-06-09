completed_table = document.getElementById("completed_table")
i = 1 
while(i < completed_table.rows.length){
    id = completed_table.rows[i].id
    document.getElementById(`get_out_${id}`).addEventListener('submit', function(event) {
        event.preventDefault();

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