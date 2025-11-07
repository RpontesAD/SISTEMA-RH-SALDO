#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar estrutura da planilha Excel
"""
import pandas as pd

def debug_excel():
    """Debug da planilha Excel"""
    
    excel_file = "DADOS COLABORADORES.xlsx"
    
    try:
        # Ler planilha
        print("Lendo planilha Excel...")
        df = pd.read_excel(excel_file, header=0)
        
        print(f"Shape: {df.shape}")
        print(f"Colunas originais: {list(df.columns)}")
        
        print("\nPrimeira linha (header):")
        print(df.iloc[0])
        
        print("\nSegunda linha (primeiro registro):")
        print(df.iloc[1])
        
        print("\nTerceira linha:")
        print(df.iloc[2])
        
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel()