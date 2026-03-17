from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, SelectField, SubmitField, TextAreaField, DateField, BooleanField, PasswordField)
from wtforms.validators import (InputRequired, Optional, Length, Regexp, NumberRange)
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Optional, Length, NumberRange, Regexp
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SelectField, BooleanField, SubmitField, DateField, PasswordField
from wtforms.validators import InputRequired, Optional, Length, NumberRange, Regexp

# -------------------------
# Formulário de Funcionários
# -------------------------
class FuncionarioForm(FlaskForm):
    nome_completo = StringField('Nome completo', validators=[InputRequired(), Length(max=100)])
    usuario = StringField('Usuário', validators=[InputRequired(), Length(max=70)])
    funcao = SelectField(
        'Função', 
        choices=[('Administrador','Administrador'), ('Recepcionista','Recepcionista'), ('Médico','Médico'), ('Enfermeiro','Enfermeiro')], 
        validators=[InputRequired()]
    )
    senha = PasswordField('Senha', validators=[InputRequired(), Length(min=6, max=200)])
    sexo = SelectField('Sexo', choices=[('Masculino','Masculino'), ('Feminino','Feminino'), ('Outro','Outro')], validators=[Optional()])
    submit = SubmitField('Salvar')

# -------------------------
# Formulário de Recepção
# -------------------------
class RecepcaoForm(FlaskForm):
    nome_completo = StringField('Nome completo', validators=[InputRequired(), Length(max=100)])
    data_nascimento = DateField('Data de nascimento', format='%Y-%m-%d', validators=[InputRequired(message="A data de nascimento é obrigatória")])
    sexo = SelectField('Sexo', choices=[('Homem','Homem'), ('Mulher','Mulher'), ('Outro','Outro')], validators=[InputRequired(message="Selecione o sexo")])
    contato = StringField('Contato', validators=[Optional(), Length(max=100)])
    cpf = StringField('CPF', validators=[Optional(), Length(max=30)])
    atendimento = SelectField('Atendimento', choices=[('Consulta','Consulta'), ('Checkup','Check-up'), ('Outro','Outro')], validators=[Optional()])
    plano = SelectField('Plano', choices=[('SUS','SUS'), ('Particular','Particular'), ('Outro','Outro')], validators=[Optional()])
    observacoes_recepcao = TextAreaField('Observações', validators=[Optional(), Length(max=2000)])
    urgencia_recepcao = SelectField('Urgência', choices=[('Vermelho','Vermelho'), ('Laranja','Laranja'), ('Amarelo','Amarelo'), ('Verde','Verde'), ('Azul','Azul')], validators=[Optional()])
    responsavel_recepcao = StringField('Responsável', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Salvar')

# -------------------------
# Formulário de Triagem
# -------------------------
class TriagemForm(FlaskForm):

    recepcao_id = SelectField("Paciente", coerce=str, validators=[InputRequired()])
    
    ocupacao = StringField('Ocupação', validators=[Optional(), Length(max=100)])
    
    # Campos numéricos agora com FloatField/IntegerField, sem regex rígido
    temperatura = StringField('Temperatura (°C)', validators=[Optional()])
    freq_cardiaca = StringField('Frequência cardíaca (bpm)', validators=[Optional()])
    freq_respiratoria = StringField('Frequência respiratória (rpm)', validators=[Optional()])
    peso = StringField('Peso (kg)', validators=[Optional()])
    altura = StringField('Altura (m)', validators=[Optional()])
    pressao_arterial = StringField('Pressão arterial (mmHg)', validators=[Optional()])  # permanece String
    
    saturacao = StringField('Saturação (%)', validators=[Optional()])
    alergia = StringField('Alergia', validators=[Optional(), Length(max=50)])
    queixa_principal = TextAreaField('Queixa principal', validators=[Optional(), Length(max=2000)])
    doencas_pre_existentes = TextAreaField('Doenças preexistentes', validators=[Optional(), Length(max=2000)])
    
    urgencia_triagem = SelectField(
        'Urgência',
        choices=[
            ('Vermelho','Vermelho - Emergência'),
            ('Laranja','Laranja - Muito urgente'),
            ('Amarelo','Amarelo - Urgente'),
            ('Verde','Verde - Pouco urgente'),
            ('Azul','Azul - Não urgente')
        ],
        validators=[InputRequired()]
    )
    
    observacoes_triagem = TextAreaField('Observações da triagem', validators=[Optional(), Length(max=2000)])
    tabagista = BooleanField('Tabagista')
    bebida_alcoolica = BooleanField('Bebe álcool')
    cirugia_realizada = TextAreaField('Cirurgias realizadas', validators=[Optional(), Length(max=2000)])
    escala_de_dor = IntegerField('Escala de dor (0-10)', validators=[Optional(), NumberRange(min=0, max=10)])
    toma_medicacao = TextAreaField('Medicação em uso', validators=[Optional(), Length(max=2000)])
    
    submit = SubmitField('Salvar')
# -------------------------
# Formulário de Médico
# -------------------------
class MedicoForm(FlaskForm):
    # Campo para selecionar o paciente (recepcao_id)
    recepcao_id = SelectField("Paciente", coerce=str, validators=[InputRequired()])

    # Campos do atendimento médico
    feedback = TextAreaField("Feedback", validators=[Optional()])
    diagnostico = TextAreaField("Diagnóstico", validators=[Optional()])
    prescricao = TextAreaField("Prescrição", validators=[Optional()])
    observacoes_medico = TextAreaField("Observações", validators=[Optional()])

    def preencher_form(self, paciente):
        """
        Método para pré-preencher os campos do formulário com dados existentes do paciente.
        paciente: instância de Recepcao que pode ter paciente.medico
        """
        # Preenche recepcao_id
        self.recepcao_id.choices = [(paciente.id, f"{paciente.id} - {paciente.nome_completo}")]
        self.recepcao_id.data = paciente.id

        # Se já existe atendimento médico, preenche os campos
        if paciente.medico:
            self.feedback.data = paciente.medico.feedback
            self.diagnostico.data = paciente.medico.diagnostico
            self.prescricao.data = paciente.medico.prescricao
            self.observacoes_medico.data = paciente.medico.observacoes_medico

# -------------------------
# Formulário de Login
# -------------------------
class LoginForm(FlaskForm):
    usuario = StringField('Usuário', validators=[InputRequired()])
    senha = PasswordField('Senha', validators=[InputRequired()])
    submit = SubmitField('Entrar')
