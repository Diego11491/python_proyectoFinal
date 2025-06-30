class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    def presentarse(self):
        return f"Hola, soy {self.nombre} y tengo {self.edad} años."


class Estudiante(Persona):
    def __init__(self, nombre, edad, nota):
        super().__init__(nombre, edad)
        self.nota = nota

    def presentarse(self):
        return f"{super().presentarse()} Mi nota final es {self.nota}."

    def guardar_en_csv(self, archivo):
        import csv
        import pandas as pd
        from os.path import exists

        if exists(archivo):
           df = pd.read_csv(archivo)
           duplicado = df[(df['nombre'] == self.nombre) & (df['edad'] == self.edad)]
           if not duplicado.empty:
                return False  # Ya existe
        else:
           df = pd.DataFrame(columns=['nombre', 'edad', 'nota'])

        with open(archivo, mode='a', newline='') as f:
           writer = csv.writer(f)
           if df.empty:
              writer.writerow(['nombre', 'edad', 'nota'])
           writer.writerow([self.nombre, self.edad, self.nota])
        return True