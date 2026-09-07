# Esri start of added imports
import sys, os, arcpy
# Esri end of added imports

# Esri start of added variables
g_ESRI_variable_1 = os.path.join(arcpy.env.scriptWorkspace,'..\\commondata\\propuesta_1.gdb')
g_ESRI_variable_2 = 'clasificar(!Distance!)'
g_ESRI_variable_3 = 'clasificacion_accesibilidad'
g_ESRI_variable_4 = "clasificacion_accesibilidad IN ('Alta', 'Media', 'Baja')"
# Esri end of added variables

import arcpy
import os

# Configurar entorno
gdb = g_ESRI_variable_1
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

# Configurar variables para las herramientas de geoprocesamiento
dataset_equip = "Equipamientos"
planeamiento = os.path.join(gdb, "Planeamiento_urbanistico", "urbano_urbanizable_Sur_Madrid_def")
distancias = [200, 500, 1000]
feature_classes = arcpy.ListFeatureClasses(feature_dataset=dataset_equip)
dataset_acces = "Accesibilidad_Equipamientos"
# Iterador para las entidades de Equipamientos
for fc in feature_classes:
    print(f"Procesando equipamiento: {fc}")

# Configurar entradas y salidas de las herramientas 
    equipamiento_path = os.path.join(gdb, dataset_equip, fc)
    buffer_output = os.path.join(gdb, dataset_equip, f"{fc}_buffers_rings")
    intersect_output = os.path.join(gdb, dataset_equip, f"{fc}_intersect")

# Crear múltiple Buffer
    arcpy.analysis.MultipleRingBuffer(
        equipamiento_path,
        buffer_output,
        distancias,
        "Meters",
        "Distance",
        "ALL",
        "FULL",
        "GEODESIC"
    )
    
# Intersect Buffer con parcelas urbanizables
    arcpy.analysis.PairwiseIntersect(
        in_features=[planeamiento, buffer_output],
        out_feature_class=intersect_output,
        join_attributes="ALL",
        output_type="INPUT"
    )
    
# Añadir campo de accesibilidad
    arcpy.AddField_management(
        intersect_output,
        "clasificacion_accesibilidad",
        "TEXT",
        field_length=20
    )

# Código de clasificacion para el campo creado 
    code_block = """
def clasificar(dist):
    if dist is None:
        return "Sin estación"
    elif dist <= 200:
        return "Alta"
    elif dist <= 500:
        return "Media"
    elif dist <= 1000:
        return "Baja"
    else:
        return "Muy baja"
"""
    expression = g_ESRI_variable_2

    # Calcular campo accesibilidad
    arcpy.CalculateField_management(
        intersect_output,
        g_ESRI_variable_3,
        expression,
        "PYTHON3",
        code_block
    )

# Seleccionar accesibilidad (Alta, Media y Baja) y exportarlo
    
    export_output = os.path.join(gdb, dataset_acces, f"{fc}_AMB_Accesibilidad")
    
    where_clause = g_ESRI_variable_4
    
    arcpy.conversion.ExportFeatures(
        intersect_output,
        export_output,
        where_clause
    )
    
    print(f"Exportadas parcelas AMB para {fc}\n")

