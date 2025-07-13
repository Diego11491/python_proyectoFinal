import pandas as pd
import numpy as np
import os

# Calcula el promedio general de las notas
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

# Carga el CSV de estudiantes y elimina duplicados por nombre
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

# Elimina un estudiante por nombre
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

# Edita la edad y la nota de un estudiante por nombre
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

# Ordena el DataFrame por la columna indicada
def ordenar_estudiantes(df, columna="nota", ascendente=False):
    try:
        return df.sort_values(by=columna, ascending=ascendente)
    except:
        return df

# Busca estudiantes que contengan el término (en nombre, edad o nota)
def buscar_estudiantes(df, termino):
    try:
        if termino.isdigit():
            edad = int(termino)
            nota = float(termino)
            filtro = (df['edad'] == edad) | (df['nota'] == nota)
        else:
            filtro = df['nombre'].str.contains(termino, case=False, na=False)
        return df[filtro]
    except:
        return pd.DataFrame()

# Devuelve estadísticas adicionales por grupo de edad
def estadisticas_por_grupo_edad(df):
    try:
        menores = df[df['edad'] < 20]['nota']
        mayores = df[df['edad'] >= 20]['nota']
        return {
            "promedio_menores": round(menores.mean(), 2) if not menores.empty else 0,
            "promedio_mayores": round(mayores.mean(), 2) if not mayores.empty else 0
        }
    except:
        return {"promedio_menores": 0, "promedio_mayores": 0}

# Devuelve los datos como lista de diccionarios usando append()
def obtener_lista_diccionarios(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        lista = []
        for _, row in df.iterrows():
            lista.append({
                "nombre": row['nombre'],
                "edad": row['edad'],
                "nota": row['nota']
            })
        return lista
    except:
        return []