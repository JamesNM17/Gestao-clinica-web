from main import app
from dados1 import db1
from model import Funcionarios
from werkzeug.security import generate_password_hash


def criar_usuario(usuario, senha, nome_completo, funcao, sexo, email):
    with app.app_context():

        # 🔍 Verifica se o usuário já existe
        existente = Funcionarios.query.filter_by(usuario=usuario).first()
        if existente:
            print(f"⚠️ O usuário {usuario} já existe!")
            return

        # 🔐 Criação com hash
        usuario_criado = Funcionarios(
            nome_completo=nome_completo,
            usuario=usuario,
            funcao=funcao,
            sexo=sexo,
            email=email,
            senha=generate_password_hash(senha),  # 🔥 CORREÇÃO
            online=False
        )

        db1.session.add(usuario_criado)
        db1.session.commit()

        print(f"✅ Usuário {usuario} ({funcao}) criado com sucesso!")
        print(f"Usuário: {usuario}")
        print("Senha: definida com segurança")
        print(f"E-mail: {email}")


def criar_usuarios_padrao():
    usuarios = [
        (
            "admin1",
            "admin1234",
            "James",
            "Administrador",
            "Masculino",
            "admin@vitaslotus.com"
        )
    ]

    for usuario in usuarios:
        criar_usuario(*usuario)


if __name__ == "__main__":
    criar_usuarios_padrao()