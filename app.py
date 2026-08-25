import os

from flask import Flask, redirect, render_template, request, session, url_for
from camera import camera_bp


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave-apenas-para-aula")

# Credenciais apenas para demonstração.
USUARIO_CORRETO = os.getenv("APP_USER", "admin")
SENHA_CORRETA = os.getenv("APP_PASSWORD", "1234")

# Registra as rotas da câmera.
app.register_blueprint(camera_bp)


@app.route("/", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")

        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            session["usuario"] = usuario
            return redirect(url_for("bem_vindo"))

        erro = "Usuário ou senha incorretos."

    return render_template("login.html", erro=erro)


@app.route("/bem-vindo")
def bem_vindo():
    usuario = session.get("usuario")

    if not usuario:
        return redirect(url_for("login"))

    return render_template("bem_vindo.html", usuario=usuario)


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)