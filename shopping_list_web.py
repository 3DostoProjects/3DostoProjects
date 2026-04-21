#!/usr/bin/env python3
"""
Lista de Compras Sofisticada - Versão Web com Flask e SQLite
Funcionalidades: Adicionar, Editar, Check, Delete, Preço, Total, Data Automática
"""

from flask import Flask, render_template_string, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DATABASE = 'shopping_list.db'

def get_db():
    """Obter conexão com banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar banco de dados"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL DEFAULT 1,
            unit TEXT DEFAULT 'un',
            price REAL DEFAULT 0,
            checked INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Template HTML completo com CSS e JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛒 Lista de Compras Sofisticada</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #2c3e50;
            --secondary: #3498db;
            --success: #27ae60;
            --danger: #e74c3c;
            --warning: #f39c12;
            --light: #ecf0f1;
            --dark: #2c3e50;
            --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.5s ease;
        }

        .header h1 {
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .header p {
            color: #7f8c8d;
            font-size: 1.1rem;
        }

        /* Cards */
        .card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 30px;
            margin-bottom: 20px;
            animation: fadeInUp 0.5s ease;
        }

        .card-title {
            font-size: 1.3rem;
            color: var(--primary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-title i {
            color: var(--secondary);
        }

        /* Form */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-weight: 500;
            color: var(--dark);
            margin-bottom: 8px;
            font-size: 0.9rem;
        }

        .form-group input,
        .form-group select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--secondary);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        /* Buttons */
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }

        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Poppins', sans-serif;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-primary {
            background: var(--success);
            color: white;
        }

        .btn-secondary {
            background: var(--secondary);
            color: white;
        }

        .btn-warning {
            background: var(--warning);
            color: white;
        }

        .btn-danger {
            background: var(--danger);
            color: white;
        }

        .btn-info {
            background: #95a5a6;
            color: white;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* Table */
        .table-container {
            overflow-x: auto;
            border-radius: 15px;
            margin-top: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        thead {
            background: var(--gradient);
            color: white;
        }

        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
        }

        td {
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
            vertical-align: middle;
        }

        tbody tr {
            transition: all 0.3s ease;
        }

        tbody tr:hover {
            background: #f8f9fa;
            transform: scale(1.01);
        }

        tbody tr.checked {
            background: #d5f5e3;
            opacity: 0.8;
        }

        tbody tr.selected {
            background: #d6eaf8;
            border-left: 4px solid var(--secondary);
        }

        /* Status badges */
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .status-pending {
            background: #fef3cd;
            color: #856404;
        }

        .status-completed {
            background: #d4edda;
            color: #155724;
        }

        /* Total Section */
        .total-section {
            background: var(--gradient);
            color: white;
            padding: 25px 30px;
            border-radius: 15px;
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
            50% { box-shadow: 0 5px 30px rgba(102, 126, 234, 0.6); }
        }

        .total-label {
            font-size: 1.3rem;
            font-weight: 500;
        }

        .total-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2ecc71;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        /* Stats */
        .stats-bar {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .stat-item {
            background: white;
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .stat-icon {
            font-size: 1.5rem;
        }

        .stat-text {
            font-size: 0.9rem;
            color: #7f8c8d;
        }

        .stat-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary);
        }

        /* Animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            .total-section {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .total-value {
                font-size: 2rem;
            }

            .btn-group {
                justify-content: center;
            }
        }

        /* Action buttons in table */
        .action-btns {
            display: flex;
            gap: 5px;
        }

        .action-btn {
            padding: 8px 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }

        .action-btn:hover {
            transform: scale(1.1);
        }

        .action-btn.edit {
            background: var(--secondary);
            color: white;
        }

        .action-btn.check {
            background: var(--warning);
            color: white;
        }

        .action-btn.delete {
            background: var(--danger);
            color: white;
        }

        /* Toast notifications */
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 10px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }

        .toast.success {
            background: var(--success);
        }

        .toast.error {
            background: var(--danger);
        }

        .toast.warning {
            background: var(--warning);
        }

        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #95a5a6;
        }

        .empty-state i {
            font-size: 5rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        .empty-state h3 {
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-shopping-cart"></i> Minha Lista de Compras</h1>
            <p>Gerencie suas compras de forma inteligente e sofisticada</p>
        </div>

        <!-- Input Form -->
        <div class="card">
            <h2 class="card-title"><i class="fas fa-plus-circle"></i> Adicionar/Editar Item</h2>
            <form id="itemForm">
                <input type="hidden" id="itemId" value="">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="itemName"><i class="fas fa-tag"></i> Nome do Item</label>
                        <input type="text" id="itemName" placeholder="Ex: Arroz" required>
                    </div>
                    <div class="form-group">
                        <label for="itemQuantity"><i class="fas fa-hashtag"></i> Quantidade</label>
                        <input type="number" id="itemQuantity" step="0.01" value="1" min="0.01">
                    </div>
                    <div class="form-group">
                        <label for="itemUnit"><i class="fas fa-balance-scale"></i> Unidade</label>
                        <select id="itemUnit">
                            <option value="un">Unidade</option>
                            <option value="kg">Quilograma</option>
                            <option value="g">Grama</option>
                            <option value="L">Litro</option>
                            <option value="mL">Mililitro</option>
                            <option value="pct">Pacote</option>
                            <option value="dz">Dúzia</option>
                            <option value="cx">Caixa</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="itemPrice"><i class="fas fa-dollar-sign"></i> Preço (R$)</label>
                        <input type="number" id="itemPrice" step="0.01" min="0" placeholder="0.00">
                    </div>
                    <div class="form-group" style="grid-column: span 2;">
                        <label for="itemNotes"><i class="fas fa-sticky-note"></i> Observações</label>
                        <input type="text" id="itemNotes" placeholder="Ex: Marca preferida, validade, etc.">
                    </div>
                </div>
                <div class="btn-group">
                    <button type="submit" class="btn btn-primary" id="btnSubmit">
                        <i class="fas fa-plus"></i> Adicionar Item
                    </button>
                    <button type="button" class="btn btn-info" id="btnCancel" style="display: none;" onclick="cancelEdit()">
                        <i class="fas fa-times"></i> Cancelar Edição
                    </button>
                    <button type="button" class="btn btn-info" onclick="clearForm()">
                        <i class="fas fa-broom"></i> Limpar Campos
                    </button>
                </div>
            </form>
        </div>

        <!-- Items Table -->
        <div class="card">
            <h2 class="card-title"><i class="fas fa-list"></i> Itens da Lista</h2>
            <div class="table-container">
                <table id="itemsTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Item</th>
                            <th>Qtd</th>
                            <th>Unid</th>
                            <th>Preço Unit</th>
                            <th>Subtotal</th>
                            <th>Status</th>
                            <th>Data Inclusão</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="itemsBody">
                        <!-- Preenchido via JavaScript -->
                    </tbody>
                </table>
                <div id="emptyState" class="empty-state" style="display: none;">
                    <i class="fas fa-shopping-basket"></i>
                    <h3>Sua lista está vazia</h3>
                    <p>Adicione itens para começar suas compras!</p>
                </div>
            </div>

            <!-- Total Section -->
            <div class="total-section">
                <div>
                    <div class="total-label"><i class="fas fa-coins"></i> Valor Total da Lista</div>
                    <div class="total-value" id="totalValue">R$ 0,00</div>
                </div>
            </div>

            <!-- Stats Bar -->
            <div class="stats-bar">
                <div class="stat-item">
                    <span class="stat-icon">📦</span>
                    <div>
                        <div class="stat-text">Total de Itens</div>
                        <div class="stat-value" id="totalItems">0</div>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">✅</span>
                    <div>
                        <div class="stat-text">Marcados</div>
                        <div class="stat-value" id="checkedItems">0</div>
                    </div>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">⏳</span>
                    <div>
                        <div class="stat-text">Pendentes</div>
                        <div class="stat-value" id="pendingItems">0</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let editingId = null;

        // Carregar dados ao iniciar
        document.addEventListener('DOMContentLoaded', loadItems);

        // Submit form
        document.getElementById('itemForm').addEventListener('submit', function(e) {
            e.preventDefault();
            saveItem();
        });

        async function loadItems() {
            try {
                const response = await fetch('/api/items');
                const data = await response.json();
                renderItems(data);
            } catch (error) {
                showToast('Erro ao carregar itens', 'error');
            }
        }

        function renderItems(items) {
            const tbody = document.getElementById('itemsBody');
            const emptyState = document.getElementById('emptyState');
            
            if (items.length === 0) {
                tbody.innerHTML = '';
                emptyState.style.display = 'block';
                updateTotals([]);
                return;
            }

            emptyState.style.display = 'none';
            tbody.innerHTML = items.map(item => `
                <tr class="${item.checked ? 'checked' : ''}" data-id="${item.id}">
                    <td>${item.id}</td>
                    <td><strong>${escapeHtml(item.name)}</strong></td>
                    <td>${formatNumber(item.quantity)}</td>
                    <td>${item.unit}</td>
                    <td>${item.price > 0 ? formatCurrency(item.price) : '-'}</td>
                    <td>${item.price > 0 ? formatCurrency(item.quantity * item.price) : '-'}</td>
                    <td>
                        <span class="status-badge ${item.checked ? 'status-completed' : 'status-pending'}">
                            ${item.checked ? '✅ Concluído' : '⏳ Pendente'}
                        </span>
                    </td>
                    <td>${formatDate(item.created_at)}</td>
                    <td>
                        <div class="action-btns">
                            <button class="action-btn edit" onclick="editItem(${item.id})" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn check" onclick="toggleCheck(${item.id})" title="Marcar/Desmarcar">
                                <i class="fas fa-${item.checked ? 'undo' : 'check'}"></i>
                            </button>
                            <button class="action-btn delete" onclick="deleteItem(${item.id})" title="Excluir">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');

            updateTotals(items);
        }

        function updateTotals(items) {
            const total = items
                .filter(item => !item.checked)
                .reduce((sum, item) => sum + (item.quantity * item.price), 0);
            
            const totalItems = items.length;
            const checkedItems = items.filter(item => item.checked).length;
            const pendingItems = totalItems - checkedItems;

            document.getElementById('totalValue').textContent = formatCurrency(total);
            document.getElementById('totalItems').textContent = totalItems;
            document.getElementById('checkedItems').textContent = checkedItems;
            document.getElementById('pendingItems').textContent = pendingItems;
        }

        async function saveItem() {
            const id = document.getElementById('itemId').value;
            const name = document.getElementById('itemName').value.trim();
            const quantity = parseFloat(document.getElementById('itemQuantity').value) || 1;
            const unit = document.getElementById('itemUnit').value;
            const price = parseFloat(document.getElementById('itemPrice').value) || 0;
            const notes = document.getElementById('itemNotes').value.trim();

            if (!name) {
                showToast('Nome do item é obrigatório!', 'warning');
                return;
            }

            const endpoint = id ? `/api/items/${id}` : '/api/items';
            const method = id ? 'PUT' : 'POST';

            try {
                const response = await fetch(endpoint, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, quantity, unit, price, notes })
                });

                if (response.ok) {
                    showToast(id ? 'Item atualizado!' : 'Item adicionado!', 'success');
                    clearForm();
                    loadItems();
                } else {
                    showToast('Erro ao salvar item', 'error');
                }
            } catch (error) {
                showToast('Erro de conexão', 'error');
            }
        }

        async function editItem(id) {
            try {
                const response = await fetch(`/api/items/${id}`);
                const item = await response.json();

                document.getElementById('itemId').value = item.id;
                document.getElementById('itemName').value = item.name;
                document.getElementById('itemQuantity').value = item.quantity;
                document.getElementById('itemUnit').value = item.unit;
                document.getElementById('itemPrice').value = item.price || '';
                document.getElementById('itemNotes').value = item.notes || '';

                document.getElementById('btnSubmit').innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                document.getElementById('btnCancel').style.display = 'inline-flex';
                
                editingId = id;
                
                // Scroll para o formulário
                document.querySelector('.card').scrollIntoView({ behavior: 'smooth' });
            } catch (error) {
                showToast('Erro ao carregar item', 'error');
            }
        }

        function cancelEdit() {
            clearForm();
        }

        function clearForm() {
            document.getElementById('itemId').value = '';
            document.getElementById('itemName').value = '';
            document.getElementById('itemQuantity').value = '1';
            document.getElementById('itemUnit').value = 'un';
            document.getElementById('itemPrice').value = '';
            document.getElementById('itemNotes').value = '';
            
            document.getElementById('btnSubmit').innerHTML = '<i class="fas fa-plus"></i> Adicionar Item';
            document.getElementById('btnCancel').style.display = 'none';
            
            editingId = null;
        }

        async function toggleCheck(id) {
            try {
                const response = await fetch(`/api/items/${id}/toggle`, {
                    method: 'PATCH'
                });

                if (response.ok) {
                    loadItems();
                }
            } catch (error) {
                showToast('Erro ao marcar item', 'error');
            }
        }

        async function deleteItem(id) {
            if (!confirm('Tem certeza que deseja excluir este item?')) {
                return;
            }

            try {
                const response = await fetch(`/api/items/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    showToast('Item excluído!', 'success');
                    if (editingId === id) {
                        clearForm();
                    }
                    loadItems();
                }
            } catch (error) {
                showToast('Erro ao excluir item', 'error');
            }
        }

        // Utility functions
        function formatCurrency(value) {
            return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        }

        function formatNumber(value) {
            return Number.isInteger(value) ? value : value.toFixed(2);
        }

        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);

            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db()
    cursor = conn.execute('''
        SELECT * FROM items 
        ORDER BY checked ASC, created_at DESC
    ''')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.json
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO items (name, quantity, unit, price, notes, checked, created_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
    ''', (
        data['name'],
        data.get('quantity', 1),
        data.get('unit', 'un'),
        data.get('price', 0),
        data.get('notes', ''),
        datetime.now().isoformat()
    ))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': item_id, 'message': 'Item criado!'}), 201

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    
    if item:
        return jsonify(dict(item))
    return jsonify({'error': 'Item não encontrado'}), 404

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE items 
        SET name=?, quantity=?, unit=?, price=?, notes=?, updated_at=?
        WHERE id=?
    ''', (
        data['name'],
        data.get('quantity', 1),
        data.get('unit', 'un'),
        data.get('price', 0),
        data.get('notes', ''),
        datetime.now().isoformat(),
        item_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item atualizado!'})

@app.route('/api/items/<int:item_id>/toggle', methods=['PATCH'])
def toggle_item(item_id):
    conn = get_db()
    cursor = conn.execute('SELECT checked FROM items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    
    if item:
        new_checked = 0 if item['checked'] else 1
        conn.execute('''
            UPDATE items SET checked=?, updated_at=? WHERE id=?
        ''', (new_checked, datetime.now().isoformat(), item_id))
        conn.commit()
    
    conn.close()
    return jsonify({'message': 'Status atualizado!'})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item excluído!'})

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("🛒 Lista de Compras Sofisticada")
    print("=" * 60)
    print("📍 Acesse no navegador: http://localhost:5000")
    print("💾 Banco de dados: shopping_list.db")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
