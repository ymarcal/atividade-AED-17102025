"""
Script integrado: Gera malhas parametricamente e executa SU2
Autor: Script automatizado
Data: 2025

Este script combina a geração de malhas no GMSH com a execução do SU2,
permitindo um estudo paramétrico completo de forma automatizada.
"""

import os
import subprocess
import shutil
import time
from pathlib import Path

# ============================================================================
# CONFIGURAÇÕES - AJUSTE CONFORME NECESSÁRIO
# ============================================================================

GMSH_PATH = r"C:\Program Files\gmsh-4.11.1-Windows64\gmsh.exe"
SU2_PATH = r"C:\Users\ymarc\OneDrive\Documents\SU2-v8.3.0-win64\win64\bin\SU2_CFD.exe"
CONFIG_FILE = "lam_flatplate.cfg"
CONFIG_BACKUP = "lam_flatplate.cfg.backup"
GEO_TEMP = "placa_temp.geo"

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def find_gmsh():
    """Tenta encontrar o executável do GMSH"""
    possible_paths = [
        r"C:\Program Files\gmsh-4.11.1-Windows64\gmsh.exe",
        r"C:\Program Files\gmsh-4.12.0-Windows64\gmsh.exe",
        r"C:\Program Files\gmsh-4.13.0-Windows64\gmsh.exe",
        r"C:\Program Files (x86)\gmsh-4.11.1-Windows64\gmsh.exe",
    ]
    
    try:
        result = subprocess.run(['gmsh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'gmsh'
    except:
        pass
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_geo_file(d_inlet, H_dom, output_geo):
    """Cria arquivo .geo com parâmetros especificados"""
    
    geo_content = f"""h=1.0;
rh=1.12;
rv=1.2;
d_inlet={d_inlet};
H_dom = {H_dom};
Point(1)={{d_inlet,0,0,h}};
Point(2)={{0,0,0,h}};
Point(3)={{0.3048,0,0,h}};
Point(4)={{0.3048,H_dom,0,h}};
Point(5)={{0,H_dom,0,h}};
Point(6)={{d_inlet,H_dom,0,h}};
Line(1)={{1,2}};
Line(2)={{2,3}};
Line(3)={{3,4}};
Line(4)={{4,5}};
Line(5)={{5,6}};
Line(6)={{6,1}};
Transfinite Curve {{1}} = 25 Using Progression 1/rh; 
Transfinite Curve {{2}} = 41 Using Progression rh;
Transfinite Curve {{3}} = 65 Using Progression rv;
Transfinite Curve {{4}} = 41 Using Progression 1/rh;
Transfinite Curve {{5}} = 25 Using Progression rh;
Transfinite Curve {{6}} = 65 Using Progression 1/rv;
Curve Loop(1) = {{1,2,3,4,5,6}};
Plane Surface(1) = {{1}};
Transfinite Surface {{1}} = {{1,3,4,6}};
Recombine Surface {{1}};
Physical Curve ('inlet') = {{6}};
Physical Curve ('outlet') = {{3,4,5}};
Physical Curve ('sym') = {{1}};
Physical Curve ('plate') = {{2}};
Physical Surface ('domain') = {{1}};
"""
    
    with open(output_geo, 'w') as f:
        f.write(geo_content)

def generate_mesh(geo_file, output_su2, gmsh_path):
    """Executa GMSH para gerar malha em formato SU2"""
    
    try:
        cmd = [
            gmsh_path,
            geo_file,
            '-2',
            '-format', 'su2',
            '-o', output_su2,
            '-'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao gerar malha: {e}")
        return False

def modify_config(mesh_filename):
    """Modifica o arquivo de configuração para usar a malha especificada"""
    with open(CONFIG_FILE, 'r') as f:
        lines = f.readlines()
    
    with open(CONFIG_FILE, 'w') as f:
        for line in lines:
            if line.strip().startswith('MESH_FILENAME='):
                f.write(f'MESH_FILENAME= {mesh_filename}\n')
            else:
                f.write(line)

def run_su2():
    """Executa o SU2_CFD"""
    
    try:
        result = subprocess.run(
            [SU2_PATH, CONFIG_FILE],
            capture_output=False,
            text=True,
            check=True
        )
        return True
    except Exception as e:
        print(f"  ✗ Erro ao executar SU2: {e}")
        return False

def rename_outputs(mesh_id):
    """Renomeia os arquivos de saída com o identificador da malha"""
    
    output_files = {
        'flow.vtu': f'flow_{mesh_id}.vtu',
        'surface_flow.vtu': f'surface_flow_{mesh_id}.vtu',
        'history.csv': f'history_{mesh_id}.csv',
        'restart_flow.dat': f'restart_flow_{mesh_id}.dat'
    }
    
    for old_name, new_name in output_files.items():
        if os.path.exists(old_name):
            if os.path.exists(new_name):
                os.remove(new_name)
            shutil.move(old_name, new_name)

def backup_config():
    """Faz backup do arquivo de configuração original"""
    if os.path.exists(CONFIG_FILE):
        shutil.copy2(CONFIG_FILE, CONFIG_BACKUP)

def restore_config():
    """Restaura o arquivo de configuração original"""
    if os.path.exists(CONFIG_BACKUP):
        shutil.copy2(CONFIG_BACKUP, CONFIG_FILE)
        os.remove(CONFIG_BACKUP)

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do estudo paramétrico"""
    
    print("\n" + "="*70)
    print(" "*10 + "ESTUDO PARAMÉTRICO - CAMADA LIMITE LAMINAR")
    print("="*70)
    print("\nWorkflow: GMSH (geração de malha) → SU2 (simulação) → Resultados")
    print("="*70 + "\n")
    
    # Verifica executáveis
    gmsh_path = find_gmsh()
    if gmsh_path is None:
        print("✗ GMSH não encontrado! Forneça o caminho:")
        gmsh_path = input("Caminho do gmsh.exe: ").strip().strip('"')
        if not os.path.exists(gmsh_path):
            print("Arquivo não encontrado!")
            return
    
    if not os.path.exists(SU2_PATH):
        print(f"✗ SU2 não encontrado em: {SU2_PATH}")
        return
    
    if not os.path.exists(CONFIG_FILE):
        print(f"✗ Arquivo de configuração não encontrado: {CONFIG_FILE}")
        return
    
    print(f"✓ GMSH: {gmsh_path}")
    print(f"✓ SU2: {SU2_PATH}")
    print(f"✓ Config: {CONFIG_FILE}\n")
    
    # Define parâmetros do estudo
    print("="*70)
    print("DEFINIÇÃO DOS PARÂMETROS")
    print("="*70)
    print("\nOpções de estudo:")
    print("  1. Variar d_inlet (distância do inlet) - H_dom fixo = 0.03")
    print("  2. Variar H_dom (altura do domínio) - d_inlet fixo = -0.16")
    print("  3. Matriz completa (variar ambos)")
    print("  4. Casos customizados")
    
    choice = input("\nEscolha (1-4): ").strip()
    
    parameters = []
    
    if choice == '1':
        H_dom = 0.03
        print(f"\nVariando d_inlet com H_dom = {H_dom}")
        print("Valores padrão: -0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16")
        response = input("Usar valores padrão? (s/n): ").strip().lower()
        
        if response == 's':
            d_inlet_values = [-0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16]
        else:
            print("Digite os valores de d_inlet separados por vírgula:")
            values_str = input("d_inlet: ")
            d_inlet_values = [float(v.strip()) for v in values_str.split(',')]
        
        for d in d_inlet_values:
            mesh_id = f"d{int(abs(d)*100):03d}_H{int(H_dom*100):02d}"
            parameters.append((d, H_dom, mesh_id))
    
    elif choice == '2':
        d_inlet = -0.16
        print(f"\nVariando H_dom com d_inlet = {d_inlet}")
        print("Valores padrão: 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10")
        response = input("Usar valores padrão? (s/n): ").strip().lower()
        
        if response == 's':
            H_dom_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10]
        else:
            print("Digite os valores de H_dom separados por vírgula:")
            values_str = input("H_dom: ")
            H_dom_values = [float(v.strip()) for v in values_str.split(',')]
        
        for h in H_dom_values:
            mesh_id = f"d{int(abs(d_inlet)*100):03d}_H{int(h*100):02d}"
            parameters.append((d_inlet, h, mesh_id))
    
    elif choice == '3':
        d_inlet_values = [-0.08, -0.12, -0.16]
        H_dom_values = [0.02, 0.03, 0.04, 0.05]
        
        print(f"\nMatriz completa:")
        print(f"  d_inlet: {d_inlet_values}")
        print(f"  H_dom: {H_dom_values}")
        print(f"  Total de casos: {len(d_inlet_values) * len(H_dom_values)}")
        
        for d in d_inlet_values:
            for h in H_dom_values:
                mesh_id = f"d{int(abs(d)*100):03d}_H{int(h*100):02d}"
                parameters.append((d, h, mesh_id))
    
    elif choice == '4':
        print("\nDefina os casos (digite 'fim' para encerrar):")
        while True:
            d_input = input("d_inlet: ").strip()
            if d_input.lower() == 'fim':
                break
            d_inlet = float(d_input)
            H_dom = float(input("H_dom: ").strip())
            mesh_id = input("ID (ex: d016_H03): ").strip()
            parameters.append((d_inlet, H_dom, mesh_id))
            print(f"  ✓ Adicionado\n")
    
    if not parameters:
        print("Nenhum parâmetro definido!")
        return
    
    # Resumo do estudo
    print(f"\n{'='*70}")
    print(f"RESUMO DO ESTUDO PARAMÉTRICO")
    print(f"{'='*70}")
    print(f"Total de casos: {len(parameters)}\n")
    print(f"{'Caso':<6} {'d_inlet':<10} {'H_dom':<10} {'Mesh ID':<15}")
    print("-"*70)
    for i, (d, h, mesh_id) in enumerate(parameters, 1):
        print(f"{i:<6} {d:<10.4f} {h:<10.4f} {mesh_id:<15}")
    
    print(f"{'='*70}")
    response = input("\nIniciar estudo paramétrico? (s/n): ").strip().lower()
    if response != 's':
        print("Operação cancelada.")
        return
    
    # Executa o estudo
    backup_config()
    
    results = []
    start_time = time.time()
    
    try:
        for i, (d_inlet, H_dom, mesh_id) in enumerate(parameters, 1):
            case_start = time.time()
            
            print(f"\n{'#'*70}")
            print(f"# CASO {i}/{len(parameters)}: {mesh_id}")
            print(f"# d_inlet = {d_inlet:.4f} m  |  H_dom = {H_dom:.4f} m")
            print(f"{'#'*70}\n")
            
            mesh_file = f"mesh_{mesh_id}.su2"
            
            # ETAPA 1: Gerar malha
            print(f"[1/3] Gerando malha...")
            create_geo_file(d_inlet, H_dom, GEO_TEMP)
            mesh_success = generate_mesh(GEO_TEMP, mesh_file, gmsh_path)
            
            if not mesh_success:
                print(f"  ✗ Falha na geração da malha!")
                results.append((mesh_id, False, "Erro na malha", 0))
                continue
            
            print(f"  ✓ Malha gerada: {mesh_file}")
            
            # ETAPA 2: Modificar configuração
            print(f"\n[2/3] Configurando SU2...")
            modify_config(mesh_file)
            print(f"  ✓ Configuração atualizada")
            
            # ETAPA 3: Executar SU2
            print(f"\n[3/3] Executando simulação SU2...")
            print("-"*70)
            su2_success = run_su2()
            print("-"*70)
            
            if not su2_success:
                print(f"  ✗ Falha na simulação!")
                results.append((mesh_id, False, "Erro no SU2", 0))
                continue
            
            print(f"  ✓ Simulação concluída")
            
            # Renomear outputs
            print(f"\nRenomeando resultados...")
            rename_outputs(mesh_id)
            print(f"  ✓ Resultados salvos com ID: {mesh_id}")
            
            # Limpar temporários
            if os.path.exists(GEO_TEMP):
                os.remove(GEO_TEMP)
            
            case_time = time.time() - case_start
            results.append((mesh_id, True, "OK", case_time))
            
            print(f"\n✓ Caso {mesh_id} concluído em {case_time:.1f}s")
    
    finally:
        restore_config()
        if os.path.exists(GEO_TEMP):
            os.remove(GEO_TEMP)
    
    # Relatório final
    total_time = time.time() - start_time
    success_count = sum(1 for _, success, _, _ in results if success)
    
    print(f"\n\n{'='*70}")
    print(f"RELATÓRIO FINAL DO ESTUDO PARAMÉTRICO")
    print(f"{'='*70}")
    print(f"\nTempo total: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Casos processados: {len(results)}")
    print(f"  ✓ Sucesso: {success_count}")
    print(f"  ✗ Falhas: {len(results) - success_count}\n")
    
    print(f"{'Caso':<15} {'Status':<10} {'Tempo (s)':<12} {'Observação'}")
    print("-"*70)
    for mesh_id, success, msg, t in results:
        status = "✓ OK" if success else "✗ ERRO"
        time_str = f"{t:.1f}" if success else "-"
        print(f"{mesh_id:<15} {status:<10} {time_str:<12} {msg}")
    
    print(f"{'='*70}\n")
    
    if success_count > 0:
        print("Arquivos de resultado gerados:")
        print("  • flow_[mesh_id].vtu       - Visualização no VISIT/Paraview")
        print("  • history_[mesh_id].csv    - Histórico de convergência")
        print("  • surface_flow_[mesh_id].vtu - Dados de superfície")
        print("\nVocê pode abrir os arquivos .vtu no VISIT para análise!")

if __name__ == "__main__":
    main()


