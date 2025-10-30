"""
Script para executar SU2 automaticamente para múltiplas malhas
Autor: Script automatizado
Data: 2025
Versão: Paralela com multiprocessing
"""

import os
import subprocess
import shutil
import glob
from pathlib import Path
from multiprocessing import Pool, cpu_count
import time

# Configurações
# SU2_PATH = r"C:\Users\ymarc\OneDrive\Documents\SU2-v8.3.0-win64\win64\bin\SU2_CFD.exe"
SU2_PATH = r"C:\Users\ymarc\OneDrive\Documents\SU2-v8.3.0-win64-mpi\win64-mpi\bin\SU2_CFD.exe"
CONFIG_FILE = "lam_flatplate.cfg"

def get_mesh_files():
    """Retorna lista de arquivos de malha a serem processados"""
    # Busca todas as malhas mesh_*.su2 (excluindo mesh.su2 e mesh_out.su2)
    mesh_files = glob.glob("mesh_d*.su2")
    mesh_files.sort()  # Ordena alfabeticamente
    return mesh_files

def create_config_for_mesh(mesh_filename, mesh_id):
    """Cria um arquivo de configuração específico para cada malha"""
    config_temp = f"lam_flatplate_{mesh_id}.cfg"
    
    with open(CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    
    # Modifica as linhas necessárias para evitar conflitos entre processos paralelos
    with open(config_temp, 'w') as f:
        for line in lines:
            if line.strip().startswith('MESH_FILENAME='):
                f.write(f'MESH_FILENAME= {mesh_filename}\n')
            elif line.strip().startswith('CONV_FILENAME='):
                f.write(f'CONV_FILENAME= history_{mesh_id}\n')
            elif line.strip().startswith('RESTART_FILENAME='):
                f.write(f'RESTART_FILENAME= restart_flow_{mesh_id}.dat\n')
            elif line.strip().startswith('VOLUME_FILENAME='):
                f.write(f'VOLUME_FILENAME= flow_{mesh_id}\n')
            elif line.strip().startswith('SURFACE_FILENAME='):
                f.write(f'SURFACE_FILENAME= surface_flow_{mesh_id}\n')
            else:
                f.write(line)
    
    return config_temp

def process_single_mesh(mesh_file):
    """Processa uma única malha (função para ser executada em paralelo)"""
    mesh_id = mesh_file.replace('mesh_', '').replace('.su2', '')
    
    print(f"\n[{mesh_id}] Iniciando processamento...")
    start_time = time.time()
    
    try:
        # Cria arquivo de configuração específico para esta malha
        config_temp = create_config_for_mesh(mesh_file, mesh_id)
        print(f"[{mesh_id}] Arquivo de configuração criado: {config_temp}")
        
        # Executa o SU2
        print(f"[{mesh_id}] Executando SU2_CFD...")
        result = subprocess.run(
            [SU2_PATH, config_temp],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Remove arquivo de configuração temporário
        if os.path.exists(config_temp):
            os.remove(config_temp)
        
        elapsed_time = time.time() - start_time
        print(f"[{mesh_id}] ✓ Concluído em {elapsed_time:.1f}s")
        
        return {
            'mesh': mesh_file,
            'success': True,
            'time': elapsed_time,
            'message': 'Sucesso'
        }
        
    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Erro código {e.returncode}"
        print(f"[{mesh_id}] ✗ {error_msg}")
        
        # Remove arquivo de configuração temporário em caso de erro
        config_temp = f"lam_flatplate_{mesh_id}.cfg"
        if os.path.exists(config_temp):
            os.remove(config_temp)
        
        return {
            'mesh': mesh_file,
            'success': False,
            'time': elapsed_time,
            'message': error_msg
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_msg = f"Exceção: {str(e)}"
        print(f"[{mesh_id}] ✗ {error_msg}")
        
        # Remove arquivo de configuração temporário em caso de erro
        config_temp = f"lam_flatplate_{mesh_id}.cfg"
        if os.path.exists(config_temp):
            os.remove(config_temp)
        
        return {
            'mesh': mesh_file,
            'success': False,
            'time': elapsed_time,
            'message': error_msg
        }

def main():
    """Função principal com processamento paralelo"""
    print("\n" + "="*60)
    print("Script de Execução Automatizada do SU2 (PARALELO)")
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
    
    # Detecta número de CPUs
    num_cpus = cpu_count()
    print(f"\nNúmero de CPUs disponíveis: {num_cpus}")
    
    # Pergunta quantos processos paralelos usar
    print(f"\nQuantos processos paralelos deseja usar?")
    print(f"  Recomendado: {max(1, num_cpus - 1)} (deixa 1 CPU livre)")
    print(f"  Máximo: {num_cpus}")
    
    while True:
        try:
            num_processes = input(f"Número de processos [padrão: {max(1, num_cpus - 1)}]: ").strip()
            if not num_processes:
                num_processes = max(1, num_cpus - 1)
            else:
                num_processes = int(num_processes)
            
            if 1 <= num_processes <= num_cpus:
                break
            else:
                print(f"  Valor deve estar entre 1 e {num_cpus}")
        except ValueError:
            print("  Valor inválido! Digite um número inteiro.")
    
    # Confirmação do usuário
    print(f"\n{'='*60}")
    print(f"Configuração:")
    print(f"  Malhas: {len(mesh_files)}")
    print(f"  Processos paralelos: {num_processes}")
    print(f"{'='*60}")
    response = input("\nDeseja iniciar o processamento? (s/n): ")
    if response.lower() != 's':
        print("Operação cancelada pelo usuário.")
        return
    
    # Inicia processamento paralelo
    print(f"\n{'='*60}")
    print(f"INICIANDO PROCESSAMENTO PARALELO")
    print(f"{'='*60}\n")
    
    start_time_total = time.time()
    
    # Usa Pool para executar em paralelo
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_single_mesh, mesh_files)
    
    total_time = time.time() - start_time_total
    
    # Processa resultados
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    # Relatório detalhado
    print(f"\n\n{'='*60}")
    print(f"RELATÓRIO DETALHADO")
    print(f"{'='*60}")
    
    print("\nSimulações bem-sucedidas:")
    for r in results:
        if r['success']:
            print(f"  ✓ {r['mesh']}: {r['time']:.1f}s")
    
    if fail_count > 0:
        print("\nSimulações com falha:")
        for r in results:
            if not r['success']:
                print(f"  ✗ {r['mesh']}: {r['message']}")
    
    # Relatório final
    print(f"\n{'='*60}")
    print(f"RELATÓRIO FINAL")
    print(f"{'='*60}")
    print(f"Total de malhas processadas: {len(mesh_files)}")
    print(f"  ✓ Sucesso: {success_count}")
    print(f"  ✗ Falhas: {fail_count}")
    print(f"\nTempo total: {total_time:.1f}s ({total_time/60:.1f} minutos)")
    if success_count > 0:
        print(f"Tempo médio por malha: {total_time/len(mesh_files):.1f}s")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

