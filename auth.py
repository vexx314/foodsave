from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome  = (data.get('nome') or '').strip()
    email = (data.get('email') or '').strip().lower()
    senha = data.get('senha') or ''
    role  = data.get('role') or 'pessoal'

    if not nome or not email or not senha:
        return jsonify({'error': 'Preencha todos os campos.'}), 400
    if len(senha) < 6:
        return jsonify({'error': 'A senha deve ter no mínimo 6 caracteres.'}), 400

    conn = get_db()
    try:
        existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            return jsonify({'error': 'Este e-mail já está em uso.'}), 409

        hashed = generate_password_hash(senha)
        cur = conn.execute(
            'INSERT INTO users (nome, email, senha, role) VALUES (?, ?, ?, ?)',
            (nome, email, hashed, role)
        )
        conn.commit()
        user_id = cur.lastrowid

        session['user_id'] = user_id
        return jsonify({
            'id': user_id,
            'nome': nome,
            'email': email,
            'role': role
        }), 201
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data  = request.get_json()
    email = (data.get('email') or '').strip().lower()
    senha = data.get('senha') or ''

    if not email or not senha:
        return jsonify({'error': 'Preencha e-mail e senha.'}), 400

    conn = get_db()
    try:
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if not user:
            return jsonify({'error': 'E-mail não encontrado.'}), 404
        if not check_password_hash(user['senha'], senha):
            return jsonify({'error': 'Senha incorreta.'}), 401

        session['user_id'] = user['id']
        return jsonify({
            'id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'role': user['role']
        })
    finally:
        conn.close()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@auth_bp.route('/me', methods=['GET'])
def me():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Não autenticado'}), 401
    conn = get_db()
    try:
        user = conn.execute('SELECT id, nome, email, role FROM users WHERE id = ?', (uid,)).fetchone()
        if not user:
            session.clear()
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify(dict(user))
    finally:
        conn.close()
