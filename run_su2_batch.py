"""
Script para executar SU2 automaticamente para múltiplas malhas
Autor: Script automatizado
Data: 2025
"""

import os
import subprocess
import shutil
import glob
from pathlib import Path

# Configurações
# SU2_PATH = r"C:\Users\ymarc\OneDrive\Documents\SU2-v8.3.0-win64\win64\bin\SU2_CFD.exe"
SU2_PATH = r"C:\Users\ymarc\OneDrive\Documents\SU2-v8.3.0-win64-mpi\win64-mpi\bin\SU2_CFD.exe"
CONFIG_FILE = "lam_flatplate.cfg"
CONFIG_BACKUP = "lam_flatplate.cfg.backup"

def get_mesh_files():
    """Retorna lista de arquivos de malha a serem processados"""
    # Busca todas as malhas mesh_*.su2 (excluindo mesh.su2 e mesh_out.su2)
    mesh_files = glob.glob("mesh_d*.su2")
    mesh_files.sort()  # Ordena alfabeticamente
    return mesh_files

def backup_config():
    """Faz backup do arquivo de configuração original"""
    if os.path.exists(CONFIG_FILE):
        shutil.copy2(CONFIG_FILE, CONFIG_BACKUP)
        print(f"✓ Backup do arquivo de configuração criado: {CONFIG_BACKUP}")

def restore_config():
    """Restaura o arquivo de configuração original"""
    if os.path.exists(CONFIG_BACKUP):
        shutil.copy2(CONFIG_BACKUP, CONFIG_FILE)
        os.remove(CONFIG_BACKUP)
        print(f"✓ Arquivo de configuração restaurado")

def modify_config(mesh_filename):
    """Modifica o arquivo de configuração para usar a malha especificada"""
    with open(CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    
    # Modifica a linha MESH_FILENAME
    with open(CONFIG_FILE, 'w') as f:
        for line in lines:
            if line.strip().startswith('MESH_FILENAME='):
                f.write(f'MESH_FILENAME= {mesh_filename}\n')
            else:
                f.write(line)
    
    print(f"✓ Configuração modificada para usar malha: {mesh_filename}")

def run_su2():
    """Executa o SU2_CFD"""
    print(f"\n{'='*60}")
    print(f"Executando SU2...")
    print(f"{'='*60}\n")
    
    try:
        # Executa o SU2
        result = subprocess.run(
            [SU2_PATH, CONFIG_FILE],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✓ SU2 executado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Erro ao executar SU2!")
        print(f"Código de erro: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n✗ Erro: SU2_CFD.exe não encontrado em:")
        print(f"  {SU2_PATH}")
        print(f"\nVerifique se o caminho está correto.")
        return False

def rename_outputs(mesh_name):
    """Renomeia os arquivos de saída com o nome da malha"""
    # Extrai o identificador da malha (ex: d002_H03)
    mesh_id = mesh_name.replace('mesh_', '').replace('.su2', '')
    
    # Lista de arquivos de saída a serem renomeados
    output_files = {
        'flow.vtu': f'flow_{mesh_id}.vtu',
        'surface_flow.vtu': f'surface_flow_{mesh_id}.vtu',
        'history.csv': f'history_{mesh_id}.csv',
        'restart_flow.dat': f'restart_flow_{mesh_id}.dat'
    }
    
    print(f"\nRenomeando arquivos de saída...")
    for old_name, new_name in output_files.items():
        if os.path.exists(old_name):
            # Se o arquivo destino já existe, remove
            if os.path.exists(new_name):
                os.remove(new_name)
            shutil.move(old_name, new_name)
            print(f"  {old_name} → {new_name}")
        else:
            print(f"  ⚠ Arquivo não encontrado: {old_name}")

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("Script de Execução Automatizada do SU2")
    print("="*60 + "\n")
    
    # Verifica se o SU2 existe
    if not os.path.exists(SU2_PATH):
        print(f"✗ ERRO: SU2_CFD.exe não encontrado!")
        print(f"  Caminho: {SU2_PATH}")
        return
    
    # Verifica se o arquivo de configuração existe
    if not os.path.exists(CONFIG_FILE):
        print(f"✗ ERRO: Arquivo de configuração não encontrado!")
        print(f"  Arquivo: {CONFIG_FILE}")
        return
    
    # Obtém lista de malhas
    mesh_files = get_mesh_files()
    
    if not mesh_files:
        print("✗ Nenhuma malha encontrada no padrão 'mesh_d*.su2'")
        return
    
    print(f"Malhas encontradas: {len(mesh_files)}")
    for i, mesh in enumerate(mesh_files, 1):
        print(f"  {i}. {mesh}")
    
    # Confirmação do usuário
    print(f"\n{'='*60}")
    response = input("Deseja processar todas essas malhas? (s/n): ")
    if response.lower() != 's':
        print("Operação cancelada pelo usuário.")
        return
    
    # Faz backup do arquivo de configuração
    backup_config()
    
    # Processa cada malha
    success_count = 0
    fail_count = 0
    
    try:
        for i, mesh_file in enumerate(mesh_files, 1):
            print(f"\n\n{'#'*60}")
            print(f"# Processando malha {i}/{len(mesh_files)}: {mesh_file}")
            print(f"{'#'*60}\n")
            
            # Modifica configuração
            modify_config(mesh_file)
            
            # Executa SU2
            success = run_su2()
            
            if success:
                # Renomeia outputs
                rename_outputs(mesh_file)
                success_count += 1
            else:
                fail_count += 1
                print(f"\n⚠ Falha ao processar {mesh_file}")
                response = input("Deseja continuar com as próximas malhas? (s/n): ")
                if response.lower() != 's':
                    break
        
    finally:
        # Sempre restaura o arquivo de configuração original
        restore_config()
    
    # Relatório final
    print(f"\n\n{'='*60}")
    print(f"RELATÓRIO FINAL")
    print(f"{'='*60}")
    print(f"Total de malhas processadas: {success_count + fail_count}")
    print(f"  ✓ Sucesso: {success_count}")
    print(f"  ✗ Falhas: {fail_count}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

