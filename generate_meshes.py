"""
Script para gerar malhas automaticamente no GMSH variando parâmetros
Autor: Script automatizado
Data: 2025
"""

import numpy as np
import os
import subprocess
import shutil
from pathlib import Path

# Configurações
GMSH_PATH = r"C:\Users\ymarc\OneDrive\Desktop\ITA_2025\AED_26\Lab 3\gmsh-4.14.0-Windows64\gmsh.exe"  # Ajuste conforme sua instalação
GEO_TEMPLATE = "placa_mod.geo"
GEO_TEMP = "placa_temp.geo"

def find_gmsh():
    """Tenta encontrar o executável do GMSH em locais comuns"""
    possible_paths = [
        r"C:\Users\ymarc\OneDrive\Desktop\ITA_2025\AED_26\Lab 3\gmsh-4.14.0-Windows64\gmsh.exe",
        r"C:\Program Files\gmsh-4.11.1-Windows64\gmsh.exe",
        r"C:\Program Files\gmsh-4.12.0-Windows64\gmsh.exe",
        r"C:\Program Files\gmsh-4.13.0-Windows64\gmsh.exe",
        r"C:\Program Files\gmsh-4.14.0-Windows64\gmsh.exe",
        r"C:\Program Files (x86)\gmsh-4.11.1-Windows64\gmsh.exe",
        r"C:\gmsh\gmsh.exe",
    ]
    
    # Verifica se gmsh está no PATH
    try:
        result = subprocess.run(['gmsh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'gmsh'
    except:
        pass
    
    # Verifica caminhos comuns
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_geo_file(x_inlet, H_dom, output_geo):
    """Cria arquivo .geo com parâmetros especificados"""

    rh=1.12
    lh0=0.02/(1+(rh**24))
    n = np.floor(np.log(-x_inlet*(rh-1)/lh0 + 1)/np.log(rh))
    x_inlet_final = -lh0*(rh**n - 1)/(rh-1)
    
    # Printar valores originais e corrigidos
    print(f"  x_inlet (original) = {x_inlet:.6f}")
    print(f"  x_inlet_final (corrigido) = {x_inlet_final:.6f}")
    print(f"  Diferença = {abs(x_inlet - x_inlet_final):.6f}")
    
    # Template do arquivo .geo
    geo_content = f"""h=1.0;
rh={rh};
rv=1.2;
x_inlet={x_inlet_final};

// H_dom = {H_dom};

// Point(1)={{-0.02,0,0,h}};
Point(1)={{x_inlet,0,0,h}};
Point(2)={{0,0,0,h}};
Point(3)={{0.3048,0,0,h}};
Point(4)={{0.3048,0.03,0,h}};
Point(5)={{0,0.03,0,h}};
Point(6)={{x_inlet,0.03,0,h}};

Line(1)={{1,2}};
Line(2)={{2,3}};
Line(3)={{3,4}};
Line(4)={{4,5}};
Line(5)={{5,6}};
Line(6)={{6,1}};

// Transfinite Curve {{1}} = 25 Using Progression 1/rh; 
Transfinite Curve {{1}} = {int(n)} Using Progression 1/rh; 
Transfinite Curve {{2}} = 41 Using Progression rh;
Transfinite Curve {{3}} = 65 Using Progression rv;
Transfinite Curve {{4}} = 41 Using Progression 1/rh;
// Transfinite Curve {{5}} = 25 Using Progression rh;
Transfinite Curve {{5}} = {int(n)} Using Progression rh;
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
    
    print(f"  [OK] Arquivo .geo criado com x_inlet={x_inlet}, H_dom={H_dom}")
    
    # Retorna o x_inlet_final para ser usado na nomenclatura do arquivo
    return x_inlet_final

def generate_mesh(geo_file, output_su2, gmsh_path):
    """Executa GMSH para gerar malha em formato SU2"""
    
    print(f"  Gerando malha com GMSH...")
    
    try:
        # Comando GMSH: gera malha 2D e exporta para SU2
        # -2: malha 2D
        # -format su2: formato de saída
        # -o: arquivo de saída
        cmd = [
            gmsh_path,
            geo_file,
            '-2',           # Gera malha 2D
            '-format', 'su2',
            '-o', output_su2
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Verifica se o arquivo foi realmente criado
        if os.path.exists(output_su2):
            print(f"  [OK] Malha gerada: {output_su2}")
            return True
        else:
            print(f"  [X] Arquivo nao foi criado: {output_su2}")
            if result.stdout:
                print(f"  Saida GMSH: {result.stdout}")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"  [X] Erro ao gerar malha!")
        print(f"  Saida de erro: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"  [X] Erro: GMSH nao encontrado em {gmsh_path}")
        return False

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("Script de Geração Automática de Malhas - GMSH")
    print("="*60 + "\n")
    
    # Encontra o GMSH
    gmsh_path = find_gmsh()
    
    if gmsh_path is None:
        print("[X] ERRO: GMSH nao encontrado!")
        print("\nPor favor, forneca o caminho completo do executavel gmsh.exe:")
        gmsh_path = input("Caminho: ").strip().strip('"')
        
        if not os.path.exists(gmsh_path):
            print(f"[X] Arquivo nao encontrado: {gmsh_path}")
            return
    
    print(f"[OK] GMSH encontrado: {gmsh_path}\n")
    
    # Define os parâmetros a serem variados
    # Baseado nas malhas existentes: d002, d004, d006, d008, d010, d012, d014
    # Formato: (x_inlet, H_dom, mesh_id)
    
    print("Escolha o modo de geração:")
    print("1. Variar apenas x_inlet (H_dom fixo em 0.03)")
    print("2. Variar apenas H_dom (x_inlet fixo em -0.16)")
    print("3. Variar ambos os parâmetros (matriz de combinações)")
    print("4. Definir parâmetros manualmente")
    
    choice = input("\nEscolha (1-4): ").strip()
    
    parameters = []
    
    if choice == '1':
        # Variar x_inlet
        x_inlet_values = [-0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16, -0.18, -0.20, -0.22, -0.24, -0.26, -0.28, -0.30, -0.32, -0.34, -0.36, -0.38, -0.40]
        H_dom = 0.03
        
        for d in x_inlet_values:
            d_str = f"{abs(d):.2f}".replace('.', '').replace('0', '')
            if d_str == '':
                d_str = '0'
            mesh_id = f"d{int(abs(d)*100):03d}_H{int(H_dom*100):02d}"
            parameters.append((d, H_dom, mesh_id))
    
    elif choice == '2':
        # Variar H_dom
        x_inlet = -0.16
        H_dom_values = [0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24, 0.27, 0.30]
        
        for h in H_dom_values:
            mesh_id = f"d{int(abs(x_inlet)*100):03d}_H{int(h*100):02d}"
            parameters.append((x_inlet, h, mesh_id))
    
    elif choice == '3':
        # Variar ambos
        x_inlet_values = [-0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16]
        H_dom_values = [0.01, 0.02, 0.03, 0.04, 0.05]
        
        for d in x_inlet_values:
            for h in H_dom_values:
                mesh_id = f"d{int(abs(d)*100):03d}_H{int(h*100):02d}"
                parameters.append((d, h, mesh_id))
    
    elif choice == '4':
        # Manual
        print("\nDefina os parâmetros (digite 'fim' para encerrar):")
        while True:
            try:
                x_inlet_input = input("x_inlet (ex: -0.16): ").strip()
                if x_inlet_input.lower() == 'fim':
                    break
                
                x_inlet = float(x_inlet_input)
                H_dom = float(input("H_dom (ex: 0.03): ").strip())
                mesh_id = input("mesh_id (ex: d016_H03): ").strip()
                
                parameters.append((x_inlet, H_dom, mesh_id))
                print(f"  [OK] Adicionado: x_inlet={x_inlet}, H_dom={H_dom}, id={mesh_id}\n")
            except ValueError:
                print("  [X] Valor invalido! Tente novamente.\n")
    else:
        print("Opção inválida!")
        return
    
    if not parameters:
        print("Nenhum parâmetro definido!")
        return
    
    # Mostra resumo
    print(f"\n{'='*60}")
    print(f"Malhas a serem geradas: {len(parameters)}")
    print(f"{'='*60}")
    for i, (d, h, mesh_id) in enumerate(parameters, 1):
        print(f"  {i}. mesh_{mesh_id}.su2 (x_inlet={d:.4f}, H_dom={h:.4f})")
    
    # Confirmação
    response = input("\nDeseja gerar todas essas malhas? (s/n): ").strip().lower()
    if response != 's':
        print("Operação cancelada.")
        return
    
    # Gera as malhas
    success_count = 0
    fail_count = 0
    
    for i, (x_inlet, H_dom, mesh_id) in enumerate(parameters, 1):
        print(f"\n{'#'*60}")
        print(f"# Malha {i}/{len(parameters)}: mesh_{mesh_id}.su2")
        print(f"# x_inlet = {x_inlet:.4f}, H_dom = {H_dom:.4f}")
        print(f"{'#'*60}")
        
        # Cria arquivo .geo temporário e obtém x_inlet_final
        x_inlet_final = create_geo_file(x_inlet, H_dom, GEO_TEMP)
        
        # Atualiza mesh_id com o valor corrigido de x_inlet_final
        mesh_id_final = f"d{int(abs(x_inlet_final)*100):03d}_H{int(H_dom*100):02d}"
        print(f"  mesh_id atualizado: {mesh_id} -> {mesh_id_final}")
        
        # Gera malha com o nome atualizado
        output_file = f"mesh_{mesh_id_final}.su2"
        success = generate_mesh(GEO_TEMP, output_file, gmsh_path)
        
        if success:
            success_count += 1
            # Remove arquivo .geo temporário
            if os.path.exists(GEO_TEMP):
                os.remove(GEO_TEMP)
        else:
            fail_count += 1
    
    # Relatório final
    print(f"\n\n{'='*60}")
    print(f"RELATORIO FINAL")
    print(f"{'='*60}")
    print(f"Total de malhas processadas: {success_count + fail_count}")
    print(f"  [OK] Sucesso: {success_count}")
    print(f"  [X] Falhas: {fail_count}")
    print(f"{'='*60}\n")
    
    if success_count > 0:
        print("As malhas foram geradas com sucesso!")
        print("Agora voce pode executar o script run_su2_batch.py para processar todas.")

if __name__ == "__main__":
    main()


