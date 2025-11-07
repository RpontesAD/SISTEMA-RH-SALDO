#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar leitura da planilha Excel
"""
import pandas as pd
import os

def test_excel():
    """Testa leitura da planilha Excel"""
    
    excel_file = "DADOS COLABORADORES.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"ERRO: Arquivo {excel_file} nao encontrado!")
        return
    
    try:
        # Ler planilha
        print("Lendo planilha Excel...")
        df = pd.read_excel(excel_file)
        
        print(f"Encontrados {len(df)} registros na planilha")
        print(f"Colunas: {list(df.columns)}")
        print("\nPrimeiras 5 linhas:")
        print(df.head())
        
        print("\nTipos de dados:")
        print(df.dtypes)
        
        print("\nInformacoes gerais:")
        print(df.info())
        
    except Exception as e:
        print(f"ERRO ao processar planilha: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel()