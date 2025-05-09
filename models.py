from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Livro(BaseModel):
    id: int 
    titulo: str
    autor: str
    ano: int  
    disponibilidade: bool 

class Usuario(BaseModel):
    id: int 
    nome: str 
    livros_emprestados: list

class Emprestimo(BaseModel):
    data_emprestimo: datetime
    id_livro: int 
    id_usuario: int

class Devolucao(BaseModel):
    id_usuario: int
    id_livro: int
    data_devolucao: datetime

class Log(BaseModel):
    tipo: str  # "empréstimo", "devolução", "cadastro_livro", "cadastro_usuario"
    id_usuario: Optional[int]
    id_livro: Optional[int]
    timestamp: datetime
    descricao: str