"""
Script para comparar pressão ao longo da linha entre (-0.02, 0) e (0, 0)
entre múltiplos arquivos VTU
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from read_vtu import read_vtu

# Diretórios
BASE_DIR = r"C:\Users\ymarc\OneDrive\Desktop\ITA_2025\AED_26\Lab9_Atividade1710"
DIR_HORIZONTAL = os.path.join(BASE_DIR, "Analise_Horizontal")
DIR_VERTICAL = os.path.join(BASE_DIR, "Analise_Vertical")


def find_nearest_point(df, x_target, y_target, tolerance=1e-3):
    """
    Encontra o ponto mais próximo de (x_target, y_target) no DataFrame
    
    Args:
        df: DataFrame com coordenadas X, Y
        x_target: coordenada X desejada
        y_target: coordenada Y desejada
        tolerance: tolerância para busca
    
    Returns:
        Linha do DataFrame mais próxima do ponto, ou None se não encontrado
    """
    # Calcula distância de cada ponto ao alvo
    distances = np.sqrt((df['X'] - x_target)**2 + (df['Y'] - y_target)**2)
    
    # Encontra o ponto mais próximo
    min_idx = distances.idxmin()
    min_distance = distances[min_idx]
    
    if min_distance < tolerance:
        return df.loc[min_idx]
    else:
        return df.loc[min_idx]


def compare_pressure_at_point(vtu_files, x_point, y_point, tolerance=1e-3):
    """
    Compara pressão em um ponto específico entre múltiplos arquivos VTU
    
    Args:
        vtu_files: lista de arquivos VTU
        x_point: coordenada X do ponto
        y_point: coordenada Y do ponto
        tolerance: tolerância para encontrar o ponto
    
    Returns:
        lista de dicionários com resultados
    """
    # Lista para armazenar DataFrames
    dataframes = []
    
    print(f"\nLendo {len(vtu_files)} arquivos VTU...")
    print("=" * 70)
    
    # Lê todos os arquivos
    for i, vtu_file in enumerate(vtu_files):
        print(f"[{i+1}/{len(vtu_files)}] Lendo: {vtu_file}")
        df = read_vtu(vtu_file)
        dataframes.append({
            'filename': vtu_file,
            'df': df
        })
    
    print("\n" + "=" * 70)
    print(f"Comparando pressão no ponto ({x_point}, {y_point})")
    print("=" * 70 + "\n")
    
    # Lista para armazenar resultados
    results = []
    
    # Para cada DataFrame, extrai pressão no ponto
    for i, data in enumerate(dataframes):
        df = data['df']
        filename = data['filename']
        
        # Encontra ponto mais próximo
        point = find_nearest_point(df, x_point, y_point, tolerance)
        
        if point is not None:
            pressure = point['Pressure']
            x_actual = point['X']
            y_actual = point['Y']
            
            result = {
                'index': i,
                'filename': filename,
                'x_actual': x_actual,
                'y_actual': y_actual,
                'pressure': pressure
            }
            
            # Calcula diferença com caso anterior (i+1 - i)
            if i > 0:
                pressure_prev = results[i-1]['pressure']
                diff = pressure - pressure_prev
                result['diff_from_previous'] = diff
                result['diff_percent'] = (diff / pressure_prev) * 100 if pressure_prev != 0 else 0
            else:
                result['diff_from_previous'] = None
                result['diff_percent'] = None
            
            results.append(result)
            
            # Imprime resultado
            print(f"Caso {i}: {filename}")
            print(f"  Ponto real: ({x_actual:.6f}, {y_actual:.6f})")
            print(f"  Pressão: {pressure:.6f} Pa")
            
            if i > 0:
                print(f"  Diferença (caso {i} - caso {i-1}): {diff:+.6f} Pa ({result['diff_percent']:+.4f}%)")
            
            print()
    
    return results, dataframes


def main():
    """Função principal - Analisa pressão entre (-0.02, 0) e (0, 0)"""
    
    print("\n" + "=" * 70)
    print(" " * 15 + "COMPARAÇÃO DE PRESSÃO ENTRE CASOS")
    print(" " * 18 + "Linha: (-0.02, 0) até (0, 0)")
    print("=" * 70)
    
    # Menu de escolha de diretório
    print("\nEscolha o diretório para analisar:")
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
        return
    
    # Encontra arquivos VTU (ordenados por nome)
    vtu_pattern = os.path.join(work_dir, 'flow_d*.vtu')
    vtu_files = sorted(glob.glob(vtu_pattern))
    
    if not vtu_files:
        print(f"\n✗ Nenhum arquivo flow_d*.vtu encontrado em {work_dir}!")
        print("  Execute o script run_su2_batch.py primeiro.")
        return
    
    print(f"\n✓ Encontrados {len(vtu_files)} arquivos:")
    for i, f in enumerate(vtu_files):
        print(f"  {i}: {f}")
    
    # Lista para armazenar DataFrames
    print("\n" + "=" * 70)
    print("Lendo arquivos VTU...")
    print("=" * 70)
    
    dataframes = []
    labels = []
    
    for i, vtu_file in enumerate(vtu_files):
        print(f"[{i+1}/{len(vtu_files)}] Lendo: {vtu_file}")
        df = read_vtu(vtu_file)
        dataframes.append(df)
        
        # Extrai label do arquivo
        basename = os.path.basename(vtu_file)
        label = basename.replace('flow_', '').replace('.vtu', '')
        labels.append(label)
    
    # Pontos ao longo da linha entre (-0.02, 0) e (0, 0)
    n_points = 20  # número de pontos a avaliar
    x_points = np.linspace(-0.02, 0, n_points)
    y_point = 0.0
    
    print(f"\n" + "=" * 70)
    print(f"Extraindo pressão em {n_points} pontos entre (-0.02, 0) e (0, 0)")
    print("=" * 70 + "\n")
    
    # Matriz para armazenar pressões: [caso][ponto]
    all_pressures = []
    
    for i, df in enumerate(dataframes):
        pressures_at_points = []
        
        for x in x_points:
            point = find_nearest_point(df, x, y_point, tolerance=1e-3)
            pressure = point['Pressure']
            pressures_at_points.append(pressure)
        
        all_pressures.append(pressures_at_points)
        print(f"Caso {i} ({labels[i]}): Extraídos {len(pressures_at_points)} pontos")
    
    # Calcula diferenças entre casos consecutivos
    print("\n" + "=" * 70)
    print("DIFERENÇAS DE PRESSÃO (Caso i+1 - Caso i)")
    print("=" * 70 + "\n")
    
    # Cria DataFrame com resultados
    results_data = []
    
    for point_idx, x in enumerate(x_points):
        row = {'X': x, 'Y': y_point}
        
        # Pressão em cada caso
        for i in range(len(dataframes)):
            row[f'P_caso_{i}_{labels[i]}'] = all_pressures[i][point_idx]
        
        # Diferenças entre casos consecutivos
        for i in range(1, len(dataframes)):
            diff = all_pressures[i][point_idx] - all_pressures[i-1][point_idx]
            row[f'Delta_P_{i-1}→{i}'] = diff
        
        results_data.append(row)
    
    df_results = pd.DataFrame(results_data)
    
    # Mostra estatísticas das diferenças
    print("ESTATÍSTICAS DAS DIFERENÇAS:")
    print("-" * 70)
    
    for i in range(1, len(dataframes)):
        col_name = f'Delta_P_{i-1}→{i}'
        diff_values = df_results[col_name].values
        
        print(f"\nCaso {i-1} ({labels[i-1]}) → Caso {i} ({labels[i]}):")
        print(f"  Média:      {np.mean(diff_values):+.6f} Pa")
        print(f"  Std Dev:    {np.std(diff_values):.6f} Pa")
        print(f"  Mínimo:     {np.min(diff_values):+.6f} Pa")
        print(f"  Máximo:     {np.max(diff_values):+.6f} Pa")
    
    # Salva resultados em CSV
    output_csv = os.path.join(work_dir, 'pressure_comparison_line.csv')
    df_results.to_csv(output_csv, index=False)
    print(f"\n" + "=" * 70)
    print(f"✓ Resultados salvos em: {output_csv}")
    
    # Plota gráficos
    print(f"Gerando gráficos...")
    
    # Gráfico 1: Distribuição de pressão em cada caso
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    for i in range(len(dataframes)):
        axes[0].plot(x_points, all_pressures[i], 'o-', label=f'Caso {i}: {labels[i]}', linewidth=2)
    
    axes[0].set_xlabel('X (m)')
    axes[0].set_ylabel('Pressão (Pa)')
    axes[0].set_title('Distribuição de Pressão entre (-0.02, 0) e (0, 0)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].axvline(0, color='red', linestyle='--', alpha=0.5, label='Início da placa')
    
    # Gráfico 2: Diferenças entre casos consecutivos
    for i in range(1, len(dataframes)):
        diffs = np.array(all_pressures[i]) - np.array(all_pressures[i-1])
        axes[1].plot(x_points, diffs, 'o-', 
                    label=f'Δ (caso {i} - caso {i-1})', linewidth=2)
    
    axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[1].set_xlabel('X (m)')
    axes[1].set_ylabel('ΔPressão (Pa)')
    axes[1].set_title('Diferenças de Pressão entre Casos Consecutivos')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(0, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    output_plot = os.path.join(work_dir, 'pressure_comparison_line.png')
    plt.savefig(output_plot, dpi=150, bbox_inches='tight')
    print(f"✓ Gráfico salvo em: {output_plot}")
    
    # Gráfico 3: Mapa de calor das diferenças
    if len(dataframes) > 1:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Prepara dados para heatmap
        diff_matrix = []
        diff_labels = []
        
        for i in range(1, len(dataframes)):
            diffs = np.array(all_pressures[i]) - np.array(all_pressures[i-1])
            diff_matrix.append(diffs)
            diff_labels.append(f'{labels[i-1]} → {labels[i]}')
        
        diff_matrix = np.array(diff_matrix)
        
        im = ax.imshow(diff_matrix, aspect='auto', cmap='RdBu_r', 
                      extent=[-0.02, 0, len(diff_labels)-0.5, -0.5])
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Transição entre casos')
        ax.set_yticks(range(len(diff_labels)))
        ax.set_yticklabels(diff_labels)
        ax.set_title('Mapa de Calor: Diferenças de Pressão')
        
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('ΔPressão (Pa)', rotation=270, labelpad=20)
        
        plt.tight_layout()
        output_heatmap = os.path.join(work_dir, 'pressure_heatmap.png')
        plt.savefig(output_heatmap, dpi=150, bbox_inches='tight')
        print(f"✓ Mapa de calor salvo em: {output_heatmap}")
    
    print("\n" + "=" * 70)
    print("✓ Análise concluída!")
    print("=" * 70 + "\n")
    
    plt.close('all')
    
    return df_results, dataframes


if __name__ == "__main__":
    main()

