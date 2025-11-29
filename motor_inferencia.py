import math
from base_conocimiento import hechos

'''
ej_datos = {
    'ingresos': 1000,
    'gastos': {
        'fijos': [
            {'renta': 200},
            {'electricidad': 100},
            {'telefono/internet': 100},
            {'seguros': 100}
            ],
        'variables': [
            {'comida': 50},
            {'transporte': 50},
            {'ropa': 250},
            {'entretenimiento': 100}
        ]
    },
    'meta_ahorro': 10000
}
'''

# funciones auxiliares
def sumar_gastos(gastos:dict, tipos=('fijos', 'variables'), tipo_index=0, gasto_index=0, total=0):
    # Caso base
    if tipo_index >= len(tipos):
        return total

    tipo_actual = tipos[tipo_index]
    lista_gastos = gastos[tipo_actual]

    # termino los gastos del tipo actual
    if gasto_index >= len(lista_gastos):
        return sumar_gastos(gastos, tipos, tipo_index + 1, 0, total)

    gasto = lista_gastos[gasto_index]
    nombre = list(gasto.keys())[0]
    monto = gasto[nombre]

    return sumar_gastos(gastos, tipos, tipo_index, gasto_index + 1, total + monto)

def sumar_prioridad(gastos: dict, hechos: tuple, prioridad_objetivo: str,
                    tipos=('fijos', 'variables'), tipo_index=0, gasto_index=0, total=0):
    # Caso base
    if tipo_index >= len(tipos):
        return total
    
    tipo_actual = tipos[tipo_index]
    lista_gastos = gastos[tipo_actual]

    # termino los gastos del tipo actual
    if gasto_index >= len(lista_gastos):
        return sumar_prioridad(gastos, hechos, prioridad_objetivo, tipos, tipo_index + 1, 0, total)

    gasto = lista_gastos[gasto_index]
    nombre = list(gasto.keys())[0]
    monto = gasto[nombre]

    # Buscar prioridad
    prioridad = obtener_prioridad(nombre, tipo_actual, hechos)
    if prioridad == prioridad_objetivo:
        total += monto

    return sumar_prioridad(gastos, hechos, prioridad_objetivo, tipos, tipo_index, gasto_index + 1, total)

def obtener_objetivo(prioridades, hechos, index=0):
    # Caso base
    if index >= len(hechos):
        return None

    hecho = hechos[index]

    if hecho[0] == 'objetivo':
        _, valor, detalle = hecho
        if any(p in detalle for p in prioridades):
            return valor

    return obtener_objetivo(prioridades, hechos, index + 1)


def obtener_prioridad(nombre, tipo, hechos, index=0):
    # Caso base
    if index >= len(hechos):
        return None

    categoria, tipo_gasto, nombre_gasto, nivel = hechos[index]

    if categoria == 'gastos' and tipo_gasto == tipo and nombre_gasto == nombre:
        return nivel

    return obtener_prioridad(nombre, tipo, hechos, index + 1)

def obtener_prioridades_gastos(gastos: dict, hechos, tipos=('fijos', 'variables'), tipo_index=0, gasto_index=0, prioridades=None):
    if prioridades is None:
        prioridades = set()

    # Caso base
    if tipo_index >= len(tipos):
        return prioridades

    tipo_actual = tipos[tipo_index]
    lista_gastos = gastos[tipo_actual]

    # no hay más gastos de tipo actual
    if gasto_index >= len(lista_gastos):
        return obtener_prioridades_gastos(gastos, hechos, tipos, tipo_index + 1, 0, prioridades)

    gasto = lista_gastos[gasto_index]
    nombre = list(gasto.keys())[0]

    prioridad = obtener_prioridad(nombre, tipo_actual, hechos)
    if prioridad:
        prioridades.add(prioridad)

    return obtener_prioridades_gastos(gastos, hechos, tipos, tipo_index, gasto_index + 1, prioridades)


# Reglas 
#1 Si no hay ingreso entonces no se puede generar el presupuesto ni calcular tiempo de ahorro
def hay_ingreso(datos:dict):
    return datos.get("ingresos", 0) > 0

#2 Si el 50% de los ingresos se usa para cubrir los gastos de prioridad alta y media, el 30% para cubrir los gastos de prioridad baja y el 20% se destina al ahorro entonces se cumple la regla 50-30-20
def regla_50_30_20(datos:dict, hechos, existe_alta_media:bool=True):
    ingresos = datos["ingresos"]
    gastos = datos["gastos"]
    total_alta_media = sumar_prioridad(gastos, hechos, 'alta') + sumar_prioridad(gastos, hechos, 'media')
    total_baja = sumar_prioridad(gastos, hechos, 'baja')

    limite_alta_media = ingresos * 0.5
    limite_baja = ingresos * 0.3
    if existe_alta_media:
        return total_alta_media <= limite_alta_media and total_baja <= limite_baja
    else:
        return total_baja <= limite_baja
    
#3 Si los ingresos son menores que la suma de los gastos entonces requiere ajustes
def requiere_ajustes(datos:dict):
    if not datos: return "sin datos" 
    ingresos = datos["ingresos"]
    gastos_totales = sumar_gastos(datos["gastos"])
    
    return ingresos < gastos_totales

#4 El tiempo para cumplir la meta se define dividiendo la meta entre el restante mensual
def tiempo_para_ahorrar(datos):
    ingresos = datos["ingresos"]
    meta_ahorro = datos["meta_ahorro"]
    gastos_totales = sumar_gastos(datos["gastos"])
    return math.ceil((meta_ahorro / (ingresos - gastos_totales)))

