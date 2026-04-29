from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pyodbc

app = FastAPI(title="API Gestor", version="1.0")

# =========================================
# 🔥 CORS (necessário pro Flutter Web)
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# 🔥 CONFIG CLIENTES
# =========================================
CLIENTES = {
    "vidros": 323,
    "fabrica": 7899,
    "cd": 12035,
    "armazem": 12124,
}

# =========================================
# 🔥 CONEXÃO SQL SERVER (RAILWAY)
# =========================================
def get_connection():
    try:
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=sistema.atdata.com.br,35987;"
            "UID=MasterLog;"
            "PWD=Master1252@#;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=5;"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro conexão: {str(e)}"
        )

# =========================================
# 🔥 CONSULTA PADRÃO
# =========================================
def consultar_estoque(cdprop: int):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            cdmaterialestoque,
            dsmaterialservico,
            SUM(qtENTRADA) AS ENTRADA,
            SUM(qtdesaldo) AS SALDO
        FROM vwr_posicaoestoque
        WHERE cdpropestoque = ?
        GROUP BY cdmaterialestoque, dsmaterialservico
        ORDER BY cdmaterialestoque
        """

        cursor.execute(query, (cdprop,))
        colunas = [col[0] for col in cursor.description]

        dados = [
            dict(zip(colunas, row))
            for row in cursor.fetchall()
        ]

        return {
            "cliente": cdprop,
            "total": len(dados),
            "dados": dados
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro consulta: {str(e)}"
        )

    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass

# =========================================
# 🔥 ENDPOINTS
# =========================================

@app.get("/")
def root():
    return {"status": "API Gestor rodando"}

# 🔹 endpoint padrão por nome
@app.get("/gestor/{cliente_nome}")
def gestor_por_nome(cliente_nome: str):
    if cliente_nome not in CLIENTES:
        raise HTTPException(
            status_code=400,
            detail="Cliente inválido"
        )

    return consultar_estoque(CLIENTES[cliente_nome])

# 🔹 endpoint por código (flexível)
@app.get("/gestor_codigo/{cdprop}")
def gestor_por_codigo(cdprop: int):
    if cdprop not in CLIENTES.values():
        raise HTTPException(
            status_code=400,
            detail="Código inválido"
        )

    return consultar_estoque(cdprop)

# 🔹 todos os clientes
@app.get("/gestor")
def gestor_todos():
    resultado = {}

    for nome, codigo in CLIENTES.items():
        try:
            resultado[nome] = consultar_estoque(codigo)
        except Exception as e:
            resultado[nome] = {"erro": str(e)}

    return resultado
