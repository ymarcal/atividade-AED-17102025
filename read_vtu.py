"""
Script simples para ler arquivos VTU e converter para DataFrame pandas
Baseado em: https://gist.github.com/christophernhill/e0633da540be8cfd254ac368e16390b6
"""

import vtk
import numpy as np
import pandas as pd


def read_vtu(filename):
    """
    Lê arquivo VTU e retorna DataFrame pandas
    
    Args:
        filename: caminho do arquivo .vtu
    
    Returns:
        df: DataFrame com coordenadas (X, Y, Z) e todas as variáveis
    """
    # Lê arquivo VTU
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    output = reader.GetOutput()
    
    # Obtém coordenadas
    points = output.GetPoints()
    npts = points.GetNumberOfPoints()
    
    # Extrai coordenadas X, Y, Z
    coordinates = np.array([points.GetPoint(i) for i in range(npts)])
    
    # Cria DataFrame com coordenadas
    df = pd.DataFrame(coordinates, columns=['X', 'Y', 'Z'])
    
    # Obtém dados dos pontos
    point_data = output.GetPointData()
    n_arrays = point_data.GetNumberOfArrays()
    
    # Adiciona cada variável ao DataFrame
    for i in range(n_arrays):
        array_name = point_data.GetArrayName(i)
        array = point_data.GetArray(i)
        n_components = array.GetNumberOfComponents()
        
        if n_components == 1:
            # Escalar
            values = np.array([array.GetValue(j) for j in range(npts)])
            df[array_name] = values
        else:
            # Vetor - adiciona cada componente
            for comp in range(n_components):
                values = np.array([array.GetComponent(j, comp) for j in range(npts)])
                df[f'{array_name}[{comp}]'] = values
    
    return df


# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Usa arquivo passado como argumento
        vtu_file = sys.argv[1]
    else:
        # Procura primeiro arquivo flow_*.vtu
        import glob
        vtu_files = glob.glob('flow_*.vtu')
        if vtu_files:
            vtu_file = vtu_files[0]
        else:
            print("Uso: python read_vtu.py <arquivo.vtu>")
            print("Ou coloque arquivos flow_*.vtu no diretório atual")
            sys.exit(1)
    
    print(f"Lendo: {vtu_file}")
    df = read_vtu(vtu_file)
    
    print(f"\nDataFrame criado com {len(df)} pontos")
    print(f"Colunas: {list(df.columns)}")
    print("\nPrimeiras linhas:")
    print(df.head())
    
    # Salva em CSV (opcional)
    csv_file = vtu_file.replace('.vtu', '.csv')
    df.to_csv(csv_file, index=False)
    print(f"\nSalvo em: {csv_file}")

