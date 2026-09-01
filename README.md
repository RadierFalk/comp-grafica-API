# Comp Gráfica API

Aplicação acadêmica de visão computacional construída com Flask, OpenCV e NumPy. O projeto permite capturar imagens pela câmera do navegador, gerar uma versão em tons de cinza e executar uma inspeção visual simples baseada em uma região de interesse (ROI), segmentação por Otsu e análise de contornos.

## Funcionalidades

- Login simples por variáveis de ambiente
- Captura de frames pela câmera do navegador
- Conversão de imagens para tons de cinza
- Inspeção visual de uma região central da imagem
- Segmentação automática com limiar de Otsu
- Detecção do maior contorno encontrado
- Classificação `OK` / `NOK` baseada na ocupação percentual da ROI
- Armazenamento local das imagens e dos dados da inspeção

## Tecnologias

- Python
- Flask
- OpenCV
- NumPy
- HTML / CSS / JavaScript

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/RadierFalk/comp-grafica-API.git
cd comp-grafica-API
```

### 2. Crie um ambiente virtual

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie `.env.example` para `.env` e altere os valores:

```env
SECRET_KEY=gere-uma-chave-segura-aqui
APP_USER=admin
APP_PASSWORD=troque-esta-senha
FLASK_DEBUG=0
```

### 5. Inicie a aplicação

```bash
python app.py
```

Depois acesse `http://127.0.0.1:5000` no navegador.

> O acesso à câmera pelo navegador exige permissão do usuário. Em ambientes remotos, normalmente também é necessário HTTPS.

## Como funciona a inspeção

1. O navegador captura um frame da câmera.
2. O servidor seleciona a região central da imagem como ROI.
3. A ROI é convertida para escala de cinza.
4. Um filtro Gaussiano reduz pequenos ruídos.
5. O método de Otsu cria uma máscara binária automaticamente.
6. Uma operação morfológica de abertura remove ruídos residuais.
7. O maior contorno é localizado.
8. A área do contorno é comparada com a área total da ROI.
9. A peça recebe status `OK` ou `NOK` conforme o limite configurado.

## Estrutura atual

```text
comp-grafica-API/
├── app.py
├── camera.py
├── inspecao.py
├── requirements.txt
├── .env.example
├── static/
│   ├── css/
│   ├── capturas/
│   └── inspecoes/
└── templates/
```

## Próximas evoluções recomendadas

- Extrair o processamento OpenCV para uma camada `services/`
- Criar histórico de inspeções com SQLite
- Tornar os parâmetros da inspeção configuráveis pela interface
- Permitir selecionar diferentes regiões de interesse
- Adicionar métricas como largura, altura, perímetro e circularidade
- Criar testes automatizados para o processamento de imagens
- Adicionar API REST para inspeções
- Criar dashboard com taxa de aprovação e histórico de resultados

## Observação

O sistema de autenticação atual é propositalmente simples e adequado apenas para estudo/demonstração. Para produção, utilize armazenamento seguro de usuários e senhas com hash.
