"""
Conexão base PostgreSQL
"""
import streamlit as st
import psycopg2
import psycopg2.extras
import urllib.parse

class BaseConnection:
    """Classe base para conexão PostgreSQL"""
    
    def __init__(self):
        # Construir connection string
        pg_config = st.secrets["connections"]["postgresql"]
        password_escaped = urllib.parse.quote_plus(pg_config['password'])
        self.conn_str = f"postgresql://{pg_config['username']}:{password_escaped}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
    
    def _execute_query(self, query, params=None, fetch=False):
        """Executa query simples"""
        try:
            with psycopg2.connect(self.conn_str) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(query, params)
                    if fetch:
                        return cur.fetchall()
                    conn.commit()
                    return True
        except Exception as e:
            return False if not fetch else []