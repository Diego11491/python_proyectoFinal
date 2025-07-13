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
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')  # Usar backend sin GUI
import matplotlib.pyplot as plt

app = Flask(__name__)
DATA_FILE = "data/estudiantes.csv"

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
    if not os.path.exists(DATA_FILE):
        return "No hay datos."

    df = pd.read_csv(DATA_FILE)
    fig, ax = plt.subplots()
    df["nota"].plot(kind="hist", bins=10, ax=ax, color="skyblue", edgecolor="black")
    ax.set_title("Distribución de Notas")
    ax.set_xlabel("Nota")
    ax.set_ylabel("Frecuencia")

    output = io.BytesIO()
    plt.savefig(output, format="png")
    output.seek(0)

    return send_file(output, mimetype="image/png")

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
    if not os.path.exists(DATA_FILE):
        return "No hay datos todavía."

    df = pd.read_csv(DATA_FILE)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Estudiantes")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="reporte_estudiantes.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

@app.route("/descargar-pdf")
def descargar_pdf():
    if not os.path.exists(DATA_FILE):
        return "No hay datos todavía."

    df = pd.read_csv(DATA_FILE)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Reporte de Estudiantes", ln=1, align="C")
    pdf.ln(10)

    for _, row in df.iterrows():
        linea = f"{row['nombre']} - Edad: {row['edad']} - Nota: {row['nota']}"
        pdf.cell(200, 10, txt=linea, ln=1)

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="reporte_estudiantes.pdf",
        mimetype="application/pdf",
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
