function mostrarModal(card) {

    function set(id, value) {
        let el = document.getElementById(id);
        if (el) el.textContent = value || "—";
    }

    // Dados básicos
    set("nomePaciente", card.dataset.nome);
    set("idPaciente", card.dataset.id);
    set("nascPaciente", card.dataset.nascimento);
    set("sexoPaciente", card.dataset.sexo);
    set("contatoPaciente", card.dataset.contato);
    set("docPaciente", card.dataset.documento);

    // Recepção
    set("planoPaciente", card.dataset.plano);
    set("atendimentoPaciente", card.dataset.atendimento);
    set("chegadaPaciente", card.dataset.chegada);
    set("observacoes_recepcaoPaciente", card.dataset.observacoes_recepcao);
    set("urgencia_recepcaoPaciente", card.dataset.urgencia_recepcao);
    set("responsavel_recepcaoPaciente", card.dataset.responsavel_recepcao);

    // Triagem
    set("ocupacaoPaciente", card.dataset.ocupacao);
    set("urgencia_triagemPaciente", card.dataset.urgencia_triagem);
    set("tempPaciente", card.dataset.temperatura);
    set("fcPaciente", card.dataset.fc);
    set("frPaciente", card.dataset.fr);
    set("pesoPaciente", card.dataset.peso);
    set("alturaPaciente", card.dataset.altura);
    set("queixaPaciente", card.dataset.queixa);
    set("doencasPaciente", card.dataset.doencas);
    set("horarioTriagemPaciente", card.dataset.horario_triagem);
    set("finalizado_triagemPaciente", card.dataset.finalizado_triagem);
    set("responsavel_triagemPaciente", card.dataset.responsavel_triagem);
    set("observacoes_triagemPaciente", card.dataset.observacoes_triagem);
    set("pressao_arterialPaciente", card.dataset.pressao_arterial);
    set("saturacaoPaciente", card.dataset.saturacao);
    set("alergiaPaciente", card.dataset.alergia);
    set("tabagistaPaciente", card.dataset.tabagista);
    set("bebida_alcoolicaPaciente", card.dataset.bebida_alcoolica);
    set("cirugiaPaciente", card.dataset.cirugia);
    set("escala_dorPaciente", card.dataset.escala_dor);
    set("toma_medicacaoPaciente", card.dataset.toma_medicacao);

    // Médico
    set("diagnosticoPaciente", card.dataset.diagnostico);
    set("prescricaoPaciente", card.dataset.prescricao);
    set("feedbackPaciente", card.dataset.feedback);
    set("finalizado_medicoPaciente", card.dataset.finalizado_medico);
    set("responsavel_medicoPaciente", card.dataset.responsavel_medico);
    set("observacoes_medicoPaciente", card.dataset.observacoes_medico);
    set("horario_finalizacaoPaciente", card.dataset.horario_finalizacao);

    // Exibir modal
    document.getElementById("modalOverlay").style.display = "block";
    const modal = document.getElementById("modalPaciente");
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