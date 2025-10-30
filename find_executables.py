"""
Script auxiliar para localizar GMSH e SU2
Autor: Script automatizado
Data: 2025
"""

import os
import subprocess
from pathlib import Path

def find_in_path(executable_name):
    """Verifica se executável está no PATH do sistema"""
    try:
        result = subprocess.run(
            [executable_name, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return executable_name, result.stdout.strip().split('\n')[0]
    except:
        pass
    return None, None

def search_common_locations(executable_patterns, drives=['C:', 'D:']):
    """Busca em locais comuns de instalação"""
    
    found = []
    
    common_dirs = [
        'Program Files',
        'Program Files (x86)',
        ''
    ]
    
    for drive in drives:
        if not os.path.exists(drive):
            continue
            
        for common_dir in common_dirs:
            base_path = os.path.join(drive, common_dir) if common_dir else drive
            
            if not os.path.exists(base_path):
                continue
            
            try:
                # Lista diretórios no nível base
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    
                    if not os.path.isdir(item_path):
                        continue
                    
                    # Verifica se o diretório tem nome relacionado
                    for pattern in executable_patterns:
                        if pattern.lower() in item.lower():
                            # Procura recursivamente por executáveis
                            for root, dirs, files in os.walk(item_path):
                                for file in files:
                                    if file.lower().endswith('.exe'):
                                        full_path = os.path.join(root, file)
                                        found.append(full_path)
                                
                                # Limita profundidade para não demorar muito
                                if root.count(os.sep) - item_path.count(os.sep) > 3:
                                    break
            except (PermissionError, OSError):
                continue
    
    return found

def find_gmsh():
    """Localiza instalação do GMSH"""
    print("\n" + "="*70)
    print("PROCURANDO GMSH...")
    print("="*70)
    
    # Verifica PATH
    print("\n[1] Verificando PATH do sistema...")
    path_exe, version = find_in_path('gmsh')
    if path_exe:
        print(f"  ✓ Encontrado no PATH: {path_exe}")
        print(f"    Versão: {version}")
        return [path_exe]
    else:
        print("  ✗ Não encontrado no PATH")
    
    # Busca em locais comuns
    print("\n[2] Buscando em diretórios comuns...")
    print("    (isso pode demorar alguns segundos...)")
    
    possible_locations = search_common_locations(['gmsh'])
    
    if possible_locations:
        print(f"\n  ✓ Encontrado(s) {len(possible_locations)} executável(is):")
        for loc in possible_locations:
            if 'gmsh.exe' in loc.lower():
                print(f"    • {loc}")
        return [loc for loc in possible_locations if 'gmsh.exe' in loc.lower()]
    else:
        print("  ✗ GMSH não encontrado automaticamente")
        return []

def find_su2():
    """Localiza instalação do SU2"""
    print("\n" + "="*70)
    print("PROCURANDO SU2...")
    print("="*70)
    
    # Verifica PATH
    print("\n[1] Verificando PATH do sistema...")
    path_exe, version = find_in_path('SU2_CFD')
    if path_exe:
        print(f"  ✓ Encontrado no PATH: {path_exe}")
        print(f"    Versão: {version}")
        return [path_exe]
    else:
        print("  ✗ Não encontrado no PATH")
    
    # Verifica localização conhecida do usuário
    user_path = r"C:\Users\ymarc\OneDrive\Documents"
    print(f"\n[2] Verificando pasta de documentos do usuário...")
    print(f"    {user_path}")
    
    found = []
    if os.path.exists(user_path):
        try:
            for item in os.listdir(user_path):
                if 'su2' in item.lower():
                    su2_dir = os.path.join(user_path, item)
                    # Procura SU2_CFD.exe
                    for root, dirs, files in os.walk(su2_dir):
                        for file in files:
                            if file.lower() == 'su2_cfd.exe':
                                full_path = os.path.join(root, file)
                                found.append(full_path)
                                print(f"    ✓ Encontrado: {full_path}")
        except (PermissionError, OSError):
            pass
    
    if found:
        return found
    
    # Busca em locais comuns
    print("\n[3] Buscando em diretórios comuns...")
    print("    (isso pode demorar alguns segundos...)")
    
    possible_locations = search_common_locations(['su2'])
    
    if possible_locations:
        su2_cfds = [loc for loc in possible_locations if 'su2_cfd.exe' in loc.lower()]
        if su2_cfds:
            print(f"\n  ✓ Encontrado(s) {len(su2_cfds)} executável(is):")
            for loc in su2_cfds:
                print(f"    • {loc}")
            return su2_cfds
    
    print("  ✗ SU2_CFD.exe não encontrado automaticamente")
    return []

def test_executable(exe_path, test_arg='--version'):
    """Testa se executável funciona"""
    try:
        result = subprocess.run(
            [exe_path, test_arg],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    """Função principal"""
    
    print("\n" + "="*70)
    print(" "*15 + "LOCALIZAÇÃO DE EXECUTÁVEIS - GMSH E SU2")
    print("="*70)
    print("\nEste script ajuda a encontrar os executáveis necessários.")
    print("="*70)
    
    # Procura GMSH
    gmsh_locations = find_gmsh()
    
    # Procura SU2
    su2_locations = find_su2()
    
    # Resumo
    print("\n\n" + "="*70)
    print("RESUMO E INSTRUÇÕES")
    print("="*70)
    
    if gmsh_locations:
        print("\n✓ GMSH encontrado!")
        print("\nCopie este caminho para usar nos scripts:")
        print(f"  GMSH_PATH = r\"{gmsh_locations[0]}\"")
        
        # Testa
        print("\nTestando executável...")
        works, output = test_executable(gmsh_locations[0])
        if works:
            print(f"  ✓ Funcionando corretamente!")
            print(f"    {output.split(chr(10))[0]}")
        else:
            print(f"  ⚠ Erro ao executar: {output}")
    else:
        print("\n✗ GMSH não encontrado automaticamente")
        print("\nOpções:")
        print("  1. Baixe em: https://gmsh.info/#Download")
        print("  2. Após instalar, execute este script novamente")
        print("  3. Ou forneça o caminho manualmente nos scripts")
    
    if su2_locations:
        print("\n✓ SU2 encontrado!")
        print("\nCopie este caminho para usar nos scripts:")
        print(f"  SU2_PATH = r\"{su2_locations[0]}\"")
        
        # Testa
        print("\nTestando executável...")
        works, output = test_executable(su2_locations[0], '-h')
        if works:
            print(f"  ✓ Funcionando corretamente!")
        else:
            print(f"  ⚠ Erro ao executar: {output}")
    else:
        print("\n✗ SU2 não encontrado automaticamente")
        print("\nOpções:")
        print("  1. Baixe em: https://su2code.github.io/download.html")
        print("  2. Após instalar, execute este script novamente")
        print("  3. Ou forneça o caminho manualmente nos scripts")
    
    print("\n" + "="*70)
    print("\nPróximos passos:")
    print("  1. Copie os caminhos acima")
    print("  2. Cole no início dos scripts Python:")
    print("     - generate_meshes.py")
    print("     - run_su2_batch.py")
    print("     - run_parametric_study.py")
    print("  3. Execute os scripts normalmente")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()


