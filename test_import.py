#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar importação sem conectar ao banco
"""
import pandas as pd
from datetime import date

def test_import():
    """Testa importação sem banco"""
    
    excel_file = "DADOS COLABORADORES.xlsx"
    
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
        
        sucessos = 0
        erros = 0
        
        # Processar cada linha
        for index, row in df.iterrows():
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
                    print(f"AVISO: Linha {index+1}: Nome ou email vazio - pulando")
                    continue
                
                print(f"OK: {nome} | {email} | {setor} | {funcao} | Saldo: {saldo_ferias}")
                sucessos += 1
                    
            except Exception as e:
                print(f"ERRO na linha {index+1}: {str(e)}")
                erros += 1
        
        # Resumo final
        print(f"\nRESUMO DO TESTE:")
        print(f"Sucessos: {sucessos}")
        print(f"Erros: {erros}")
        print(f"Total processado: {sucessos + erros}")
        
    except Exception as e:
        print(f"ERRO ao processar planilha: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import()