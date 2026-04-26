from flask import Blueprint, request, jsonify, session
from database import get_db
from datetime import date

foods_bp = Blueprint('foods', __name__)

def require_auth():
    uid = session.get('user_id')
    if not uid:
        return None, (jsonify({'error': 'Não autenticado'}), 401)
    return uid, None

@foods_bp.route('/foods', methods=['GET'])
def get_foods():
    uid, err = require_auth()
    if err: return err

    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM foods WHERE user_id = ? AND status = 'ativo' ORDER BY validade ASC",
            (uid,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()

@foods_bp.route('/foods', methods=['POST'])
def add_food():
    uid, err = require_auth()
    if err: return err

    data      = request.get_json()
    nome      = (data.get('nome') or '').strip()
    categoria = data.get('categoria') or 'Outros'
    quantidade= (data.get('quantidade') or '').strip()
    validade  = data.get('validade') or ''
    preco     = float(data.get('preco') or 0)

    if not nome or not quantidade or not validade:
        return jsonify({'error': 'Campos obrigatórios faltando.'}), 400

    conn = get_db()
    try:
        cur = conn.execute(
            'INSERT INTO foods (user_id, nome, categoria, quantidade, validade, preco) VALUES (?,?,?,?,?,?)',
            (uid, nome, categoria, quantidade, validade, preco)
        )
        conn.commit()
        food = conn.execute('SELECT * FROM foods WHERE id = ?', (cur.lastrowid,)).fetchone()
        return jsonify(dict(food)), 201
    finally:
        conn.close()

@foods_bp.route('/foods/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    uid, err = require_auth()
    if err: return err

    data      = request.get_json()
    nome      = (data.get('nome') or '').strip()
    categoria = data.get('categoria') or 'Outros'
    quantidade= (data.get('quantidade') or '').strip()
    validade  = data.get('validade') or ''
    preco     = float(data.get('preco') or 0)

    if not nome or not quantidade or not validade:
        return jsonify({'error': 'Campos obrigatórios faltando.'}), 400

    conn = get_db()
    try:
        existing = conn.execute('SELECT id FROM foods WHERE id = ? AND user_id = ?', (food_id, uid)).fetchone()
        if not existing:
            return jsonify({'error': 'Alimento não encontrado.'}), 404

        conn.execute(
            'UPDATE foods SET nome=?, categoria=?, quantidade=?, validade=?, preco=? WHERE id=? AND user_id=?',
            (nome, categoria, quantidade, validade, preco, food_id, uid)
        )
        conn.commit()
        food = conn.execute('SELECT * FROM foods WHERE id = ?', (food_id,)).fetchone()
        return jsonify(dict(food))
    finally:
        conn.close()

@foods_bp.route('/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    uid, err = require_auth()
    if err: return err

    conn = get_db()
    try:
        existing = conn.execute('SELECT id FROM foods WHERE id = ? AND user_id = ?', (food_id, uid)).fetchone()
        if not existing:
            return jsonify({'error': 'Alimento não encontrado.'}), 404

        conn.execute('DELETE FROM foods WHERE id = ? AND user_id = ?', (food_id, uid))
        conn.commit()
        return jsonify({'ok': True})
    finally:
        conn.close()

@foods_bp.route('/foods/<int:food_id>/mark', methods=['POST'])
def mark_food(food_id):
    uid, err = require_auth()
    if err: return err

    data = request.get_json()
    tipo = data.get('tipo')  # 'consumed' or 'wasted'
    if tipo not in ('consumed', 'wasted'):
        return jsonify({'error': 'Tipo inválido.'}), 400

    conn = get_db()
    try:
        food = conn.execute('SELECT * FROM foods WHERE id = ? AND user_id = ?', (food_id, uid)).fetchone()
        if not food:
            return jsonify({'error': 'Alimento não encontrado.'}), 404

        today = date.today().isoformat()
        conn.execute(
            'INSERT INTO history (user_id, food_name, food_category, tipo, preco, data) VALUES (?,?,?,?,?,?)',
            (uid, food['nome'], food['categoria'], tipo, food['preco'], today)
        )
        conn.execute("UPDATE foods SET status = ? WHERE id = ?", (tipo, food_id))
        conn.commit()
        return jsonify({'ok': True})
    finally:
        conn.close()

@foods_bp.route('/history', methods=['GET'])
def get_history():
    uid, err = require_auth()
    if err: return err

    conn = get_db()
    try:
        rows = conn.execute(
            'SELECT * FROM history WHERE user_id = ? ORDER BY created_at DESC',
            (uid,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()
