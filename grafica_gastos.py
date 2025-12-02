from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GraficoGastosWidget(QWidget):
    """Widget contenedor para la gráfica de pastel de Matplotlib."""
    def __init__(self, datos):
        super().__init__()
        self.datos = datos
        self.layout = QVBoxLayout(self)
        self.canvas = self.create_pie_chart()
        self.layout.addWidget(self.canvas)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: white; border-radius: 10px;")

    def create_pie_chart(self):
        """Genera y retorna el lienzo de la gráfica de pastel."""
        
        # 1. Preparar los datos
        gastos_data = {}
        todos_los_gastos = self.datos['gastos']['fijos'] + self.datos['gastos']['variables']
        
        for gasto_dict in todos_los_gastos:
            nombre = list(gasto_dict.keys())[0]
            monto = list(gasto_dict.values())[0]
            if monto > 0:  # Solo mostrar gastos con montos > 0
                gastos_data[nombre.capitalize()] = monto

        # 2. Crear la figura
        fig = Figure(figsize=(6.5, 5.5), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if not gastos_data:
            ax.text(
                0.5, 0.5, "No hay gastos registrados para graficar.",
                ha='center', va='center', fontsize=12, transform=ax.transAxes
            )
            ax.axis('off')
            return canvas

        labels = list(gastos_data.keys())
        sizes = list(gastos_data.values())

        show_labels_inside = len(labels) <= 8

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels if show_labels_inside else None,
            autopct='%1.1f%%' if show_labels_inside else None,
            startangle=90,
            textprops={'fontsize': 9}
        )

        ax.axis('equal')  
        ax.set_title('Distribución de Gastos Mensuales', fontsize=14, fontweight='bold')

        if not show_labels_inside:
            ax.legend(
                wedges,
                labels,
                title="Gastos",
                loc="center left",
                bbox_to_anchor=(1.02, 0.5),
                fontsize=9
            )

        fig.tight_layout(rect=[0, 0, 0.85, 1])  

        return canvas
