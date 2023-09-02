document.addEventListener("DOMContentLoaded", function() {

    // Função para fazer filtro
    const searchProject = document.getElementById('searchProject');
    const resetSearch = document.getElementById('resetSearch');
    const cards = document.querySelectorAll('.card');

    searchProject.addEventListener('keyup', function() {
      const filter = this.value.toUpperCase();

      // Verificar se há pelo menos 3 caracteres digitados
      if (filter.length < 3) {
        return;
      }

      for (const card of cards) {
        const projectName = card.querySelector('.btn-link').textContent.toUpperCase();
        if (projectName.includes(filter)) {
          card.style.display = "";
        } else {
          card.style.display = "none";
        }
      }
    });

    // Função para resetar a busca
    resetSearch.addEventListener('click', function() {
      searchProject.value = "";
      for (const card of cards) {
        card.style.display = "";
      }
    });

    // Função para habilitar o botão de adicionar projeto no modal
    const newProjectNameModal = document.getElementById('newProjectNameModal');
    const addProjectBtn = document.getElementById('addProjectBtn');
    console.log("addProjectBtn", addProjectBtn);

    newProjectNameModal.addEventListener('keyup', function() {
      const projectName = this.value.trim();
      console.log("projectName", projectName, projectName.length < 3);
      addProjectBtn.disabled = projectName.length < 3;
    });

    // Atica botão incluir tarefas
    const addTaskBtns = document.querySelectorAll(".addTaskBtn");

    addTaskBtns.forEach((btn) => {
        const id = btn.id.replace("addTaskBtn", "");
        const newTaskNameInput = document.getElementById(`newTaskName${id}`);

        newTaskNameInput.addEventListener("input", function() {
            if (newTaskNameInput.value.length > 1) {
                btn.disabled = false;
            } else {
                btn.disabled = true;
            }
        });
    });

    // Abre modal para excluir projetos ou tarefas
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        $(modal).on('show.bs.modal', function(event) {
            const modalId = this.id;
            const button = event.relatedTarget;
            const type = button.getAttribute('data-type');
            const id = button.getAttribute('data-id');
            const projetoId = button.getAttribute('data-projeto-id');
            const targetId = (type === 'projeto') ? id : projetoId;
            const deleteModalBody = document.getElementById(`deleteModalBody${targetId}`);
            const deleteForm = document.getElementById(`deleteForm${targetId}`);

            if (deleteModalBody) {
                if (type === 'projeto') {
                    deleteModalBody.textContent = 'Tem certeza de que deseja excluir este projeto?';
                    deleteForm.action = `/excluir_projeto/${id}`;
                } else {
                    deleteModalBody.textContent = 'Tem certeza de que deseja excluir esta tarefa?';
                    deleteForm.action = `/excluir_tarefa/${projetoId}/${id}`;
                }
            }
        });
    });

    //Salva a checagem das tarefas
    let projectCards = document.querySelectorAll('.card');

    projectCards.forEach(card => {
        let customSwitchDivs = card.querySelectorAll('.custom-switch'); // seleciona divs que contêm os switches

        customSwitchDivs.forEach(customSwitch => {
            let checkbox = customSwitch.querySelector('input[type="checkbox"]'); // seleciona o input dentro da div
            checkbox.addEventListener('change', function() {
                let id_projeto = this.getAttribute('data-projeto-id');
                let id_tarefa = this.getAttribute('data-tarefa-id');
                let feito = this.checked;

                // Altera as classes do item da lista
                let listItem = this.closest('li');
                if (feito) {
                    listItem.classList.remove('unchecked-item');
                    listItem.classList.add('checked-item');
                } else {
                    listItem.classList.remove('checked-item');
                    listItem.classList.add('unchecked-item');
                }

                console.log('Tarefa', id_projeto, id_tarefa);

                fetch(`/update_tarefa/${id_projeto}/${id_tarefa}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({feito: feito})
                }).then(response => response.json())
                  .then(data => {
                      console.log(data);
                  });
            });
        });
    });
});
