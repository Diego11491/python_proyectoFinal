import pandas as pd
import numpy as np

def calcular_promedio(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        if df.empty:
            return 0
        return round(np.mean(df['nota']), 2)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return 0
    except Exception as e:
        print(f"Error al calcular promedio: {e}")
        return 0

def cargar_estudiantes_csv(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        df = df.drop_duplicates(subset=['nombre'], keep='last')
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['nombre', 'edad', 'nota'])
    except Exception as e:
        print(f"Error al cargar estudiantes: {e}")
        return pd.DataFrame(columns=['nombre', 'edad', 'nota'])

def eliminar_estudiante_csv(ruta_csv, nombre):
    try:
        df = pd.read_csv(ruta_csv)
        df = df[df['nombre'] != nombre]
        df.to_csv(ruta_csv, index=False)
        return True
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return False
    except Exception as e:
        print(f"Error al eliminar estudiante: {e}")
        return False

def editar_estudiante_csv(ruta_csv, nombre, nueva_edad, nueva_nota):
    try:
        df = pd.read_csv(ruta_csv)
        df.loc[df['nombre'] == nombre, 'edad'] = nueva_edad
        df.loc[df['nombre'] == nombre, 'nota'] = nueva_nota
        df.to_csv(ruta_csv, index=False)
        return True
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return False
    except Exception as e:
        print(f"Error al editar estudiante: {e}")
        return False