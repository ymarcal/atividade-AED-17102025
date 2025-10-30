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

# Diretórios
BASE_DIR = r"C:\Users\ymarc\OneDrive\Desktop\ITA_2025\AED_26\Lab9_Atividade1710"
DIR_HORIZONTAL = os.path.join(BASE_DIR, "Analise_Horizontal")
DIR_VERTICAL = os.path.join(BASE_DIR, "Analise_Vertical")

def get_mesh_files(directory):
    """Retorna lista de arquivos de malha a serem processados"""
    # Busca todas as malhas mesh_*.su2 no diretório especificado
    search_pattern = os.path.join(directory, "mesh_d*.su2")
    mesh_files = glob.glob(search_pattern)
    mesh_files.sort()  # Ordena alfabeticamente
    return mesh_files

def create_config_for_mesh(mesh_filename, mesh_id, output_dir):
    """Cria um arquivo de configuração específico para cada malha"""
    config_temp = os.path.join(output_dir, f"lam_flatplate_{mesh_id}.cfg")
    
    with open(CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    
    # Modifica as linhas necessárias para evitar conflitos entre processos paralelos
    with open(config_temp, 'w') as f:
        for line in lines:
            if line.strip().startswith('MESH_FILENAME='):
                f.write(f'MESH_FILENAME= {mesh_filename}\n')
            elif line.strip().startswith('CONV_FILENAME='):
                f.write(f'CONV_FILENAME= {os.path.join(output_dir, f"history_{mesh_id}")}\n')
            elif line.strip().startswith('RESTART_FILENAME='):
                f.write(f'RESTART_FILENAME= {os.path.join(output_dir, f"restart_flow_{mesh_id}.dat")}\n')
            elif line.strip().startswith('VOLUME_FILENAME='):
                f.write(f'VOLUME_FILENAME= {os.path.join(output_dir, f"flow_{mesh_id}")}\n')
            elif line.strip().startswith('SURFACE_FILENAME='):
                f.write(f'SURFACE_FILENAME= {os.path.join(output_dir, f"surface_flow_{mesh_id}")}\n')
            else:
                f.write(line)
    
    return config_temp

def process_single_mesh(args):
    """Processa uma única malha (função para ser executada em paralelo)"""
    mesh_file, output_dir = args
    
    # Extrai o mesh_id do nome do arquivo
    mesh_basename = os.path.basename(mesh_file)
    mesh_id = mesh_basename.replace('mesh_', '').replace('.su2', '')
    
    print(f"\n[{mesh_id}] Iniciando processamento...")
    start_time = time.time()
    
    try:
        # Cria arquivo de configuração específico para esta malha
        config_temp = create_config_for_mesh(mesh_file, mesh_id, output_dir)
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
        config_temp = os.path.join(output_dir, f"lam_flatplate_{mesh_id}.cfg")
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
        config_temp = os.path.join(output_dir, f"lam_flatplate_{mesh_id}.cfg")
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
    
    # Menu de escolha de diretório
    print("Escolha o diretório para processar:")
    print("1. Análise Horizontal (variando x_inlet)")
    print("2. Análise Vertical (variando H_dom)")
    print("3. Diretório atual")
    
    choice = input("\nEscolha (1-3): ").strip()
    
    if choice == '1':
        work_dir = DIR_HORIZONTAL
        analysis_type = "Horizontal"
    elif choice == '2':
        work_dir = DIR_VERTICAL
        analysis_type = "Vertical"
    elif choice == '3':
        work_dir = BASE_DIR
        analysis_type = "Diretório atual"
    else:
        print("Opção inválida!")
        return
    
    print(f"\nTipo de análise: {analysis_type}")
    print(f"Diretório de trabalho: {work_dir}")
    
    # Verifica se o diretório existe
    if not os.path.exists(work_dir):
        print(f"\n✗ ERRO: Diretório não encontrado!")
        print(f"  Crie o diretório primeiro ou gere as malhas.")
        return
    
    # Obtém lista de malhas
    mesh_files = get_mesh_files(work_dir)
    
    if not mesh_files:
        print(f"\n✗ Nenhuma malha encontrada no padrão 'mesh_d*.su2' em {work_dir}")
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
    
    # Prepara argumentos para cada malha (mesh_file, output_dir)
    mesh_args = [(mesh_file, work_dir) for mesh_file in mesh_files]
    
    # Usa Pool para executar em paralelo
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_single_mesh, mesh_args)
    
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

