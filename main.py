from fastapi import FastAPI, HTTPException
import pyodbc

app = FastAPI(title="API Gestor", version="1.0")

# =========================================
# 🔥 CONEXÃO (IGUAL SUA MACRO)
# =========================================
def get_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=sistema.atdata.com.br,35987;"
            "UID=MasterLog;"
            "PWD=Master1252@#;"
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro conexão: {e}")


# =========================================
# 🔥 CONSULTA PADRÃO (SUA MACRO)
# =========================================
def consultar_estoque(cdprop):
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

    dados = []
    for row in cursor.fetchall():
        dados.append(dict(zip(colunas, row)))

    cursor.close()
    conn.close()

    return dados


# =========================================
# 🔥 ENDPOINTS INDIVIDUAIS (IGUAL VBA)
# =========================================

@app.get("/gestor/vidros")
def gestor_vidros():
    return consultar_estoque(323)


@app.get("/gestor/fabrica")
def gestor_fabrica():
    return consultar_estoque(7899)


@app.get("/gestor/cd")
def gestor_cd():
    return consultar_estoque(12035)


@app.get("/gestor/armazem")
def gestor_armazem():
    return consultar_estoque(12124)


# =========================================
# 🔥 ENDPOINT DINÂMICO (FLEXÍVEL)
# =========================================
@app.get("/gestor/{cdprop}")
def gestor_dinamico(cdprop: int):
    if cdprop not in [323, 7899, 12035, 12124]:
        raise HTTPException(
            status_code=400,
            detail="Código inválido"
        )

    return consultar_estoque(cdprop)


# =========================================
# 🔥 TODOS DE UMA VEZ
# =========================================
@app.get("/gestor")
def gestor_todos():
    return {
        "vidros": consultar_estoque(323),
        "fabrica": consultar_estoque(7899),
        "cd": consultar_estoque(12035),
        "armazem": consultar_estoque(12124),
    }


# =========================================
# 🔥 TESTE
# =========================================
@app.get("/")
def root():
    return {"status": "API Gestor rodando"}