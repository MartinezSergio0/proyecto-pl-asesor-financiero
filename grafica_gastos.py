# grafico_gastos.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np 

class GraficoGastosWidget(QWidget):
    """Widget contenedor para la gráfica de pastel de Matplotlib, con agrupación de 'Otros' y leyenda."""
    def __init__(self, datos):
        super().__init__()
        self.datos = datos
        self.layout = QVBoxLayout(self)
        self.canvas = self.create_pie_chart() # Ya no retorna la tabla, solo el canvas
        
        self.layout.addWidget(self.canvas)

        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setStyleSheet("background-color: white; border-radius: 10px;")

    def autopct_format(self, values):
        """Función personalizada para ocultar porcentajes menores al 5%."""
        def format_fn(pct):
            # Solo muestra el porcentaje si es mayor o igual al 5%
            return ('%1.1f%%' % pct) if pct >= 5 else ''
        return format_fn

    def _draw_empty_chart(self):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No hay gastos registrados para graficar.", ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.axis('off')
        return FigureCanvas(fig)

    def create_pie_chart(self):
        """Genera y retorna el lienzo de la gráfica de pastel."""
        
        todos_los_gastos = self.datos['gastos']['fijos'] + self.datos['gastos']['variables']
        
        gastos_positivos = {}
        for gasto_dict in todos_los_gastos:
            nombre = list(gasto_dict.keys())[0]
            monto = list(gasto_dict.values())[0]
            if monto > 0:
                gastos_positivos[nombre.capitalize()] = monto

        total_gastos = sum(gastos_positivos.values())
        if total_gastos == 0:
            return self._draw_empty_chart()

        umbral_porcentaje = 5.0
        umbral_monto = total_gastos * (umbral_porcentaje / 100.0)
        
        gastos_mayores = {}
        monto_otros = 0
        
        for nombre, monto in gastos_positivos.items():
            if monto >= umbral_monto:
                gastos_mayores[nombre] = monto
            else:
                monto_otros += monto

        # 3. Construir los datos finales para el gráfico
        final_labels = list(gastos_mayores.keys())
        final_sizes = list(gastos_mayores.values())
        
        if monto_otros > 0:
            final_labels.append("Otros")
            final_sizes.append(monto_otros)

        # 4. Crear la figura de Matplotlib
        fig = Figure(figsize=(6, 5), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Generar la gráfica de pastel
        wedges, texts, autotexts = ax.pie(
            final_sizes, 
            autopct=self.autopct_format(final_sizes), # <-- Porcentajes condicionales
            startangle=90, 
            textprops={'fontsize': 10, 'color': 'white', 'fontweight': 'bold'}
        )
        ax.axis('equal') 
        ax.set_title('Gastos principales', fontsize=14, fontweight='bold')
        
        # Añadir la leyenda al costado derecho
        ax.legend(
            wedges, 
            final_labels, 
            title="Categorías",
            loc="center left",
            bbox_to_anchor=(0.95, 0, 0.5, 1) # Mueve la leyenda fuera del pastel
        )

        fig.tight_layout(rect=[0, 0, 0.85, 1]) # Ajustar el layout para dar espacio a la leyenda
        
        return canvas