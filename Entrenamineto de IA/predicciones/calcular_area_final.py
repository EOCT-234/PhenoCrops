import os
import pandas as pd
from shapely.geometry import Polygon
from shapely.ops import unary_union

labels_path = "resultados2/labels"
output_file = "areas_finales.xlsx"

data = []
errores = []

PX_PER_CM = 94  # tu escala
SCALE = (1 / PX_PER_CM) ** 2  # cm² por pixel²

for file in os.listdir(labels_path):
    if not file.endswith(".txt"):
        continue

    filepath = os.path.join(labels_path, file)

    try:
        with open(filepath, "r") as f:
            values = list(map(float, f.read().split()))

        # Extraer coordenadas desc. YOLO -> pares (x, y)
        coords = [(values[i], values[i+1]) for i in range(0, len(values), 2)]

        # --- REPARADOR ---
        # Si faltó el último punto, lo cerramos automáticamente
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        polygon = Polygon(coords)

        # Si es inválido, intentar repararlo
        if not polygon.is_valid:
            polygon = polygon.buffer(0)  # repara huecos y cruces

        if not polygon.is_valid:
            errores.append(f"{file}: polígono inválido incluso tras reparación")
            continue

        area_px = polygon.area
        area_cm = area_px * SCALE

        data.append([file, area_px, area_cm])

    except Exception as e:
        errores.append(f"{file}: {str(e)}")

df = pd.DataFrame(data, columns=["archivo", "area_px", "area_cm"])
df.to_excel(output_file, index=False)

print(f"✔ Cálculo completado. Archivo guardado en: {output_file}\n")

if errores:
    print("⚠ Archivos con problemas:")
    for e in errores:
        print(" -", e)
