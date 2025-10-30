"""
Exemplo de uso programático da comparação de pressão
"""

import glob
import numpy as np
import matplotlib.pyplot as plt
from read_vtu import read_vtu
from compare_pressure import find_nearest_point


# =============================================================================
# EXEMPLO 1: Comparação básica em um ponto
# =============================================================================

def exemplo_basico():
    """Exemplo básico: compara pressão em um ponto entre casos"""
    
    print("\n" + "="*70)
    print("EXEMPLO 1: Comparação Básica")
    print("="*70 + "\n")
    
    # Encontra arquivos VTU
    vtu_files = sorted(glob.glob('flow_d*.vtu'))
    
    if len(vtu_files) < 2:
        print("✗ Necessário pelo menos 2 arquivos VTU")
        return
    
    # Lista para armazenar DataFrames
    dataframes = []
    
    # Lê arquivos
    for vtu_file in vtu_files:
        print(f"Lendo: {vtu_file}")
        df = read_vtu(vtu_file)
        dataframes.append(df)
    
    # Ponto de interesse
    x_point = 0.5  # m
    y_point = 0.0  # m (na placa)
    
    print(f"\nComparando pressão no ponto ({x_point}, {y_point})")
    print("-" * 70)
    
    # Extrai pressão em cada caso
    pressures = []
    
    for i, df in enumerate(dataframes):
        point = find_nearest_point(df, x_point, y_point)
        pressure = point['Pressure']
        pressures.append(pressure)
        
        print(f"Caso {i}: Pressão = {pressure:.6f} Pa")
        
        # Calcula diferença com caso anterior
        if i > 0:
            diff = pressure - pressures[i-1]
            print(f"  → Diferença (caso {i} - caso {i-1}): {diff:+.6f} Pa")
    
    print()


# =============================================================================
# EXEMPLO 2: Comparação em múltiplos pontos
# =============================================================================

def exemplo_multiplos_pontos():
    """Exemplo: compara pressão em vários pontos ao longo da placa"""
    
    print("\n" + "="*70)
    print("EXEMPLO 2: Múltiplos Pontos ao Longo da Placa")
    print("="*70 + "\n")
    
    # Encontra arquivos VTU
    vtu_files = sorted(glob.glob('flow_d*.vtu'))
    
    if len(vtu_files) < 2:
        print("✗ Necessário pelo menos 2 arquivos VTU")
        return
    
    # Lê arquivos
    dataframes = []
    for vtu_file in vtu_files:
        print(f"Lendo: {vtu_file}")
        df = read_vtu(vtu_file)
        dataframes.append(df)
    
    # Pontos ao longo da placa
    x_points = [0.1, 0.3, 0.5, 0.7, 0.9]
    y_point = 0.0  # na placa
    
    print(f"\nComparando pressão em {len(x_points)} pontos")
    print("-" * 70)
    
    # Para cada ponto
    for x in x_points:
        print(f"\nPonto X = {x:.2f} m:")
        
        pressures_at_x = []
        
        for i, df in enumerate(dataframes):
            point = find_nearest_point(df, x, y_point)
            pressure = point['Pressure']
            pressures_at_x.append(pressure)
            
            if i > 0:
                diff = pressure - pressures_at_x[i-1]
                print(f"  Caso {i}: P = {pressure:.4f} Pa, ΔP = {diff:+.4f} Pa")
            else:
                print(f"  Caso {i}: P = {pressure:.4f} Pa")


# =============================================================================
# EXEMPLO 3: Plotar diferenças de pressão
# =============================================================================

