from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json
import cv2
import numpy as np
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

inspecao_bp = Blueprint("inspecao", __name__)
PASTA_INSPECOES = Path(__file__).resolve().parent / "static" / "inspecoes"
PASTA_INSPECOES.mkdir(parents=True, exist_ok=True)

# Percentual mínimo da ROI ocupado pelo maior objeto.
AREA_MINIMA_PERCENTUAL = 5.0

def usuario_logado():
    return session.get("usuario")

@inspecao_bp.route("/inspecao")
def inspecao():
    usuario = usuario_logado()
    if not usuario:
        return redirect(url_for("login"))
    return render_template("inspecao.html", usuario=usuario)

@inspecao_bp.route("/inspecionar-frame", methods=["POST"])
def analisar_frame():
    if not usuario_logado():
        return jsonify({"erro": "Sessão expirada."}), 401
        
    arquivo = request.files.get("frame")
    if arquivo is None:
        return jsonify({"erro": "Nenhuma imagem foi recebida."}), 400
        
    # 1. Converte os bytes recebidos em imagem OpenCV.
    dados = np.frombuffer(arquivo.read(), dtype=np.uint8)
    imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)
    if imagem is None:
        return jsonify({"erro": "Não foi possível interpretar a imagem."}), 400
        
    altura, largura = imagem.shape[:2]
    
    # 2. Define a Região de Interesse (ROI) central.
    x1 = int(largura * 0.25)
    x2 = int(largura * 0.75)
    y1 = int(altura * 0.25)
    y2 = int(altura * 0.75)
    roi = imagem[y1:y2, x1:x2]
    
    # 3. Pré-processamento.
    cinza = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    suave = cv2.GaussianBlur(cinza, (5, 5), 0)
    
    # 4. Otsu escolhe automaticamente o limiar.
    # THRESH_BINARY_INV deixa objetos escuros em branco na máscara.
    _, mascara = cv2.threshold(
        suave,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )
    
    # 5. Remove pequenos ruídos.
    kernel = np.ones((3, 3), np.uint8)
    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1,
    )
    
    # 6. Localiza objetos na máscara.
    contornos, _ = cv2.findContours(
        mascara,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    
    maior_contorno = max(contornos, key=cv2.contourArea) if contornos else None
    maior_area = cv2.contourArea(maior_contorno) if maior_contorno is not None else 0
    area_roi = mascara.shape[0] * mascara.shape[1]
    percentual = (maior_area / area_roi) * 100 if area_roi else 0
    
    # 7. Regra de decisão do processo.
    status = "OK" if percentual >= AREA_MINIMA_PERCENTUAL else "NOK"
    
    # 8. Cria uma imagem anotada para o operador.
    resultado = imagem.copy()
    cor = (0, 180, 0) if status == "OK" else (0, 0, 255)
    cv2.rectangle(resultado, (x1, y1), (x2, y2), cor, 3)
    
    if maior_contorno is not None:
        deslocamento = np.array([[[x1, y1]]])
        contorno_na_imagem = maior_contorno + deslocamento
        cv2.drawContours(resultado, [contorno_na_imagem], -1, cor, 2)
        
    texto = f"{status} - ocupacao: {percentual:.1f}%"
    cv2.putText(
        resultado,
        texto,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        cor,
        2,
        cv2.LINE_AA,
    )
    
    # 9. Salva imagens e dados da inspeção.
    identificador = uuid4().hex[:8]
    nome_original = f"inspecao_{identificador}_original.png"
    nome_mascara = f"inspecao_{identificador}_mascara.png"
    nome_resultado = f"inspecao_{identificador}_resultado.png"
    nome_dados = f"inspecao_{identificador}.json"
    
    cv2.imwrite(str(PASTA_INSPECOES / nome_original), imagem)
    cv2.imwrite(str(PASTA_INSPECOES / nome_mascara), mascara)
    cv2.imwrite(str(PASTA_INSPECOES / nome_resultado), resultado)
    
    dados_inspecao = {
        "id": identificador,
        "data_hora": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "area_pixels": int(maior_area),
        "percentual_ocupacao": round(percentual, 2),
        "limite_percentual": AREA_MINIMA_PERCENTUAL,
    }
    
    with open(PASTA_INSPECOES / nome_dados, "w", encoding="utf-8") as arquivo_json:
        json.dump(dados_inspecao, arquivo_json, ensure_ascii=False, indent=2)
        
    return jsonify({
        "url": url_for(
            "inspecao.resultado_inspecao",
            identificador=identificador,
        )
    })

@inspecao_bp.route("/resultado-inspecao/<identificador>")
def resultado_inspecao(identificador):
    if not usuario_logado():
        return redirect(url_for("login"))
        
    if len(identificador) != 8 or not all(
        caractere in "0123456789abcdef" for caractere in identificador
    ):
        return redirect(url_for("inspecao.inspecao"))
        
    nome_original = f"inspecao_{identificador}_original.png"
    nome_mascara = f"inspecao_{identificador}_mascara.png"
    nome_resultado = f"inspecao_{identificador}_resultado.png"
    nome_dados = f"inspecao_{identificador}.json"
    caminho_dados = PASTA_INSPECOES / nome_dados
    
    if not caminho_dados.exists():
        return redirect(url_for("inspecao.inspecao"))
        
    with open(caminho_dados, "r", encoding="utf-8") as arquivo_json:
        dados_inspecao = json.load(arquivo_json)
        
    return render_template(
        "resultado_inspecao.html",
        dados=dados_inspecao,
        original=url_for("static", filename=f"inspecoes/{nome_original}"),
        mascara=url_for("static", filename=f"inspecoes/{nome_mascara}"),
        resultado=url_for("static", filename=f"inspecoes/{nome_resultado}"),
    )
