# app.py
from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/img'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utils para CSV
PROJETOS_CSV = 'projetos.csv'
TAREFAS_CSV = 'tarefas.csv'

CAMPOS_PROJETO = ['id', 'nome', 'descricao', 'data_criacao', 'imagem']
CAMPOS_TAREFA = ['id', 'id_projeto', 'titulo', 'descricao', 'status']

# Funções auxiliares

def ler_csv(caminho, campos):
    if not os.path.exists(caminho):
        with open(caminho, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
    with open(caminho, newline='') as f:
        return list(csv.DictReader(f))

def salvar_csv(caminho, dados, campos):
    with open(caminho, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)

def gerar_id(lista):
    return str(max([int(i['id']) for i in lista], default=0) + 1)

# Rotas
@app.route('/')
def index():
    projetos = ler_csv(PROJETOS_CSV, CAMPOS_PROJETO)
    return render_template('index.html', projetos=projetos)

@app.route('/projeto/<id>')
def ver_projeto(id):
    projetos = ler_csv(PROJETOS_CSV, CAMPOS_PROJETO)
    tarefas = ler_csv(TAREFAS_CSV, CAMPOS_TAREFA)
    projeto = next((p for p in projetos if p['id'] == id), None)
    tarefas_projeto = [t for t in tarefas if t['id_projeto'] == id]
    return render_template('projeto.html', projeto=projeto, tarefas=tarefas_projeto)

@app.route('/criar_projeto', methods=['GET', 'POST'])
def criar_projeto():
    if request.method == 'POST':
        projetos = ler_csv(PROJETOS_CSV, CAMPOS_PROJETO)
        id_proj = gerar_id(projetos)
        imagem = request.files.get('imagem')
        nome_arquivo = f"{id_proj}_{imagem.filename}" if imagem else ''
        if imagem:
            imagem.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))
        projeto = {
            'id': id_proj,
            'nome': request.form['nome'],
            'descricao': request.form['descricao'],
            'data_criacao': datetime.today().strftime('%Y-%m-%d'),
            'imagem': nome_arquivo
        }
        projetos.append(projeto)
        salvar_csv(PROJETOS_CSV, projetos, CAMPOS_PROJETO)
        return redirect(url_for('index'))
    return render_template('criar_projeto.html')

@app.route('/editar_projeto/<id>', methods=['GET', 'POST'])
def editar_projeto(id):
    projetos = ler_csv(PROJETOS_CSV, CAMPOS_PROJETO)
    projeto = next((p for p in projetos if p['id'] == id), None)
    if request.method == 'POST':
        projeto['nome'] = request.form['nome']
        projeto['descricao'] = request.form['descricao']
        salvar_csv(PROJETOS_CSV, projetos, CAMPOS_PROJETO)
        return redirect(url_for('index'))
    return render_template('editar_projeto.html', projeto=projeto)

@app.route('/remover_projeto/<id>')
def remover_projeto(id):
    projetos = ler_csv(PROJETOS_CSV, CAMPOS_PROJETO)
    tarefas = ler_csv(TAREFAS_CSV, CAMPOS_TAREFA)
    projetos = [p for p in projetos if p['id'] != id]
    tarefas = [t for t in tarefas if t['id_projeto'] != id]
    salvar_csv(PROJETOS_CSV, projetos, CAMPOS_PROJETO)
    salvar_csv(TAREFAS_CSV, tarefas, CAMPOS_TAREFA)
    return redirect(url_for('index'))

@app.route('/adicionar_tarefa/<id_projeto>', methods=['POST'])
def adicionar_tarefa(id_projeto):
    tarefas = ler_csv(TAREFAS_CSV, CAMPOS_TAREFA)
    id_tarefa = gerar_id(tarefas)
    tarefa = {
        'id': id_tarefa,
        'id_projeto': id_projeto,
        'titulo': request.form['titulo'],
        'descricao': request.form['descricao'],
        'status': request.form['status']
    }
    tarefas.append(tarefa)
    salvar_csv(TAREFAS_CSV, tarefas, CAMPOS_TAREFA)
    return redirect(url_for('ver_projeto', id=id_projeto))

@app.route('/editar_tarefa/<id>', methods=['GET', 'POST'])
def editar_tarefa(id):
    tarefas = ler_csv(TAREFAS_CSV, CAMPOS_TAREFA)
    tarefa = next((t for t in tarefas if t['id'] == id), None)
    if request.method == 'POST':
        tarefa['titulo'] = request.form['titulo']
        tarefa['descricao'] = request.form['descricao']
        tarefa['status'] = request.form['status']
        salvar_csv(TAREFAS_CSV, tarefas, CAMPOS_TAREFA)
        return redirect(url_for('ver_projeto', id=tarefa['id_projeto']))
    return render_template('editar_tarefa.html', tarefa=tarefa)

@app.route('/remover_tarefa/<id>')
def remover_tarefa(id):
    tarefas = ler_csv(TAREFAS_CSV, CAMPOS_TAREFA)
    tarefa = next((t for t in tarefas if t['id'] == id), None)
    if tarefa:
        tarefas = [t for t in tarefas if t['id'] != id]
        salvar_csv(TAREFAS_CSV, tarefas, CAMPOS_TAREFA)
        return redirect(url_for('ver_projeto', id=tarefa['id_projeto']))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
