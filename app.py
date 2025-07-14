from flask import Flask, render_template, request, redirect, send_file
from models import Estudiante
from utils import (
    calcular_promedio,
    cargar_estudiantes_csv,
    eliminar_estudiante_csv,
    editar_estudiante_csv,
    estadisticas_por_grupo_edad,
    obtener_lista_diccionarios
)
import pandas as pd
import numpy as np
import os
import io

# Configurar matplotlib ANTES de cualquier otra importación de matplotlib
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt

from fpdf import FPDF  # Asegúrate de usar fpdf2 en requirements.txt
import base64

app = Flask(__name__)
DATA_FILE = "data/estudiantes.csv"

# Configurar matplotlib para mejor compatibilidad
plt.style.use('default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        edad = int(request.form["edad"])
        nota = float(request.form["nota"])

        estudiante = Estudiante(nombre, edad, nota)
        estudiante.guardar_en_csv(DATA_FILE)

        promedio_actual = calcular_promedio(DATA_FILE)

        return render_template(
            "resultado.html", estudiante=estudiante, promedio=promedio_actual
        )
    return render_template("registro.html")

@app.route("/estadisticas")
def estadisticas():
    if not os.path.exists(DATA_FILE):
        return "No hay datos todavía."

    df = pd.read_csv(DATA_FILE)

    promedio = round(np.mean(df["nota"]), 2)
    maximo = df["nota"].max()
    minimo = df["nota"].min()
    aprobados = df[df["nota"] >= 11].shape[0]
    desaprobados = df[df["nota"] < 11].shape[0]

    # Obtener los 3 mejores estudiantes como tuplas
    top3 = df.sort_values(by="nota", ascending=False).head(3)
    mejores_estudiantes = [(row["nombre"], row["nota"]) for _, row in top3.iterrows()]

    # Estadísticas por edad
    grupo_edad = estadisticas_por_grupo_edad(df)

    return render_template(
        "estadisticas.html",
        promedio=promedio,
        maximo=maximo,
        minimo=minimo,
        aprobados=aprobados,
        desaprobados=desaprobados,
        total=len(df),
        mejores_estudiantes=mejores_estudiantes,
        grupo_edad=grupo_edad
    )

@app.route("/presentaciones")
def presentaciones():
    if not os.path.exists(DATA_FILE):
        return render_template("presentaciones.html", estudiantes=[])

    df = cargar_estudiantes_csv(DATA_FILE)
    estudiantes = [
        Estudiante(row["nombre"], row["edad"], row["nota"]) for _, row in df.iterrows()
    ]
    return render_template("presentaciones.html", estudiantes=estudiantes)

@app.route("/estructura-datos")
def estructura_datos():
    datos = obtener_lista_diccionarios(DATA_FILE)
    return render_template("estructura_datos.html", lista_estudiantes=datos)

@app.route("/grafico")
def grafico():
    try:
        if not os.path.exists(DATA_FILE):
            return "No hay datos disponibles.", 404
        
        df = pd.read_csv(DATA_FILE)
        
        if df.empty or 'nota' not in df.columns:
            return "No hay datos de notas disponibles.", 404
        
        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        df["nota"].plot(kind="hist", bins=10, ax=ax, color="skyblue", edgecolor="black", alpha=0.7)
        ax.set_title("Distribución de Notas", fontsize=16, fontweight='bold')
        ax.set_xlabel("Nota", fontsize=12)
        ax.set_ylabel("Frecuencia", fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Mejorar el diseño
        plt.tight_layout()
        
        # Guardar en memoria
        output = io.BytesIO()
        plt.savefig(output, format="png", dpi=300, bbox_inches='tight')
        output.seek(0)
        plt.close(fig)  # Liberar memoria
        
        return send_file(output, mimetype="image/png")
        
    except Exception as e:
        print(f"Error en gráfico: {str(e)}")
        return f"Error al generar gráfico: {str(e)}", 500

@app.route("/editar-estudiante", methods=["POST"])
def editar_estudiante():
    nombre = request.form["nombre"]
    nueva_edad = int(request.form["edad"])
    nueva_nota = float(request.form["nota"])

    success = editar_estudiante_csv(DATA_FILE, nombre, nueva_edad, nueva_nota)

    if success:
        return redirect("/presentaciones")
    else:
        return "Error al editar el estudiante", 500

@app.route("/eliminar-estudiante", methods=["POST"])
def eliminar_estudiante():
    nombre = request.form["nombre"]

    success = eliminar_estudiante_csv(DATA_FILE, nombre)

    if success:
        return redirect("/presentaciones")
    else:
        return "Error al eliminar el estudiante", 500

@app.route("/descargar-excel")
def descargar_excel():
    try:
        if not os.path.exists(DATA_FILE):
            return "No hay datos para exportar.", 404
        
        df = pd.read_csv(DATA_FILE)
        
        if df.empty:
            return "No hay datos para exportar.", 404
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Escribir datos principales
            df.to_excel(writer, sheet_name='Estudiantes', index=False)
            
            # Crear hoja de estadísticas
            stats_data = {
                'Estadística': ['Total estudiantes', 'Promedio notas', 'Nota máxima', 'Nota mínima'],
                'Valor': [len(df), round(df['nota'].mean(), 2), df['nota'].max(), df['nota'].min()]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            # Formatear las hojas
            workbook = writer.book
            worksheet = writer.sheets['Estudiantes']
            
            # Formato de encabezados
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Aplicar formato a encabezados
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustar ancho de columnas
            if 'nombre' in df.columns:
                worksheet.set_column('A:A', 25)  # Nombre
            if 'edad' in df.columns:
                worksheet.set_column('B:B', 10)  # Edad
            if 'nota' in df.columns:
                worksheet.set_column('C:C', 10)  # Nota
            if 'carrera' in df.columns:
                worksheet.set_column('D:D', 20)  # Carrera (si existe)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_estudiantes.xlsx'
        )
        
    except Exception as e:
        print(f"Error en Excel: {str(e)}")
        return f"Error al generar Excel: {str(e)}", 500

@app.route("/descargar-pdf")
def descargar_pdf():
    try:
        if not os.path.exists(DATA_FILE):
            return "No hay datos para exportar.", 404
        
        df = pd.read_csv(DATA_FILE)
        
        if df.empty:
            return "No hay datos para exportar.", 404
        
        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar fuente (usar fuente estándar que siempre está disponible)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Reporte de Estudiantes", ln=True, align="C")
        pdf.ln(10)
        
        # Verificar qué columnas existen
        columnas = df.columns.tolist()
        
        # Crear encabezados dinámicamente
        pdf.set_font("Arial", "B", 12)
        
        # Configurar anchos de columna basado en columnas disponibles
        if 'nombre' in columnas and 'edad' in columnas and 'nota' in columnas:
            pdf.cell(80, 10, "Nombre", 1, 0, "C")
            pdf.cell(30, 10, "Edad", 1, 0, "C")
            pdf.cell(30, 10, "Nota", 1, 0, "C")
            
            # Si hay carrera, agregarla
            if 'carrera' in columnas:
                pdf.cell(50, 10, "Carrera", 1, 1, "C")
            else:
                pdf.ln()
            
            # Datos
            pdf.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                # Manejar texto largo
                nombre = str(row['nombre'])[:30] if len(str(row['nombre'])) > 30 else str(row['nombre'])
                
                pdf.cell(80, 8, nombre, 1, 0, "L")
                pdf.cell(30, 8, str(row['edad']), 1, 0, "C")
                pdf.cell(30, 8, str(row['nota']), 1, 0, "C")
                
                if 'carrera' in columnas:
                    carrera = str(row['carrera'])[:20] if len(str(row['carrera'])) > 20 else str(row['carrera'])
                    pdf.cell(50, 8, carrera, 1, 1, "L")
                else:
                    pdf.ln()
        else:
            # Si no tiene las columnas esperadas, mostrar datos simples
            pdf.set_font("Arial", "", 10)
            for _, row in df.iterrows():
                linea = " - ".join([f"{col}: {row[col]}" for col in columnas])
                pdf.cell(0, 8, linea[:80], ln=True)  # Limitar longitud de línea
        
        # Estadísticas
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Estadísticas", ln=True)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Total de estudiantes: {len(df)}", ln=True)
        
        if 'nota' in columnas:
            pdf.cell(0, 8, f"Promedio de notas: {df['nota'].mean():.2f}", ln=True)
            pdf.cell(0, 8, f"Nota máxima: {df['nota'].max()}", ln=True)
            pdf.cell(0, 8, f"Nota mínima: {df['nota'].min()}", ln=True)
        
        # Guardar en memoria
        output = io.BytesIO()
        output.write(pdf.output(dest='S').encode('latin1'))  # Usar 'latin1' para evitar problemas de codificación
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reporte_estudiantes.pdf'
        )
        
    except Exception as e:
        print(f"Error en PDF: {str(e)}")
        return f"Error al generar PDF: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)