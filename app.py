from flask import Flask, render_template, request, redirect, send_file
from models import Estudiante
from utils import (
    calcular_promedio,
    cargar_estudiantes_csv,
    eliminar_estudiante_csv,
    editar_estudiante_csv,
)
import pandas as pd
import numpy as np
import os
import io
from fpdf import FPDF

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

    return render_template(
        "estadisticas.html",
        promedio=promedio,
        maximo=maximo,
        minimo=minimo,
        aprobados=aprobados,
        desaprobados=desaprobados,
        total=len(df),
        mejores_estudiantes=mejores_estudiantes,
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
    if not os.path.exists(DATA_FILE):
        return "No hay datos."

    df = pd.read_csv(DATA_FILE)

    lista_estudiantes = []

    for _, row in df.iterrows():
        estudiante_dict = {
            "nombre": row["nombre"],
            "edad": row["edad"],
            "nota": row["nota"],
        }
        lista_estudiantes.append(estudiante_dict)

    return render_template("estructura_datos.html", lista_estudiantes=lista_estudiantes)


# ===== RUTAS PARA CRUD =====


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


# ===== FIN NUEVAS RUTAS =====


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
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
