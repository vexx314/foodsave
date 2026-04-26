# 🥦 FoodSave — Deploy no Render

## Passo a Passo para publicar no Render

### 1. Suba o código para o GitHub
Crie um repositório no GitHub e envie esta pasta:
```bash
git init
git add .
git commit -m "FoodSave v1"
git remote add origin https://github.com/SEU_USUARIO/foodsave.git
git push -u origin main
```

### 2. Crie uma conta no Render
Acesse https://render.com e faça login com o GitHub.

### 3. Crie um Web Service
- Clique em **New → Web Service**
- Conecte seu repositório do GitHub
- Configure assim:

| Campo | Valor |
|-------|-------|
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

### 4. Adicione um Disco Persistente (para o SQLite não sumir)
- Na aba **Disks** do seu serviço, clique em **Add Disk**
- Name: `foodsave-data`
- Mount Path: `/var/data`
- Size: 1 GB (grátis no plano pago / use 512MB no gratuito)

### 5. Configure variável de ambiente
Na aba **Environment**, adicione:
- `RENDER_DISK_PATH` = `/var/data`
- `SECRET_KEY` = (gere uma string aleatória, ex: `render-gera-automatico`)

### 6. Clique em Deploy!
Aguarde o build (~2-5 min). Seu app estará em:
`https://foodsave-XXXX.onrender.com`

---

## ⚠️ Aviso sobre plano gratuito
No plano gratuito do Render:
- O servidor "dorme" após 15 min sem uso (primeira requisição demora ~30s pra acordar)
- **Persistent Disk não está disponível no free tier** — os dados do SQLite serão apagados a cada deploy
- Para dados persistentes de graça: use o plano pago ($7/mês) com Disk, ou substitua SQLite por PostgreSQL gratuito (ver abaixo)

## Alternativa gratuita com PostgreSQL
O Render oferece PostgreSQL gratuito por 90 dias. Após isso, é necessário pagar ou exportar os dados.

---

## Estrutura do Projeto
```
foodsave/
├── app.py              # Flask app (entry point)
├── Procfile            # Comando de start para o Render
├── render.yaml         # Config do Render (opcional)
├── requirements.txt    # Dependências Python
├── .gitignore
├── models/
│   └── database.py     # SQLite com suporte a disco persistente
├── routes/
│   ├── auth.py         # /register /login /logout /me
│   └── foods.py        # /foods /history
└── templates/
    └── index.html      # Frontend completo
```
