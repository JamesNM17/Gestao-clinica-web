from flask import Flask, render_template, redirect, url_for, abort, flash, request
from dados1 import db1
from model import (
    Funcionarios, Recepcao, Triagem, Medico,
    AdminRecepcao, AdminTriagem, AdminMedico, AdminFuncionarios
)
from forms import FuncionarioForm, RecepcaoForm, TriagemForm, MedicoForm, LoginForm
from flask_admin import Admin
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# -----------------------
# CONFIGURAÇÃO DO APP
# -----------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] = 'trocarDepoisPeloAmorDeDeus'

db1.init_app(app)
with app.app_context():
    db1.create_all()

# -----------------------
# LOGIN MANAGER
# -----------------------
lg = LoginManager()
lg.init_app(app)
lg.login_view = "login"

@lg.user_loader
def load_user(user_id):
    try:
        return db1.session.get(Funcionarios, int(user_id))
    except Exception:
        return None

# -----------------------
# FLASK-ADMIN
# -----------------------
admin = Admin(app, name="Painel Clínico")
admin.add_view(AdminRecepcao(Recepcao, db1.session, name="Recepção"))
admin.add_view(AdminTriagem(Triagem, db1.session, name="Triagem"))
admin.add_view(AdminMedico(Medico, db1.session, name="Médico"))
admin.add_view(AdminFuncionarios(Funcionarios, db1.session, name="Funcionários"))

# -----------------------
# HELPERS DE PERMISSÃO
# -----------------------
def check_role(*roles):
    func = (current_user.funcao or "").strip().lower()
    return func in [r.lower() for r in roles]

def require_role(*roles):
    if not check_role(*roles):
        abort(403)

# -----------------------
# ROTAS DE LOGIN
# -----------------------
@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Funcionarios.query.filter_by(usuario=form.usuario.data).first()
        if user and user.senha == form.senha.data:
            login_user(user)
            func = (user.funcao or "").strip().lower()
            if func == "administrador":
                return redirect(url_for("admin_dashboard"))
            elif func == "recepcionista":
                return redirect(url_for("recepcao_list"))
            elif func in ["médico", "medico"]:
                return redirect(url_for("dashboard_medico"))
            elif func == "enfermeiro":
                return redirect(url_for("triagem"))
            else:
                return redirect(url_for("login"))
        flash("Usuário ou senha incorretos", "danger")
    return render_template("login.html", form=form)

@app.route("/sair")
@login_required
def sair():
    logout_user()
    return redirect(url_for("login"))

# -----------------------
# DASHBOARDS
# -----------------------
@app.route("/dash_pacientes")
@login_required
def dash_pacientes():
    require_role("recepcionista", "administrador")
    pacientes = Recepcao.query.order_by(Recepcao.horario_chegada.desc()).all()
    return render_template("dash_pacientes.html", dados=pacientes)

@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    require_role("administrador")
    dados = Funcionarios.query.all()
    return render_template("dash_admin.html", dados=dados)

