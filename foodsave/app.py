import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template
from database import init_db
from auth import auth_bp
from foods import foods_bp

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(foods_bp, url_prefix='/api')

# Inicializa o banco
with app.app_context():
    init_db()

# Rota principal (SÓ UMA!)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("✅ FoodSave rodando...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
