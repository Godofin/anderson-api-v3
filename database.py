"""
Configuração do banco de dados Neon Postgres
"""
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Cria conexão com Neon"""
    try:
        import pg8000.native
        
        database_url = os.getenv("POSTGRES_URL")
        if not database_url:
            raise ValueError("POSTGRES_URL não encontrada")
        
        parsed = urlparse(database_url)
        
        conn = pg8000.native.Connection(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            ssl_context=True
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        raise


def execute_query(query: str, params: tuple = None, fetch: str = "all"):
    """Executa query convertendo placeholders"""
    conn = None
    try:
        conn = get_connection()
        
        # Converte %s para formato pg8000 (:1, :2, etc)
        if params:
            converted_query = query
            param_dict = {}
            for i, param in enumerate(params, 1):
                placeholder = f":{i}"
                converted_query = converted_query.replace('%s', placeholder, 1)
                param_dict[str(i)] = param
            
            result = conn.run(converted_query, **param_dict)
        else:
            result = conn.run(query)
        
        # Processa resultados
        if fetch == "all":
            if not result:
                return []
            columns = [desc[0] for desc in conn.columns]
            return [dict(zip(columns, row)) for row in result]
        elif fetch == "one":
            if result:
                columns = [desc[0] for desc in conn.columns]
                return dict(zip(columns, result[0]))
            return None
        else:
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        raise
    finally:
        if conn:
            conn.close()