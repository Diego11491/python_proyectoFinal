import pandas as pd
import numpy as np

def calcular_promedio(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        return round(np.mean(df['nota']), 2)
    except:
        return 0

def cargar_estudiantes_csv(ruta_csv):
    try:
        return pd.read_csv(ruta_csv)
    except:
        return pd.DataFrame()
