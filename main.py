from fastapi import FastAPI, HTTPException, status
from models import Livro, Usuario, Emprestimo, Devolucao, Log
from typing import List
from datetime import datetime

app = FastAPI()

livros: List[Livro] = [] 
usuarios: List[Usuario] = []
emprestimos: List[Emprestimo] = []
logs: List[Log] = []

### LIVROS 

# Listar livros
@app.get("/livros", response_model=List[Livro])
def listar_livros():
    return livros 

# Obter livro pelo título
@app.get("/livros/{titulo}", response_model=Livro)
def obter_livro(titulo: str):
    for livro in livros:
        if livro.titulo == titulo:
            return livro
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Livro não encontrado."
    )

# Cadastrar livro
@app.post("/livros", response_model=Livro, status_code=status.HTTP_201_CREATED)
def criar_livro(livro: Livro):
    for l in livros:
        if l.id == livro.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID já existe."
            )
    livros.append(livro)

    logs.append(Log(
        tipo="cadastro_livro",
        id_usuario=None,
        id_livro=livro.id,
        timestamp=datetime.now(),
        descricao=f"Livro '{livro.titulo}' cadastrado com ID {livro.id}"
    ))

    return livro

### USUÁRIOS

# Listar usuários
@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():
    return usuarios 

# Cadastrar usuário 
@app.post("/usuarios", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: Usuario):
    for u in usuarios:
        if u.id == usuario.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID já existe."
            )
    usuarios.append(usuario)

    logs.append(Log(
        tipo="cadastro_usuario",
        id_usuario=usuario.id,
        id_livro=None,
        timestamp=datetime.now(),
        descricao=f"Usuário '{usuario.nome}' cadastrado com ID {usuario.id}"
    ))

    return usuario

### REALIZAR EMPRÉSTIMO

# Listar empréstimos realizados
@app.get("/emprestimos", response_model=List[Emprestimo])
def listar_emprestimos():
    return emprestimos

# Emprestar livro (UUID do usuário, UUID do livro e data do empréstimo)
@app.post("/emprestimos", response_model=Emprestimo, status_code=status.HTTP_201_CREATED)
def criar_emprestimo(emprestimo: Emprestimo):
    livro = None
    usuario = None
    
    for l in livros:
        if l.id == emprestimo.id_livro:
            livro = l
            break

    for u in usuarios:
        if u.id == emprestimo.id_usuario:
            usuario = u
            break

    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if not livro.disponibilidade:
        raise HTTPException(status_code=400, detail="Livro indisponível.")

    livro.disponibilidade = False
    usuario.livros_emprestados.append(livro.id)
    emprestimos.append(emprestimo)
    
    print(f"[EMPRÉSTIMO] Livro ID {emprestimo.id_livro} emprestado para Usuário ID {emprestimo.id_usuario} em {emprestimo.data_emprestimo}")

    logs.append(Log(
    tipo="empréstimo",
    id_usuario=emprestimo.id_usuario,
    id_livro=emprestimo.id_livro,
    timestamp=datetime.now(),
    descricao=f"Livro ID {emprestimo.id_livro} emprestado para usuário ID {emprestimo.id_usuario}"
))

    return emprestimo

# Devolver livro (UUUID do usuário, UUUID do livro e data da devolução)
@app.put("/emprestimos/devolver")
def devolver_livro(devolucao: Devolucao):
    livro = None
    usuario = None
    emprestimo = None
    
    for l in livros:
        if l.id == devolucao.id_livro:
            livro = l
            break

    for u in usuarios:
        if u.id == devolucao.id_usuario:
            usuario = u
            break

    for e in emprestimos:
        if e.id_livro == devolucao.id_livro and e.id_usuario == devolucao.id_usuario:
            emprestimo = e
            break


    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    if livro.disponibilidade:
        raise HTTPException(status_code=400, detail="O livro já está disponível.")

    livro.disponibilidade = True
    if devolucao.id_livro in usuario.livros_emprestados:
        usuario.livros_emprestados.remove(devolucao.id_livro)

    print(f"[DEVOLUÇÃO] Livro ID {devolucao.id_livro} devolvido por Usuário ID {devolucao.id_usuario} em {devolucao.data_devolucao}")

    logs.append(Log(
    tipo="devolução",
    id_usuario=devolucao.id_usuario,
    id_livro=devolucao.id_livro,
    timestamp=datetime.now(),
    descricao=f"Livro ID {devolucao.id_livro} devolvido por usuário ID {devolucao.id_usuario}"
))

    return {"mensagem": "Livro devolvido com sucesso."}

# Listar todos os livros atualmente emprestados por um usuário, identificado pelo seu UUID 
@app.get("/usuarios/{id_usuario}/livros-emprestados", response_model=List[Livro])
def listar_livros_emprestados(id_usuario: int):
    livros_emprestados = []

    usuario = None
    for u in usuarios:
        if u.id == id_usuario:
            usuario = u
            break

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    for livro in livros:
        if livro.id in usuario.livros_emprestados:
            livros_emprestados.append(livro)

    return livros_emprestados

# Logs
@app.get("/logs", response_model=List[Log])
def listar_logs():
    return logs