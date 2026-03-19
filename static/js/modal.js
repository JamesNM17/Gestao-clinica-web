function mostrarModal(card) {

    function set(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value || "—";
    }

    // Básico
    set("nomePaciente", card.dataset.nome);
    set("idPaciente", card.dataset.id);
    set("nascPaciente", card.dataset.nascimento);
    set("sexoPaciente", card.dataset.sexo);
    set("contatoPaciente", card.dataset.contato);

    // Recepção
    set("planoPaciente", card.dataset.plano);
    set("atendimentoPaciente", card.dataset.atendimento);
    set("chegadaPaciente", card.dataset.chegada);

    // Triagem
    set("urgencia_triagemPaciente", card.dataset.urgencia_triagem);
    set("queixaPaciente", card.dataset.queixa);
    set("pressao_arterialPaciente", card.dataset.pressao_arterial);
    set("saturacaoPaciente", card.dataset.saturacao);

    // Médico
    set("diagnosticoPaciente", card.dataset.diagnostico);
    set("prescricaoPaciente", card.dataset.prescricao);

    const overlay = document.getElementById("modalOverlay");
    const modal = document.getElementById("modalPaciente");

    overlay.style.display = "block";
    modal.style.display = "block";

    setTimeout(() => {
        modal.classList.add("modal-open");
    }, 10);
}

function fecharModal() {
    const overlay = document.getElementById("modalOverlay");
    const modal = document.getElementById("modalPaciente");

    modal.classList.remove("modal-open");

    setTimeout(() => {
        modal.style.display = "none";
        overlay.style.display = "none";
    }, 200);
}