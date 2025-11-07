#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar colaboradores da planilha Excel para o banco de dados
"""
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import date

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from database.simple_psycopg2 import SimplePsycopg2

def main():
    """Importa colaboradores da planilha Excel"""
    
    # Caminho da planilha
    excel_file = "DADOS COLABORADORES.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"ERRO: Arquivo {excel_file} nao encontrado!")
        return
    
    try:
        # Ler planilha
        print("Lendo planilha Excel...")
        df = pd.read_excel(excel_file)
        
        # Renomear colunas baseado na estrutura real
        df.columns = [
            'nome', 'email', 'senha', 'confirmar_senha', 'data_admissao', 
            'setor', 'funcao', 'saldo_ferias', 'nivel_acesso'
        ]
        
        # Remover primeira linha que contem os headers
        df = df.drop(0).reset_index(drop=True)
        
        print(f"Encontrados {len(df)} colaboradores na planilha")
        print(f"Colunas: {list(df.columns)}")
        
        # Inicializar banco
        print("Conectando ao banco...")
        try:
            db = SimplePsycopg2()
            print("Conexao estabelecida!")
        except Exception as e:
            print(f"ERRO ao conectar: {e}")
            return
        
        sucessos = 0
        erros = 0
        
        # Processar cada linha
        for index, row in df.iterrows():
            print(f"Processando linha {index+1}/{len(df)}...", end=" ")
            try:
                # Extrair dados da linha
                nome = str(row['nome']).strip()
                email = str(row['email']).strip().lower()
                senha = str(row['senha']).strip() if pd.notna(row['senha']) else 'temp123'
                setor = str(row['setor']).strip().upper()
                funcao = str(row['funcao']).strip()
                nivel_acesso = str(row['nivel_acesso']).strip().lower() if pd.notna(row['nivel_acesso']) else 'colaborador'
                saldo_ferias = int(row['saldo_ferias']) if pd.notna(row['saldo_ferias']) else 12
                
                # Validacoes basicas
                if not nome or nome == 'nan' or not email or email == 'nan':
                    print(f"PULADO - Nome ou email vazio")
                    continue
                
                print(f"Cadastrando {nome}...", end=" ")
                
                # Tentar cadastrar usando metodo direto do banco
                success = db.create_user(
                    nome=nome,
                    email=email,
                    senha=senha,
                    setor=setor,
                    funcao=funcao,
                    nivel_acesso=nivel_acesso,
                    saldo_ferias=saldo_ferias,
                    data_admissao=date.today()
                )
                
                if success:
                    print("OK")
                    sucessos += 1
                else:
                    print("ERRO - Email ja existe")
                    erros += 1
                    
            except Exception as e:
                print(f"ERRO - {str(e)}")
                erros += 1
        
        # Resumo final
        print(f"\nRESUMO DA IMPORTACAO:")
        print(f"Sucessos: {sucessos}")
        print(f"Erros: {erros}")
        print(f"Total processado: {sucessos + erros}")
        
    except Exception as e:
        print(f"ERRO ao processar planilha: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()