hechos = (
    ('gastos', 'fijos', 'renta', 'alta'),
    ('gastos', 'fijos', 'electricidad', 'alta'),
    ('gastos', 'fijos', 'agua', 'alta'),
    ('gastos', 'fijos', 'gas', 'alta'),
    ('gastos', 'fijos', 'telefono/internet', 'media'),
    ('gastos', 'fijos', 'seguros', 'media'),
    ('gastos', 'variables', 'comida', 'alta'),
    ('gastos', 'variables', 'transporte', 'media'),
    ('gastos', 'variables', 'ropa', 'baja'),
    ('gastos', 'variables', 'cine y conciertos', 'baja'),        
    ('gastos', 'variables', 'videojuegos y apps de pago', 'baja'),
    ('gastos', 'variables', 'libros y revistas', 'media'),        
    ('gastos', 'variables', 'cursos y talleres (hobbies)', 'media'), 
    ('gastos', 'variables', 'actividades deportivas/gimnasio', 'media'), 
    ('gastos', 'variables', 'salidas sociales y bares', 'baja'), 
    ('gastos', 'variables', 'salud/medicamentos', 'alta'),
    ('gastos', 'variables', 'interes de deudas','alta'),
    ('objetivo', .50, ('alta', 'media')),
    ('objetivo', .30, ('baja',))
)

# Reglas que aplican en la base de conocimiento
#11 Si un gasto es una necesidad básica o su falta genera un riesgo grave entonces tiene una prioridad alta
#12 Si un gasto es una gasto importante para mantener estabilidad/funcionalidad pero su falta no representa un riesgo crítico entonces tiene una prioridad media
#13 Si un gasto es prescindible entonces se considera un gasto de prioridad baja