#5  Si los ingresos son mayores a los gastos entonces se puede ahorrar
def puede_ahorrar(datos:dict):
    ingresos = datos["ingresos"]
    gastos_totales = sumar_gastos(datos["gastos"])
    return ingresos > gastos_totales

#6 Si no existen gastos de prioridad alta/media, el porcentaje destinado a esos gastos puede destinarse al ahorro
def existen_gastos_alta_media(gastos_dict, hechos, tipos=['fijos','variables'], tipo_index=0, gasto_index=0):
    # Caso base
    if tipo_index >= len(tipos):
        return False

    tipo_actual = tipos[tipo_index]
    lista_gastos = gastos_dict[tipo_actual]

    # Ya no hay gastos de ese tipo
    if gasto_index >= len(lista_gastos):
        return existen_gastos_alta_media(gastos_dict, hechos, tipos, tipo_index + 1, 0)

    gasto = lista_gastos[gasto_index]
    nombre = list(gasto.keys())[0]

    prioridad = obtener_prioridad(nombre, tipo_actual, hechos)

    if prioridad == 'alta' or prioridad == 'media':
        return True

    return existen_gastos_alta_media(gastos_dict, hechos, tipos, tipo_index, gasto_index + 1)

#7 El déficit se calcula restando los gastos a los ingresos
def calcular_deficit(datos:dict):
    ingresos = datos["ingresos"]
    gastos = sumar_gastos(datos["gastos"])
    return gastos - ingresos

#8 Si el porcentaje objetivo de una categoría es menor al porcentaje destinado, es necesario recortar hasta acercarlo al porcentaje objetivo
def cumple_porcentaje_objetivo(datos:dict, prioridades:list, hechos):
    ingresos = datos["ingresos"]
    objetivo = obtener_objetivo(prioridades, hechos)
    gasto_actual = 0
    for prioridad in prioridades:
        gasto_actual += sumar_prioridad(datos["gastos"], hechos, prioridad)
    porcentaje_gasto = gasto_actual / ingresos
    if porcentaje_gasto <= objetivo:
        return True
    else:
        return False
    
#9 El monto de recorte de una categoria se calcula gasto_actual − (porcentaje_objetivo / 100) * ingreso
def calcular_monto_recorte(datos:dict, prioridades:list, hechos):
    objetivo = obtener_objetivo(prioridades, hechos)
    ingresos = datos["ingresos"]
    gasto_actual = 0
    for prioridad in prioridades:
        gasto_actual += sumar_prioridad(datos["gastos"], hechos, prioridad)
    return gasto_actual - (objetivo * ingresos)

#10 Si no se define una meta de ahorro no se puede calcular el tiempo para cumplirla
def existe_meta(datos:dict):
    return "meta_ahorro" in datos and datos["meta_ahorro"] > 0


# Consultas
def que_gastos_ajustar(datos: dict):
    if not hay_ingreso(datos):
        return "No es posible evaluar sin ingresos."

    if requiere_ajustes(datos):
        deficit = calcular_deficit(datos)
        return f"Los gastos superan los ingresos en ${deficit}. Se requieren recortes generales."

    if regla_50_30_20(datos, hechos):
        return "No se requieren ajustes en los gastos."

    ingresos = datos["ingresos"]
    prioridades_presentes = obtener_prioridades_gastos(datos["gastos"], hechos)

    grupos_objetivo = {}
    for prioridad in prioridades_presentes:
        objetivo = obtener_objetivo([prioridad], hechos)
        if objetivo not in grupos_objetivo:
            grupos_objetivo[objetivo] = []
        grupos_objetivo[objetivo].append(prioridad)

    ajustes = []

    for objetivo, prioridades in grupos_objetivo.items():
        gasto_total = sum(
            sumar_prioridad(datos["gastos"], hechos, p)
            for p in prioridades
        )
        limite = ingresos * objetivo

        if gasto_total > limite:
            exceso = gasto_total - limite
            prioridades_str = "/".join(prioridades)
            ajustes.append(
                f"Gastos con prioridad '{prioridades_str}' superan el límite de {objetivo*100:.0f}% por ${exceso:.2f}."
            )

    if not ajustes:
        return "Los gastos están dentro de los límites de los objetivos definidos."

    return "Ajustes recomendados:\n- " + "\n- ".join(ajustes)

def cosulta_meses_para_ahorrar(datos:dict):
    if not hay_ingreso(datos): return "No hay ingresos registrados."
    elif not existe_meta(datos): return "No se definio una meta de ahorro."
    elif not puede_ahorrar(datos): return "No puede ahorrar, se requieren ajustes en el presupuesto."  
    else: return tiempo_para_ahorrar(datos)
    
def consulta_gastos_requieren_ajuste(datos:dict):
    if not hay_ingreso(datos): return "No es posible evaluar sin ingresos."
    elif requiere_ajustes(datos): return "Los gastos superan los ingresos, se requieren ajustes."      
    else: return "Los gastos estan dentro del presupuesto."
    
def consulta_cumple_regla_50_30_20(datos:dict):
    if not hay_ingreso(datos): return "No es posible evaluar sin ingresos."
    ex_alta_media = existen_gastos_alta_media(datos["gastos"], hechos)
    if regla_50_30_20(datos, hechos, ex_alta_media):
        return "Los ingresos cumplen con la regla 50/30/20."
    else:
        return "Los ingresos no cumplen con la regla 50/30/20."