@app.route("/dashboard_medico")
@login_required
def dashboard_medico():
    require_role("medico", "administrador")
    
    pacientes_aguardando = (
        Recepcao.query
        .join(Triagem)
        .filter(Triagem.finalizado_triagem == True)
        .outerjoin(Medico)
        .filter((Medico.finalizado_medico == False) | (Medico.id == None))
        .order_by(Triagem.horario_de_triagem.asc())
        .all()
    )

    ultimos_atendimentos = (
        Medico.query
        .filter(Medico.finalizado_medico == True)
        .order_by(Medico.horario_de_finalizacao.desc())
        .limit(5)
        .all()
    )

    atendimentos_hoje = Medico.query.filter(
        Medico.horario_de_finalizacao >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()

    return render_template(
        "dash_medico.html",
        pacientes_aguardando=pacientes_aguardando,
        ultimos_atendimentos=ultimos_atendimentos,
        atendimentos_hoje=atendimentos_hoje
    )

# -----------------------
# ATENDER PACIENTE (ÚNICA FUNÇÃO)
# -----------------------
@app.route('/atender_paciente/<string:paciente_id>', methods=['GET', 'POST'])
@login_required
def atender_paciente(paciente_id):
    require_role("medico", "administrador")
    
    # Busca o paciente pelo ID
    paciente = Recepcao.query.get_or_404(paciente_id)
    
    # Cria formulário e pré-preenche se já houver atendimento
    form = MedicoForm()
    form.preencher_form(paciente)

    if form.validate_on_submit():
        # Se ainda não existe atendimento médico
        if not paciente.medico:
            novo = Medico(
                recepcao_id=paciente.id,
                feedback=form.feedback.data or '',
                diagnostico=form.diagnostico.data or '',
                prescricao=form.prescricao.data or '',
                finalizado_medico=True,
                responsavel_medico=current_user.nome_completo,
                observacoes_medico=form.observacoes_medico.data or '',
                horario_de_finalizacao=datetime.utcnow()
            )
            db1.session.add(novo)
        else:
            # Atualiza atendimento existente
            m = paciente.medico
            m.feedback = form.feedback.data or ''
            m.diagnostico = form.diagnostico.data or ''
            m.prescricao = form.prescricao.data or ''
            m.finalizado_medico = True
            m.responsavel_medico = current_user.nome_completo
            m.observacoes_medico = form.observacoes_medico.data or ''
            m.horario_de_finalizacao = datetime.utcnow()
        
        db1.session.commit()
        flash(f"Atendimento do paciente {paciente.nome_completo} finalizado com sucesso!", "success")
        return redirect(url_for('dashboard_medico'))

    return render_template("medico/form.html", form=form, paciente=paciente, action="Finalizar")

# -----------------------
# PAINEL DE CHAMADA DE SENHA
# -----------------------
@app.route("/painel_senha")
@login_required
def painel_senha():
    require_role("administrador", "recepcionista")
    
    # Lista pacientes chamados, mas ainda não atendidos
    pacientes = Recepcao.query.filter(Recepcao.chamado == True).order_by(Recepcao.horario_chegada.asc()).all()
    
    return render_template("painel_senha.html", pacientes=pacientes)

# -----------------------
# FUNCIONÁRIOS
# -----------------------
@app.route("/funcionarios")
@login_required
def funcionarios_list():
    require_role("administrador")
    dados = Funcionarios.query.all()
    return render_template("funcionarios/list.html", dados=dados)

@app.route("/funcionario/novo", methods=["GET", "POST"])
@login_required
def funcionario_novo():
    require_role("administrador")
    form = FuncionarioForm()
    if form.validate_on_submit():
        novo_func = Funcionarios(
            nome_completo=form.nome_completo.data,
            usuario=form.usuario.data,
            funcao=form.funcao.data,
            sexo=form.sexo.data,
            senha=form.senha.data
        )
        db1.session.add(novo_func)
        db1.session.commit()
        flash(f"Funcionário {novo_func.nome_completo} criado com sucesso!", "success")
        return redirect(url_for("funcionarios_list"))
    return render_template("funcionarios/form.html", form=form, action="Novo")

@app.route("/funcionario/editar/<int:id>", methods=["GET", "POST"])
@login_required
def funcionarios_editar(id):
    require_role("administrador")
    func = Funcionarios.query.get_or_404(id)
    form = FuncionarioForm(obj=func)
    if form.validate_on_submit():
        func.nome_completo = form.nome_completo.data
        func.usuario = form.usuario.data
        func.funcao = form.funcao.data
        func.sexo = form.sexo.data
        func.senha = form.senha.data
        db1.session.commit()
        flash(f"Funcionário {func.nome_completo} atualizado com sucesso!", "success")
        return redirect(url_for("funcionarios_list"))
    return render_template("funcionarios/form.html", form=form, action="Editar")

@app.route("/funcionario/excluir/<int:id>", methods=["POST"])
@login_required
def funcionarios_excluir(id):
    require_role("administrador")
    func = Funcionarios.query.get_or_404(id)
    db1.session.delete(func)
    db1.session.commit()
    flash(f"Funcionário {func.nome_completo} excluído com sucesso!", "warning")
    return redirect(url_for("funcionarios_list"))

# -----------------------
# RECEPÇÃO
# -----------------------
@app.route("/recepcao")
@login_required
def recepcao_list():
    require_role("recepcionista", "administrador")
    dados = Recepcao.query.order_by(Recepcao.horario_chegada.desc()).all()
    return render_template("dash_recepcao.html", dados=dados)

@app.route("/recepcao/novo", methods=["GET","POST"])
@login_required
def recepcao_novo():
    require_role("recepcionista", "administrador")
    form = RecepcaoForm()
    if form.validate_on_submit():
        r = Recepcao(
            nome_completo=form.nome_completo.data,
            data_nascimento=form.data_nascimento.data,
            sexo=form.sexo.data,
            contato=form.contato.data,
            cpf=form.cpf.data,
            atendimento=form.atendimento.data,
            plano=form.plano.data,
            observacoes_recepcao=form.observacoes_recepcao.data,
            urgencia_recepcao=form.urgencia_recepcao.data,
            responsavel_recepcao=current_user.nome_completo,
        )
        db1.session.add(r)
        db1.session.commit()
        flash("Paciente registrado com sucesso!", "success")
        return redirect(url_for("recepcao_list"))
    return render_template("recepcao/form.html", form=form, action="Novo")

@app.route("/recepcao/editar/<id>", methods=["GET","POST"])
@login_required
def recepcao_editar(id):
    require_role("recepcionista","administrador")
    item = Recepcao.query.get_or_404(id)
    form = RecepcaoForm(obj=item)
    if form.validate_on_submit():
        item.nome_completo = form.nome_completo.data
        item.data_nascimento = form.data_nascimento.data
        item.sexo = form.sexo.data
        item.contato = form.contato.data
        item.cpf = form.cpf.data
        item.atendimento = form.atendimento.data
        item.plano = form.plano.data
        item.observacoes_recepcao = form.observacoes_recepcao.data
        item.urgencia_recepcao = form.urgencia_recepcao.data
        responsavel_recepcao = current_user.nome_completo,
        db1.session.commit()
        flash("Registro atualizado!", "success")
        return redirect(url_for("recepcao_list"))
    return render_template("recepcao/form.html", form=form, action="Editar")

@app.route("/recepcao/excluir/<id>", methods=["POST"])
@login_required
def recepcao_excluir(id):
    require_role("recepcionista","administrador")
    item = Recepcao.query.get_or_404(id)
    db1.session.delete(item)
    db1.session.commit()
    flash("Registro excluído.", "warning")
    return redirect(url_for("recepcao_list"))

# -----------------------
# TRIAGEM
# -----------------------
@app.route("/triagem")
@login_required
def triagem():
    require_role("enfermeiro", "administrador")
    pacientes = (
        Recepcao.query
        .outerjoin(Triagem)
        .filter((Triagem.id == None) | (Triagem.finalizado_triagem == False))
        .order_by(Recepcao.horario_chegada.asc())
        .all()
    )
    return render_template("dash_triagem.html", pacientes=pacientes)

@app.route("/triagem/novo", methods=["GET", "POST"])
@login_required
def triagem_novo():
    require_role("enfermeiro", "administrador")

    # Recebe o ID do paciente (string)
    recepcao_id = request.args.get("recepcao_id")
    form = TriagemForm()

    # Lista de pacientes disponíveis (sem triagem finalizada)
    pacientes_disponiveis = (
        Recepcao.query
        .outerjoin(Triagem)
        .filter((Triagem.finalizado_triagem == False) | (Triagem.id == None))
        .order_by(Recepcao.nome_completo)
        .all()
    )
    form.recepcao_id.choices = [(p.id, f"{p.nome_completo} ({p.id})") for p in pacientes_disponiveis]

    if form.validate_on_submit():

        # Cria a triagem com os dados do formulário
        t = Triagem(
            recepcao_id=recepcao_id,
            ocupacao=form.ocupacao.data or "",
            temperatura=form.temperatura.data or "",
            freq_cardiaca=form.freq_cardiaca.data,
            freq_respiratoria=form.freq_respiratoria.data,
            peso=form.peso.data or "",
            altura=form.altura.data or "",
            queixa_principal=form.queixa_principal.data or "",
            doencas_pre_existentes=form.doencas_pre_existentes.data or "",
            urgencia_triagem=form.urgencia_triagem.data or "",
            responsavel_triagem=current_user.nome_completo,
            observacoes_triagem=form.observacoes_triagem.data or "",
            pressao_arterial=form.pressao_arterial.data or "",
            alergia=form.alergia.data or "",
            saturacao=form.saturacao.data,
            tabagista=form.tabagista.data or False,
            bebida_alcoolica=form.bebida_alcoolica.data or False,
            cirugia_realizada=form.cirugia_realizada.data or "",
            escala_de_dor=form.escala_de_dor.data,
            toma_medicacao=form.toma_medicacao.data or "",
            horario_de_triagem=datetime.utcnow(),
            finalizado_triagem=True  # marca como finalizada
        )

        # Commit com tratamento de erro
        try:
            db1.session.add(t)
            db1.session.commit()
            flash("Triagem registrada e finalizada com sucesso!", "success")
        except Exception as e:
            db1.session.rollback()
            flash(f"Erro ao salvar triagem: {e}", "danger")
            print("Erro ao salvar triagem:", e)
            return redirect(url_for("triagem"))

        return redirect(url_for("triagem"))

    # Paciente selecionado (para template e botão "Chamar Paciente")
    paciente = db1.session.get(Recepcao, recepcao_id) if recepcao_id else None

    # Debug de validação do formulário
    if form.errors:
        print("Erros do formulário:", form.errors)

    return render_template(
        "triagem/form.html",
        form=form,
        action="Finalizar",
        recepcao_id=recepcao_id,
        paciente=paciente
    )

@app.route("/chamar_paciente/<paciente_id>/<destino>", methods=["POST"])
@login_required
def chamar_paciente(paciente_id, destino):
    require_role("enfermeiro", "administrador", "medico")

    paciente = Recepcao.query.get_or_404(paciente_id)

    paciente.chamado = True
    paciente.destino = destino

    db1.session.commit()

    flash(f"Paciente {paciente.nome_completo} chamado para {destino}!", "success")

    # Redireciona de acordo com o destino
    if destino.lower() == "triagem":
        return redirect(url_for('triagem'))  # aqui vai o nome da rota da triagem
    elif destino.lower() == "consulta":
        return redirect(url_for('medico'))  # aqui o nome da rota do médico
    else:
        return redirect(request.referrer or url_for('recepcao'))


@app.route("/triagem/editar/<int:id>", methods=["GET", "POST"])
@login_required
def triagem_editar(id):
    require_role("enfermeiro", "administrador")
    t = Triagem.query.get_or_404(id)
    form = TriagemForm(obj=t)
    form.recepcao_id.choices = [(r.id, f"{r.nome_completo} ({r.id})") for r in Recepcao.query.order_by(Recepcao.nome_completo).all()]

    if form.validate_on_submit():
        t.recepcao_id = form.recepcao_id.data
        t.ocupacao = form.ocupacao.data
        t.temperatura = form.temperatura.data
        t.freq_cardiaca = form.freq_cardiaca.data
        t.freq_respiratoria = form.freq_respiratoria.data
        t.peso = form.peso.data
        t.altura = form.altura.data
        t.queixa_principal = form.queixa_principal.data
        t.doencas_pre_existentes = form.doencas_pre_existentes.data
        t.urgencia_triagem = form.urgencia_triagem.data
        t.pressao_arterial = form.pressao_arterial.data
        t.saturacao = form.saturacao.data
        t.alergia = form.alergia.data
        t.finalizado_triagem = form.finalizado_triagem.data
        db1.session.commit()
        flash("Triagem atualizada com sucesso!", "success")
        return redirect(url_for("triagem"))

    return render_template("triagem/form.html", form=form, action="Editar")

@app.route("/triagem/excluir/<int:id>", methods=["POST"])
@login_required
def triagem_excluir(id):
    require_role("enfermeiro", "administrador")
    t = Triagem.query.get_or_404(id)
    db1.session.delete(t)
    db1.session.commit()
    flash("Triagem excluída com sucesso!", "warning")
    return redirect(url_for("triagem"))

# -----------------------
# GUIA
# -----------------------
@app.route("/guia")
@login_required
def guia():
    return render_template("guia.html")

# -----------------------
# EXECUÇÃO
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)