def exemplo_plotar_diferencas():
    """Exemplo: plota gráfico das diferenças de pressão"""
    
    print("\n" + "="*70)
    print("EXEMPLO 3: Gráfico de Diferenças de Pressão")
    print("="*70 + "\n")
    
    # Encontra arquivos VTU
    vtu_files = sorted(glob.glob('flow_d*.vtu'))
    
    if len(vtu_files) < 2:
        print("✗ Necessário pelo menos 2 arquivos VTU")
        return
    
    # Lê arquivos
    dataframes = []
    labels = []
    
    for vtu_file in vtu_files:
        print(f"Lendo: {vtu_file}")
        df = read_vtu(vtu_file)
        dataframes.append(df)
        
        # Extrai identificador do arquivo (ex: d002_H03)
        import os
        basename = os.path.basename(vtu_file)
        label = basename.replace('flow_', '').replace('.vtu', '')
        labels.append(label)
    
    # Ponto de interesse
    x_point = 0.5
    y_point = 0.0
    
    # Extrai pressões
    pressures = []
    cases = []
    
    for i, df in enumerate(dataframes):
        point = find_nearest_point(df, x_point, y_point)
        pressure = point['Pressure']
        pressures.append(pressure)
        cases.append(i)
    
    # Calcula diferenças
    diffs = [pressures[i] - pressures[i-1] for i in range(1, len(pressures))]
    
    # Plota
    fig, axes = plt.subplots(2, 1, figsize=(10, 10))
    
    # Subplot 1: Pressão absoluta
    axes[0].plot(cases, pressures, 'o-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Caso')
    axes[0].set_ylabel('Pressão (Pa)')
    axes[0].set_title(f'Pressão no Ponto ({x_point}, {y_point})')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xticks(cases)
    axes[0].set_xticklabels(labels, rotation=45, ha='right')
    
    # Subplot 2: Diferenças
    axes[1].bar(range(1, len(dataframes)), diffs, color='steelblue')
    axes[1].axhline(0, color='red', linestyle='--', linewidth=1)
    axes[1].set_xlabel('Transição')
    axes[1].set_ylabel('ΔPressão (Pa)')
    axes[1].set_title('Diferença de Pressão entre Casos Consecutivos')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Labels para as transições
    transition_labels = [f"{labels[i-1]}\n→\n{labels[i]}" for i in range(1, len(labels))]
    axes[1].set_xticks(range(1, len(dataframes)))
    axes[1].set_xticklabels(transition_labels, rotation=0, fontsize=8)
    
    plt.tight_layout()
    plt.savefig('pressure_differences.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico salvo: pressure_differences.png\n")
    plt.close()


# =============================================================================
# EXEMPLO 4: Diferenças ao longo da placa
# =============================================================================

def exemplo_diferencas_ao_longo_placa():
    """Exemplo: plota diferenças de pressão ao longo da placa"""
    
    print("\n" + "="*70)
    print("EXEMPLO 4: Diferenças ao Longo da Placa")
    print("="*70 + "\n")
    
    # Encontra arquivos VTU
    vtu_files = sorted(glob.glob('flow_d*.vtu'))
    
    if len(vtu_files) < 2:
        print("✗ Necessário pelo menos 2 arquivos VTU")
        return
    
    # Lê apenas os dois primeiros casos para comparação
    print(f"Lendo: {vtu_files[0]}")
    df1 = read_vtu(vtu_files[0])
    
    print(f"Lendo: {vtu_files[1]}")
    df2 = read_vtu(vtu_files[1])
    
    # Pontos ao longo da placa
    x_points = np.linspace(0.1, 1.0, 20)
    y_point = 0.0
    
    pressures_1 = []
    pressures_2 = []
    
    for x in x_points:
        point1 = find_nearest_point(df1, x, y_point)
        point2 = find_nearest_point(df2, x, y_point)
        
        pressures_1.append(point1['Pressure'])
        pressures_2.append(point2['Pressure'])
    
    # Calcula diferenças
    diffs = np.array(pressures_2) - np.array(pressures_1)
    
    # Plota
    fig, axes = plt.subplots(3, 1, figsize=(12, 12))
    
    # Subplot 1: Pressões
    axes[0].plot(x_points, pressures_1, 'o-', label=vtu_files[0], linewidth=2)
    axes[0].plot(x_points, pressures_2, 's-', label=vtu_files[1], linewidth=2)
    axes[0].set_xlabel('X (m)')
    axes[0].set_ylabel('Pressão (Pa)')
    axes[0].set_title('Distribuição de Pressão na Placa')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Subplot 2: Diferença absoluta
    axes[1].plot(x_points, diffs, 'o-', linewidth=2, color='red')
    axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[1].set_xlabel('X (m)')
    axes[1].set_ylabel('ΔPressão (Pa)')
    axes[1].set_title('Diferença de Pressão (Caso 2 - Caso 1)')
    axes[1].grid(True, alpha=0.3)
    
    # Subplot 3: Diferença percentual
    diff_percent = (diffs / np.array(pressures_1)) * 100
    axes[2].plot(x_points, diff_percent, 'o-', linewidth=2, color='green')
    axes[2].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[2].set_xlabel('X (m)')
    axes[2].set_ylabel('ΔPressão (%)')
    axes[2].set_title('Diferença Percentual de Pressão')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('pressure_distribution_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico salvo: pressure_distribution_comparison.png\n")
    plt.close()


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def main():
    """Menu para escolher exemplo"""
    
    print("\n" + "="*70)
    print(" "*20 + "EXEMPLOS DE COMPARAÇÃO")
    print("="*70 + "\n")
    
    print("Escolha o exemplo:")
    print("  1. Comparação básica em um ponto")
    print("  2. Múltiplos pontos ao longo da placa")
    print("  3. Gráfico de diferenças de pressão")
    print("  4. Diferenças ao longo da placa")
    print("  5. Executar todos os exemplos")
    print("  0. Sair")
    
    choice = input("\nEscolha (0-5): ").strip()
    
    try:
        if choice == '1':
            exemplo_basico()
        elif choice == '2':
            exemplo_multiplos_pontos()
        elif choice == '3':
            exemplo_plotar_diferencas()
        elif choice == '4':
            exemplo_diferencas_ao_longo_placa()
        elif choice == '5':
            exemplo_basico()
            exemplo_multiplos_pontos()
            exemplo_plotar_diferencas()
            exemplo_diferencas_ao_longo_placa()
        elif choice == '0':
            print("Encerrando...")
            return
        else:
            print("Opção inválida!")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



