import string
import random
from datetime import datetime
from flask import redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from dados1 import db1
import random
from flask import session, jsonify
from datetime import timedelta

# -------------------------
# Gerador de IDs para Recepção
# -------------------------
def gerar_id_recepcao():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=5))

# -------------------------
# Funcionários
# -------------------------
class Funcionarios(UserMixin, db1.Model):
    __tablename__ = 'funcionarios'

    id = db1.Column(db1.Integer, primary_key=True)
    nome_completo = db1.Column(db1.String(100), nullable=False)
    usuario = db1.Column(db1.String(70), nullable=False, unique=True)
    funcao = db1.Column(db1.String(30), nullable=False)
    senha = db1.Column(db1.String(200), nullable=False)
    sexo = db1.Column(db1.String(15), nullable=True)
    email = db1.Column(db1.String(120), unique=True, nullable=False)
    data_criacao = db1.Column(db1.DateTime, default=datetime.utcnow)
    cpf = db1.Column(db1.String(14), unique=True, nullable=True)
    telefone = db1.Column(db1.String(20), nullable=True)
    data_nascimento = db1.Column(db1.Date, nullable=True)
    ultimo_login = db1.Column(db1.DateTime, nullable=True)
    ultimo_logout = db1.Column(db1.DateTime)
    online = db1.Column(db1.Boolean, default=False)
    foto = db1.Column(db1.String(200))


# -------------------------
# Recepção
# -------------------------
class Recepcao(db1.Model):
    __tablename__ = 'recepcao'

    id = db1.Column(db1.String(5), primary_key=True, default=gerar_id_recepcao)
    chamado = db1.Column(db1.Boolean, default=False)        
    destino = db1.Column(db1.String(50), nullable=True)  
    nome_completo = db1.Column(db1.String(100), nullable=False)
    data_nascimento = db1.Column(db1.Date, nullable=True)
    sexo = db1.Column(db1.String(15), nullable=True)
    contato = db1.Column(db1.String(100), nullable=True)
    cpf = db1.Column(db1.String(30), nullable=True)
    atendimento = db1.Column(db1.String(50), nullable=True)
    plano = db1.Column(db1.String(50), nullable=True)
    horario_chegada = db1.Column(db1.DateTime, default=datetime.utcnow)
    observacoes_recepcao = db1.Column(db1.Text)
    urgencia_recepcao = db1.Column(db1.String(50))
    responsavel_recepcao = db1.Column(db1.String(100))

    triagem = db1.relationship(
        "Triagem",
        back_populates="recepcao",
        uselist=False,
        cascade="all, delete-orphan"
    )

    medico = db1.relationship(
        "Medico",
        back_populates="recepcao",
        uselist=False,
        cascade="all, delete-orphan"
    )

# -------------------------
# Triagem
# -------------------------
class Triagem(db1.Model):
    __tablename__ = 'triagem'

    id = db1.Column(db1.Integer, primary_key=True)
    recepcao_id = db1.Column(
        db1.String(5),
        db1.ForeignKey('recepcao.id'),
        nullable=False,
        unique=True
    )

    ocupacao = db1.Column(db1.String(100))
    temperatura = db1.Column(db1.String(20))
    freq_cardiaca = db1.Column(db1.Integer)
    freq_respiratoria = db1.Column(db1.Integer)
    peso = db1.Column(db1.String(20))
    altura = db1.Column(db1.String(20))
    queixa_principal = db1.Column(db1.Text)
    doencas_pre_existentes = db1.Column(db1.Text)
    urgencia_triagem = db1.Column(db1.String(50))
    finalizado_triagem = db1.Column(db1.Boolean, default=False)
    responsavel_triagem = db1.Column(db1.String(100))
    observacoes_triagem = db1.Column(db1.Text)
    pressao_arterial = db1.Column(db1.String(20))  # ou o tamanho que quiser
    alergia = db1.Column(db1.String(50))
    saturacao = db1.Column(db1.Integer)
    tabagista = db1.Column(db1.Boolean, default=False)
    bebida_alcoolica = db1.Column(db1.Boolean, default=False)
    cirugia_realizada = db1.Column(db1.Text)
    horario_de_triagem = db1.Column(db1.DateTime, default=datetime.utcnow)
    escala_de_dor = db1.Column(db1.Integer)
    toma_medicacao = db1.Column(db1.Text)

    recepcao = db1.relationship("Recepcao", back_populates="triagem")

# -------------------------
# Médico
# -------------------------
class Medico(db1.Model):
    __tablename__ = 'medico'

    id = db1.Column(db1.Integer, primary_key=True)
    recepcao_id = db1.Column(
        db1.String(5),
        db1.ForeignKey('recepcao.id'),
        nullable=False,
        unique=True
    )

    feedback = db1.Column(db1.Text)
    diagnostico = db1.Column(db1.Text)
    prescricao = db1.Column(db1.Text)
    finalizado_medico = db1.Column(db1.Boolean, default=False)
    responsavel_medico = db1.Column(db1.String(100))
    observacoes_medico = db1.Column(db1.Text)
    horario_de_finalizacao = db1.Column(db1.DateTime, default=datetime.utcnow)

    recepcao = db1.relationship("Recepcao", back_populates="medico")

# -------------------------
# Admin
# -------------------------
class BaseAdmin(ModelView):
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))

class AdminRecepcao(BaseAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.funcao or "").lower() in ["recepcionista", "administrador"]

class AdminTriagem(BaseAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.funcao or "").lower() in ["enfermeiro", "administrador"]

class AdminMedico(BaseAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.funcao or "").lower() in ["medico", "administrador"]

class AdminFuncionarios(BaseAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.funcao or "").lower() == "administrador"