#!/usr/bin/env python3
"""
Lista de Compras Sofisticada com SQLite
Funcionalidades: Adicionar, Editar, Check, Delete, Preço, Total, Data Automática
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ShoppingListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛒 Lista de Compras Sofisticada")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f5f5f5")
        
        # Configurar estilo
        self.setup_styles()
        
        # Inicializar banco de dados
        self.init_database()
        
        # Criar interface
        self.create_widgets()
        
        # Carregar dados
        self.load_data()
    
    def setup_styles(self):
        """Configura estilos modernos para a aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        # Configurar Treeview
        style.configure("Treeview", 
                       background="#ffffff",
                       foreground="#333333",
                       rowheight=35,
                       fieldbackground="#ffffff",
                       font=('Arial', 11))
        style.map("Treeview", background=[('selected', '#3498db')],
                  foreground=[('selected', '#ffffff')])
        
        style.configure("Treeview.Heading",
                       font=('Arial Bold', 12),
                       background='#2c3e50',
                       foreground='#ffffff',
                       padding=10)
        
        # Botões personalizados
        style.configure('Add.TButton', font=('Arial', 11, 'bold'), padding=10)
        style.configure('Edit.TButton', font=('Arial', 11), padding=10)
        style.configure('Delete.TButton', font=('Arial', 11), padding=10)
        style.configure('Check.TButton', font=('Arial', 11), padding=10)
    
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        self.conn = sqlite3.connect('shopping_list.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
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
        
        self.conn.commit()
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f5f5f5", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="🛒 Minha Lista de Compras", 
            font=("Arial", 24, "bold"),
            bg="#f5f5f5",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de entrada de dados
        input_frame = tk.LabelFrame(
            main_frame, 
            text="Adicionar/Editar Item", 
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            padx=20,
            pady=20
        )
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Variáveis de entrada
        self.name_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")
        self.unit_var = tk.StringVar(value="un")
        self.price_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self.editing_id = None
        
        # Grid de inputs
        labels = ["Nome do Item:", "Quantidade:", "Unidade:", "Preço (R$):", "Observações:"]
        vars = [self.name_var, self.quantity_var, self.unit_var, self.price_var, self.notes_var]
        
        for i, (label, var) in enumerate(zip(labels, vars)):
            tk.Label(input_frame, text=label, font=("Arial", 11), bg="#ffffff").grid(
                row=i//3, column=(i%3)*2, padx=10, pady=10, sticky="e"
            )
            
            if label == "Unidade:":
                combo = ttk.Combobox(input_frame, textvariable=var, width=15, 
                                   values=["un", "kg", "g", "L", "mL", "pct", "dz"])
                combo.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=10)
            else:
                entry = tk.Entry(input_frame, textvariable=var, width=20, font=("Arial", 11))
                entry.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=10)
        
        # Frame de botões
        button_frame = tk.Frame(input_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=6, pady=20)
        
        self.btn_add = tk.Button(
            button_frame, text="➕ Adicionar", command=self.add_or_save,
            bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
            padx=20, pady=10, relief=tk.FLAT, cursor="hand2"
        )
        self.btn_add.pack(side=tk.LEFT, padx=5)
        
        self.btn_edit = tk.Button(
            button_frame, text="✏️ Editar", command=self.edit_item,
            bg="#3498db", fg="white", font=("Arial", 11),
            padx=20, pady=10, relief=tk.FLAT, cursor="hand2", state=tk.DISABLED
        )
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        
        self.btn_check = tk.Button(
            button_frame, text="✅ Marcar/Desmarcar", command=self.toggle_check,
            bg="#f39c12", fg="white", font=("Arial", 11),
            padx=20, pady=10, relief=tk.FLAT, cursor="hand2", state=tk.DISABLED
        )
        self.btn_check.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete = tk.Button(
            button_frame, text="🗑️ Excluir", command=self.delete_item,
            bg="#e74c3c", fg="white", font=("Arial", 11),
            padx=20, pady=10, relief=tk.FLAT, cursor="hand2", state=tk.DISABLED
        )
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = tk.Button(
            button_frame, text="🧹 Limpar Campos", command=self.clear_fields,
            bg="#95a5a6", fg="white", font=("Arial", 11),
            padx=20, pady=10, relief=tk.FLAT, cursor="hand2"
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        # Frame da tabela
        table_frame = tk.Frame(main_frame, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Treeview com scrollbars
        columns = ("ID", "Item", "Qtd", "Unid", "Preço Unit", "Subtotal", "Status", "Data Inclusão", "Observações")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configurar colunas
        column_widths = [50, 250, 60, 60, 100, 100, 80, 150, 200]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind de seleção
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', lambda e: self.edit_item())
        
        # Frame do total
        total_frame = tk.Frame(main_frame, bg="#2c3e50", padx=20, pady=15)
        total_frame.pack(fill=tk.X)
        
        self.total_label = tk.Label(
            total_frame, 
            text="Total: R$ 0,00", 
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="#27ae60"
        )
        self.total_label.pack(side=tk.RIGHT)
        
        tk.Label(
            total_frame, 
            text="💰 Valor Total da Lista:", 
            font=("Arial", 16),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack(side=tk.LEFT)
        
        # Stats frame
        stats_frame = tk.Frame(main_frame, bg="#f5f5f5")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.items_count_label = tk.Label(
            stats_frame, 
            text="Itens: 0 | Marcados: 0 | Pendentes: 0", 
            font=("Arial", 11),
            bg="#f5f5f5",
            fg="#7f8c8d"
        )
        self.items_count_label.pack(side=tk.LEFT)
    
    def load_data(self):
        """Carrega os dados do banco na tabela"""
        # Limpar tabela atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar dados
        self.cursor.execute('''
            SELECT id, name, quantity, unit, price, checked, notes, created_at 
            FROM items 
            ORDER BY checked ASC, created_at DESC
        ''')
        
        rows = self.cursor.fetchall()
        total = 0
        items_count = 0
        checked_count = 0
        
        for row in rows:
            item_id, name, qty, unit, price, checked, notes, created_at = row
            
            # Formatar data
            try:
                date_obj = datetime.fromisoformat(created_at)
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_date = created_at
            
            # Calcular subtotal
            subtotal = qty * price if price else 0
            if not checked:  # Só soma itens não marcados
                total += subtotal
            
            items_count += 1
            if checked:
                checked_count += 1
            
            # Status visual
            status = "✅" if checked else "⏳"
            
            # Inserir na tabela
            values = (
                item_id,
                name,
                f"{qty:.2f}" if qty != int(qty) else str(int(qty)),
                unit,
                f"R$ {price:.2f}" if price else "-",
                f"R$ {subtotal:.2f}",
                status,
                formatted_date,
                notes or "-"
            )
            
            # Cor diferente para itens marcados
            tag = "checked" if checked else "unchecked"
            self.tree.insert("", tk.END, values=values, tags=(tag,))
        
        # Configurar tags de cor
        self.tree.tag_configure("checked", background="#d5f5e3")
        self.tree.tag_configure("unchecked", background="#ffffff")
        
        # Atualizar total
        self.total_label.config(text=f"Total: R$ {total:.2f}")
        
        # Atualizar stats
        pending = items_count - checked_count
        self.items_count_label.config(
            text=f"Itens: {items_count} | ✅ Marcados: {checked_count} | ⏳ Pendentes: {pending}"
        )
    
    def add_or_save(self):
        """Adiciona novo item ou salva edição"""
        if self.editing_id is not None:
            self.save_edit()
        else:
            self.add_item()
    
    def add_item(self):
        """Adiciona um novo item"""
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showwarning("Atenção", "Por favor, digite o nome do item!")
            return
        
        try:
            quantity = float(self.quantity_var.get().replace(',', '.') or 1)
            price = float(self.price_var.get().replace(',', '.') or 0)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos!")
            return
        
        unit = self.unit_var.get()
        notes = self.notes_var.get().strip()
        
        # Inserir no banco
        self.cursor.execute('''
            INSERT INTO items (name, quantity, unit, price, notes, checked, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        ''', (name, quantity, unit, price, notes, datetime.now().isoformat()))
        
        self.conn.commit()
        
        # Limpar campos e recarregar
        self.clear_fields()
        self.load_data()
        
        messagebox.showinfo("Sucesso", f"Item '{name}' adicionado com sucesso!")
    
    def edit_item(self):
        """Edita um item selecionado"""
        selected = self.tree.selection()
        
        if not selected and self.editing_id is None:
            messagebox.showwarning("Atenção", "Selecione um item para editar!")
            return
        
        if self.editing_id is None:
            # Pegar ID do item selecionado
            item_values = self.tree.item(selected[0])['values']
            self.editing_id = item_values[0]
            
            # Preencher campos com dados atuais
            self.name_var.set(item_values[1])
            self.quantity_var.set(str(item_values[2]).replace('.', ','))
            self.unit_var.set(item_values[3])
            
            price_str = str(item_values[4])
            if price_str != "-":
                self.price_var.set(price_str.replace('R$ ', '').replace('.', ','))
            else:
                self.price_var.set("")
        
        # Atualizar botão
        self.btn_add.config(text="💾 Salvar Alterações", bg="#27ae60")
        self.btn_edit.config(state=tk.DISABLED)
        self.btn_check.config(state=tk.DISABLED)
        self.btn_delete.config(state=tk.DISABLED)
    
    def save_edit(self):
        """Salva as alterações do item"""
        if self.editing_id is None:
            return
        
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showwarning("Atenção", "Nome do item é obrigatório!")
            return
        
        try:
            quantity = float(self.quantity_var.get().replace(',', '.') or 1)
            price = float(self.price_var.get().replace(',', '.') or 0)
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos!")
            return
        
        unit = self.unit_var.get()
        notes = self.notes_var.get().strip()
        
        # Atualizar no banco
        self.cursor.execute('''
            UPDATE items 
            SET name=?, quantity=?, unit=?, price=?, notes=?, updated_at=?
            WHERE id=?
        ''', (name, quantity, unit, price, notes, datetime.now().isoformat(), self.editing_id))
        
        self.conn.commit()
        
        # Resetar estado
        self.editing_id = None
        self.clear_fields()
        self.load_data()
        
        self.btn_add.config(text="➕ Adicionar", bg="#27ae60")
        self.btn_edit.config(state=tk.NORMAL)
        self.btn_check.config(state=tk.NORMAL)
        self.btn_delete.config(state=tk.NORMAL)
        
        messagebox.showinfo("Sucesso", "Item atualizado com sucesso!")
    
    def toggle_check(self):
        """Marca/desmarca um item"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item para marcar/desmarcar!")
            return
        
        item_values = self.tree.item(selected[0])['values']
        item_id = item_values[0]
        current_status = 1 if item_values[6] == "✅" else 0
        new_status = 0 if current_status else 1
        
        # Atualizar no banco
        self.cursor.execute('''
            UPDATE items SET checked=?, updated_at=? WHERE id=?
        ''', (new_status, datetime.now().isoformat(), item_id))
        
        self.conn.commit()
        self.load_data()
    
    def delete_item(self):
        """Exclui um item"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item para excluir!")
            return
        
        item_values = self.tree.item(selected[0])['values']
        item_name = item_values[1]
        
        confirm = messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Deseja realmente excluir o item '{item_name}'?"
        )
        
        if confirm:
            item_id = item_values[0]
            self.cursor.execute('DELETE FROM items WHERE id=?', (item_id,))
            self.conn.commit()
            
            self.clear_fields()
            self.load_data()
            
            messagebox.showinfo("Sucesso", f"Item '{item_name}' excluído!")
    
    def on_select(self, event):
        """Handle selection event"""
        selected = self.tree.selection()
        
        if selected:
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_check.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
        else:
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_check.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)
    
    def clear_fields(self):
        """Limpa todos os campos de entrada"""
        self.name_var.set("")
        self.quantity_var.set("1")
        self.unit_var.set("un")
        self.price_var.set("")
        self.notes_var.set("")
        self.editing_id = None
        
        # Resetar botão de adicionar
        self.btn_add.config(text="➕ Adicionar", bg="#27ae60")
        self.btn_edit.config(state=tk.NORMAL)
        self.btn_check.config(state=tk.NORMAL)
        self.btn_delete.config(state=tk.NORMAL)
    
    def __del__(self):
        """Fechar conexão ao destruir"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    root = tk.Tk()
    app = ShoppingListApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
