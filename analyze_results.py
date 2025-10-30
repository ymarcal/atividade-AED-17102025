"""
Script para análise e comparação de resultados do estudo paramétrico
Autor: Script automatizado
Data: 2025

Funções:
- Lê arquivos history_*.csv
- Gera gráficos de convergência
- Compara diferentes casos
- Extrai coeficientes de arrasto e sustentação
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def find_history_files():
    """Encontra todos os arquivos de histórico"""
    history_files = glob.glob('history_d*.csv')
    history_files.sort()
    return history_files

def parse_mesh_id(filename):
    """Extrai parâmetros do nome do arquivo"""
    # Exemplo: history_d016_H03.csv
    basename = os.path.basename(filename)
    parts = basename.replace('history_', '').replace('.csv', '').split('_')
    
    try:
        d_str = parts[0].replace('d', '')
        h_str = parts[1].replace('H', '')
        
        d_inlet = -float(d_str) / 100.0
        H_dom = float(h_str) / 100.0
        
        return d_inlet, H_dom, f"{parts[0]}_{parts[1]}"
    except:
        return None, None, basename

def load_history(filename):
    """Carrega arquivo de histórico do SU2"""
    try:
        # SU2 CSV pode ter diferentes formatos
        df = pd.read_csv(filename)
        
        # Remove espaços nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        return df
    except Exception as e:
        print(f"  ✗ Erro ao carregar {filename}: {e}")
        return None

def plot_convergence_individual(history_files):
    """Plota convergência individual de cada caso"""
    
    print("\n" + "="*70)
    print("GRÁFICOS DE CONVERGÊNCIA INDIVIDUAL")
    print("="*70 + "\n")
    
    for hist_file in history_files:
        d_inlet, H_dom, mesh_id = parse_mesh_id(hist_file)
        df = load_history(hist_file)
        
        if df is None:
            continue
        
        print(f"Processando: {mesh_id}")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'Convergência - {mesh_id} (d_inlet={d_inlet:.3f}, H_dom={H_dom:.3f})', 
                     fontsize=14, fontweight='bold')
        
        # Identifica colunas de resíduos (RMS)
        rms_cols = [col for col in df.columns if 'rms' in col.lower() or 'RMS' in col]
        iter_col = 'Inner_Iter' if 'Inner_Iter' in df.columns else df.columns[0]
        
        # Plot 1: Resíduos
        ax = axes[0, 0]
        for col in rms_cols[:4]:  # Primeiros 4 resíduos
            if col in df.columns:
                ax.semilogy(df[iter_col], df[col], label=col, linewidth=2)
        ax.set_xlabel('Iteração')
        ax.set_ylabel('Resíduo (log)')
        ax.set_title('Resíduos RMS')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Coeficiente de Arrasto
        ax = axes[0, 1]
        drag_cols = [col for col in df.columns if 'Drag' in col or 'CD' in col or 'DRAG' in col]
        for col in drag_cols:
            if col in df.columns:
                ax.plot(df[iter_col], df[col], label=col, linewidth=2)
        ax.set_xlabel('Iteração')
        ax.set_ylabel('Cd')
        ax.set_title('Coeficiente de Arrasto')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Coeficiente de Sustentação
        ax = axes[1, 0]
        lift_cols = [col for col in df.columns if 'Lift' in col or 'CL' in col or 'LIFT' in col]
        for col in lift_cols:
            if col in df.columns:
                ax.plot(df[iter_col], df[col], label=col, linewidth=2)
        ax.set_xlabel('Iteração')
        ax.set_ylabel('Cl')
        ax.set_title('Coeficiente de Sustentação')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Tempo de simulação
        ax = axes[1, 1]
        time_cols = [col for col in df.columns if 'Time' in col or 'Wall' in col]
        for col in time_cols:
            if col in df.columns:
                ax.plot(df[iter_col], df[col], label=col, linewidth=2)
        ax.set_xlabel('Iteração')
        ax.set_ylabel('Tempo (s)')
        ax.set_title('Tempo de Simulação')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salva figura
        output_file = f'convergence_{mesh_id}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  ✓ Gráfico salvo: {output_file}")
        plt.close()

def compare_cases(history_files, parameter='d_inlet'):
    """Compara diferentes casos variando um parâmetro"""
    
    print("\n" + "="*70)
    print(f"COMPARAÇÃO DE CASOS - Variando {parameter}")
    print("="*70 + "\n")
    
    data = []
    
    for hist_file in history_files:
        d_inlet, H_dom, mesh_id = parse_mesh_id(hist_file)
        df = load_history(hist_file)
        
        if df is None:
            continue
        
        # Pega valores finais (última iteração)
        last_row = df.iloc[-1]
        
        data.append({
            'd_inlet': d_inlet,
            'H_dom': H_dom,
            'mesh_id': mesh_id,
            'df': df,
            'last': last_row
        })
    
    if not data:
        print("Nenhum dado encontrado!")
        return
    
    # Ordena por parâmetro escolhido
    data.sort(key=lambda x: x[parameter])
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Comparação de Casos - Variando {parameter}', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Convergência de densidade
    ax = axes[0, 0]
    for item in data:
        df = item['df']
        label = f"{item['mesh_id']}"
        iter_col = 'Inner_Iter' if 'Inner_Iter' in df.columns else df.columns[0]
        rms_dens = [col for col in df.columns if 'Density' in col and 'rms' in col.lower()]
        if rms_dens:
            ax.semilogy(df[iter_col], df[rms_dens[0]], label=label, linewidth=1.5)
    ax.set_xlabel('Iteração')
    ax.set_ylabel('RMS Densidade (log)')
    ax.set_title('Convergência de Densidade')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Cd final vs parâmetro
    ax = axes[0, 1]
    param_values = [item[parameter] for item in data]
    drag_cols = [col for col in data[0]['last'].index if 'Drag' in col or 'CD' in col]
    if drag_cols:
        cd_values = [item['last'][drag_cols[0]] for item in data]
        ax.plot(param_values, cd_values, 'o-', linewidth=2, markersize=8)
        ax.set_xlabel(parameter)
        ax.set_ylabel('Cd')
        ax.set_title('Coeficiente de Arrasto vs ' + parameter)
        ax.grid(True, alpha=0.3)
        
        # Anota valores
        for i, (x, y, item) in enumerate(zip(param_values, cd_values, data)):
            ax.annotate(item['mesh_id'], (x, y), textcoords="offset points", 
                       xytext=(0,10), ha='center', fontsize=7)
    
    # Plot 3: Cl final vs parâmetro
    ax = axes[1, 0]
    lift_cols = [col for col in data[0]['last'].index if 'Lift' in col or 'CL' in col]
    if lift_cols:
        cl_values = [item['last'][lift_cols[0]] for item in data]
        ax.plot(param_values, cl_values, 's-', linewidth=2, markersize=8, color='orange')
        ax.set_xlabel(parameter)
        ax.set_ylabel('Cl')
        ax.set_title('Coeficiente de Sustentação vs ' + parameter)
        ax.grid(True, alpha=0.3)
    
    # Plot 4: Tempo total
    ax = axes[1, 1]
    time_cols = [col for col in data[0]['last'].index if 'Time' in col]
    if time_cols:
        time_values = [item['last'][time_cols[0]] for item in data]
        ax.bar([item['mesh_id'] for item in data], time_values, color='steelblue')
        ax.set_xlabel('Caso')
        ax.set_ylabel('Tempo Total (s)')
        ax.set_title('Tempo de Simulação')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    output_file = f'comparison_{parameter}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Gráfico de comparação salvo: {output_file}")
    plt.close()

def generate_summary_table(history_files):
    """Gera tabela resumo com resultados finais"""
    
    print("\n" + "="*70)
    print("TABELA RESUMO DOS RESULTADOS")
    print("="*70 + "\n")
    
    summary = []
    
    for hist_file in history_files:
        d_inlet, H_dom, mesh_id = parse_mesh_id(hist_file)
        df = load_history(hist_file)
        
        if df is None:
            continue
        
        last_row = df.iloc[-1]
        
        # Extrai valores principais
        drag_cols = [col for col in df.columns if 'Drag' in col or 'CD' in col]
        lift_cols = [col for col in df.columns if 'Lift' in col or 'CL' in col]
        
        cd = last_row[drag_cols[0]] if drag_cols else None
        cl = last_row[lift_cols[0]] if lift_cols else None
        
        summary.append({
            'Caso': mesh_id,
            'd_inlet (m)': f"{d_inlet:.4f}",
            'H_dom (m)': f"{H_dom:.4f}",
            'Cd': f"{cd:.6f}" if cd is not None else "N/A",
            'Cl': f"{cl:.6f}" if cl is not None else "N/A",
            'Iterações': int(last_row[df.columns[0]]) if len(df.columns) > 0 else "N/A"
        })
    
    # Cria DataFrame e exibe
    df_summary = pd.DataFrame(summary)
    print(df_summary.to_string(index=False))
    
    # Salva em CSV
    output_csv = 'summary_results.csv'
    df_summary.to_csv(output_csv, index=False)
    print(f"\n✓ Tabela resumo salva: {output_csv}")
    
    return df_summary

def main():
    """Função principal"""
    
    print("\n" + "="*70)
    print(" "*15 + "ANÁLISE DE RESULTADOS - ESTUDO PARAMÉTRICO")
    print("="*70 + "\n")
    
    # Encontra arquivos de histórico
    history_files = find_history_files()
    
    if not history_files:
        print("✗ Nenhum arquivo de histórico encontrado!")
        print("  Procurando por: history_d*.csv")
        return
    
    print(f"✓ Arquivos encontrados: {len(history_files)}\n")
    for i, f in enumerate(history_files, 1):
        print(f"  {i}. {f}")
    
    print("\n" + "="*70)
    print("Opções de análise:")
    print("  1. Gráficos de convergência individuais")
    print("  2. Comparação variando d_inlet")
    print("  3. Comparação variando H_dom")
    print("  4. Tabela resumo")
    print("  5. Análise completa (todas as opções)")
    
    choice = input("\nEscolha (1-5): ").strip()
    
    if choice == '1' or choice == '5':
        plot_convergence_individual(history_files)
    
    if choice == '2' or choice == '5':
        compare_cases(history_files, parameter='d_inlet')
    
    if choice == '3' or choice == '5':
        compare_cases(history_files, parameter='H_dom')
    
    if choice == '4' or choice == '5':
        generate_summary_table(history_files)
    
    print("\n" + "="*70)
    print("✓ Análise concluída!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()


