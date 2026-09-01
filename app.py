import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

from camera import camera_bp
from inspecao import inspecao_bp

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "troque-esta-chave-em-producao"),
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Credenciais simples para fins acadêmicos/demonstração.
USUARIO_CORRETO = os.getenv("APP_USER", "admin")
SENHA_CORRETA = os.getenv("APP_PASSWORD", "1234")

app.register_blueprint(camera_bp)
app.register_blueprint(inspecao_bp)


@app.route("/", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            session.clear()
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
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
