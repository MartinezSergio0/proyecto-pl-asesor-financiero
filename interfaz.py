from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QLineEdit, QMessageBox, QGridLayout, QScrollArea, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QFont
import math 

# --- IMPORTACIONES DE TUS MÓDULOS ---
from motor_inferencia import (
    cosulta_meses_para_ahorrar, 
    consulta_gastos_requieren_ajuste, 
    consulta_cumple_regla_50_30_20, 
    que_gastos_ajustar
)
from base_conocimiento import hechos
# ------------------------------------

# --- FUNCIÓN AUXILIAR PARA GENERAR DATOS (sin cambios) ---
def generar_dict(entrada_gastos, entrada_ingreso, entrada_ahorro):
    """Genera el diccionario de datos financieros."""
    try:
        ingresos = float(entrada_ingreso.text())
        if ingresos <= 0:
             QMessageBox.critical(None, "Error de Validación", "El ingreso debe ser un valor positivo.")
             return None
    except ValueError:
        QMessageBox.critical(None, "Error de Validación", "Por favor ingrese un valor válido para los ingresos.")
        return None
        
    ahorro_texto = entrada_ahorro.text().strip()
    ahorro = None
    if ahorro_texto:
        try:
            ahorro = float(ahorro_texto)
        except ValueError:
            QMessageBox.critical(None, "Error de Validación", "Por favor ingrese un valor válido para la meta de ahorro (o deje el campo vacío).")
            return None

    gastos_fijos = []
    gastos_variables = []
    
    gastos_info = {}
    for hecho in hechos:
        if hecho[0] == 'gastos':
            gastos_info[hecho[2]] = hecho[1] 
            
    for nombre_gasto, entry in entrada_gastos.items():
        try:
            monto = float(entry.text() if entry.text() else 0.0) 
        except ValueError:
            QMessageBox.critical(None, "Error de Validación", f"Por favor ingrese un valor válido para {nombre_gasto.capitalize()}.")
            return None
        
        tipo_gasto = gastos_info.get(nombre_gasto)

        if tipo_gasto == 'fijos':
            gastos_fijos.append({nombre_gasto: monto})
        elif tipo_gasto == 'variables':
            gastos_variables.append({nombre_gasto: monto})
    
    datos = {
        "ingresos": ingresos,
        "gastos": {
            "fijos": gastos_fijos,
            "variables": gastos_variables
        }
    }
    if ahorro is not None:
        datos["meta_ahorro"] = ahorro

    return datos


# ----------------------------------------------------------------------
# VISTA 3: CONSULTAS 
# ----------------------------------------------------------------------

class VistaConsultas(QWidget):
    def __init__(self, datos, main_window):
        super().__init__()
        self.datos = datos
        self.main_window = main_window 
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QWidget { background-color: #e0f2f7; font-family: 'Segoe UI', Arial, sans-serif; color: #333333; }
            QLabel#Title { color: #00796b; font-size: 26pt; font-weight: bold; padding: 15px 0; }
            QLabel { font-size: 11pt; }
            QPushButton { background-color: #00796b; color: white; border: none; border-radius: 8px; padding: 15px; font-size: 13pt; font-weight: 600; margin-top: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }
            QPushButton:hover { background-color: #004d40; }
            QPushButton:pressed { background-color: #00382e; padding-top: 17px; padding-bottom: 13px; }
            #BtnBack { background-color: #f44336; }
            #BtnBack:hover { background-color: #d32f2f; }
        """)
        
        titulo = QLabel("Análisis Financiero Detallado")
        titulo.setObjectName("Title")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        self._add_button(layout, "Evaluar Gastos (Vs. Ingresos)", consulta_gastos_requieren_ajuste)
        self._add_button(layout, "Analizar Regla 50/30/20", consulta_cumple_regla_50_30_20)
        self._add_button(layout, "Obtener Sugerencias de Ajuste", que_gastos_ajustar)
        self._add_button(layout, "Calcular Tiempo para Meta de Ahorro", cosulta_meses_para_ahorrar)

        btn_back = QPushButton("← Volver a Ingreso de Datos")
        btn_back.setObjectName("BtnBack")
        btn_back.clicked.connect(lambda: self.main_window.navigate_to(self.main_window.view_ingreso_datos_index))
        layout.addWidget(btn_back)


    def _add_button(self, layout, text, func):
        btn = QPushButton(text)
        btn.clicked.connect(lambda: self.handle_consulta(func(self.datos), text))
        layout.addWidget(btn)
        
    def handle_consulta(self, resultado_motor, boton_texto):
        self.mostrar_resultado(resultado_motor, boton_texto)


    def mostrar_resultado(self, resultado, boton_texto):
        msg = QMessageBox(self)
        msg.setWindowTitle("Resultado de la Consulta")

        final_text = ""
        
        if isinstance(resultado, int) and boton_texto == "Calcular Tiempo para Meta de Ahorro":
            
            meses_total = resultado
            meta = self.datos.get("meta_ahorro", 0.0)
            ingresos = self.datos.get("ingresos", 0.0)
            
            gastos_totales = 0
            if "gastos" in self.datos:
                for tipo in self.datos["gastos"]: 
                    for item in self.datos["gastos"][tipo]:
                        gastos_totales += list(item.values())[0]

            ahorro_mensual = ingresos - gastos_totales
            
            años = math.floor(meses_total / 12)
            meses_restantes = meses_total % 12
            
            nota_ahorro = ""
            if gastos_totales == 0 and ahorro_mensual > 0:
                nota_ahorro = (
                    f"\n\n***NOTA:*** El cálculo se basa en tu **Máxima Capacidad de Ahorro Teórico** "
                    f"($\${ingresos:.2f}$) ya que no se ingresaron montos de gastos."
                )

            final_text = (
                f"🎯 Meta: **${meta:.2f}**\n"
                f" - Ahorro Mensual Disponible: **${ahorro_mensual:.2f}**\n"
                f" - Se necesitan **{meses_total} meses** (aprox. {años} años y {meses_restantes} meses)."
                f"{nota_ahorro}"
            )

        elif isinstance(resultado, str):
            final_text = resultado
            
        else:
            final_text = "Error de datos: Resultado inesperado de la consulta."

        msg.setText(final_text)
        msg.setFont(QFont("Segoe UI", 10))
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; color: #333333; font-family: 'Segoe UI', Arial, sans-serif; }
            QMessageBox QLabel { color: #333333; font-size: 10pt; }
            QMessageBox QPushButton { background-color: #00796b; color: white; border-radius: 5px; padding: 8px 15px; font-size: 10pt; }
            QMessageBox QPushButton:hover { background-color: #004d40; }
        """)
        msg.exec()


# ----------------------------------------------------------------------
# VISTA 2: INGRESO DE DATOS 
# ----------------------------------------------------------------------

class VistaIngresoDatos(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.entrada_gastos = {}
        self.entry_ingreso = None
        self.entry_ahorro = None
        self.gastos_seleccionados = []
        self.gastos_info = self._load_gastos_info()
        
        # Widgets para el layout de gastos (inicializados aquí para setup_ui)
        self.gastos_widget = QWidget()
        self.gastos_layout = QVBoxLayout(self.gastos_widget) 

        self.setup_ui()

    def _load_gastos_info(self):
        info = {}
        for hecho in hechos:
            if hecho[0] == 'gastos':
                info[hecho[2]] = hecho[1] # nombre_gasto: tipo_gasto
        return info

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QWidget { background-color: #f0f4f8; font-family: 'Segoe UI', Arial, sans-serif; color: #333333; }
            QLabel#Title { color: #2c3e50; font-size: 24pt; font-weight: bold; padding: 15px 0; }
            QLabel { color: #34495e; font-size: 11pt; }
            QLineEdit { border: 1px solid #bdc3c7; border-radius: 5px; padding: 8px; font-size: 11pt; background-color: #ffffff; }
            QLineEdit:focus { border: 1px solid #3498db; }
            QPushButton { background-color: #3498db; color: white; border: none; border-radius: 8px; padding: 15px; font-size: 16pt; font-weight: 600; margin-top: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #21618c; padding-top: 17px; padding-bottom: 13px; }
            #BtnBack { background-color: #95a5a6; }
            #BtnBack:hover { background-color: #7f8c8d; }
            QLabel#SectionHeader { color: #2c3e50; font-size: 16pt; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
            QLabel#Tip { color: #e67e22; font-style: italic; font-size: 11pt; margin-bottom: 10px; }
        """)

        titulo = QLabel("Ingrese sus Datos Financieros")
        titulo.setObjectName("Title")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titulo)
        
        instruccion = QLabel("Complete los montos para un análisis preciso:")
        instruccion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruccion.setStyleSheet("font-size: 12pt; margin-bottom: 10px;")
        main_layout.addWidget(instruccion)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # self.gastos_widget y self.gastos_layout ya están inicializados
        self.gastos_layout.setContentsMargins(15, 15, 15, 15)
        self.gastos_layout.setSpacing(0)
        self.scroll_area.setWidget(self.gastos_widget)
        main_layout.addWidget(self.scroll_area)

        self.validator = QDoubleValidator(0.0, 9999999.0, 2)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        
        frame_ingreso = self._create_input_frame("💰 Ingresos mensuales:", False)
        self.entry_ingreso = frame_ingreso.findChild(QLineEdit)
        main_layout.addWidget(frame_ingreso)

        frame_ahorro = self._create_input_frame("📈 Meta de ahorro (opcional):", True)
        self.entry_ahorro = frame_ahorro.findChild(QLineEdit)
        main_layout.addWidget(frame_ahorro)
        
        h_layout_buttons = QHBoxLayout()
        
        btn_back = QPushButton("← Cambiar Selección")
        btn_back.setObjectName("BtnBack")
        btn_back.clicked.connect(lambda: self.main_window.navigate_to(self.main_window.view_seleccion_index))
        h_layout_buttons.addWidget(btn_back)

        btn_enviar = QPushButton("Enviar Datos y Ver Análisis")
        btn_enviar.clicked.connect(self.enviar)
        h_layout_buttons.addWidget(btn_enviar)
        
        main_layout.addLayout(h_layout_buttons)

    def _create_input_frame(self, label_text, is_optional):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet("QFrame { background-color: #eaf5f8; border-radius: 8px; padding: 10px; margin-top: 10px; }")
        layout_frame = QHBoxLayout(frame)
        label = QLabel(label_text)
        entry = QLineEdit()
        entry.setValidator(self.validator)
        entry.setPlaceholderText("0.00" if not is_optional else "Dejar vacío si no aplica")
        entry.setObjectName(label_text.split()[1].lower()) 
        layout_frame.addWidget(label)
        layout_frame.addWidget(entry)
        return frame

    def update_fields(self, gastos_seleccionados):
        """Clasifica los gastos y actualiza la interfaz de ingresos."""
        self.gastos_seleccionados = gastos_seleccionados
        self.entrada_gastos = {}
        
        # --- LIMPIEZA SEGURA DEL LAYOUT PRINCIPAL DE GASTOS ---
        while self.gastos_layout.count():
            item = self.gastos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # ----------------------------------------------------

        gastos_fijos_lista = []
        gastos_variables_lista = []

        for gasto in gastos_seleccionados:
            tipo = self.gastos_info.get(gasto)
            if tipo == 'fijos':
                gastos_fijos_lista.append(gasto)
            elif tipo == 'variables':
                gastos_variables_lista.append(gasto)

        # --- RECREACIÓN DE CONTENEDORES Y LAYOUTS INTERNOS ---
        # Se crean dentro de update_fields para garantizar que son nuevos objetos
        self.fijos_container = QWidget()
        self.fijos_layout = QGridLayout(self.fijos_container)

        self.variables_container = QWidget()
        self.variables_layout = QGridLayout(self.variables_container)
        # ----------------------------------------------------

        if gastos_fijos_lista:
            header = QLabel("Gastos Fijos")
            header.setObjectName("SectionHeader")
            self.gastos_layout.addWidget(header)
            
            for row, gasto in enumerate(gastos_fijos_lista):
                label = QLabel(f"{gasto.capitalize()}: ")
                entry = QLineEdit()
                entry.setPlaceholderText("0.00")
                entry.setValidator(self.validator)
                self.fijos_layout.addWidget(label, row, 0)
                self.fijos_layout.addWidget(entry, row, 1)
                self.entrada_gastos[gasto] = entry
            
            self.gastos_layout.addWidget(self.fijos_container)


        if gastos_variables_lista:
            header = QLabel("Gastos Variables")
            header.setObjectName("SectionHeader")
            self.gastos_layout.addWidget(header)
            
            tip = QLabel("TIP: Agrega lo **máximo** que estimes gastar en estos rubros.")
            tip.setObjectName("Tip")
            self.gastos_layout.addWidget(tip)

            for row, gasto in enumerate(gastos_variables_lista):
                label = QLabel(f"{gasto.capitalize()}: ")
                entry = QLineEdit()
                entry.setPlaceholderText("0.00")
                entry.setValidator(self.validator)
                self.variables_layout.addWidget(label, row, 0)
                self.variables_layout.addWidget(entry, row, 1)
                self.entrada_gastos[gasto] = entry
            
            self.gastos_layout.addWidget(self.variables_container)


    def enviar(self):
        """Genera el diccionario y navega a la vista de consultas."""
        datos = generar_dict(self.entrada_gastos, self.entry_ingreso, self.entry_ahorro)
        if datos:
            vista_consultas = VistaConsultas(datos, self.main_window)
            self.main_window.load_and_navigate(vista_consultas, self.main_window.view_consultas_index)
            

# ----------------------------------------------------------------------
# VISTA 1: SELECCIÓN 
# --------------------------hola pa--------------------------------------------

class VistaSeleccion(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.checkbox_vars = {}
        self.setup_ui() # <--- SOLUCIÓN: Llama al método setup_ui aquí.

    def setup_ui(self): # <--- SOLUCIÓN: Definición del método setup_ui.
        main_layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QWidget { background-color: #e0f7fa; font-family: 'Segoe UI', Arial, sans-serif; color: #212121; }
            QLabel#Title { color: #00796b; font-size: 30pt; font-weight: bold; padding: 20px 0; }
            QLabel { color: #424242; font-size: 12pt; }
            QCheckBox { padding: 8px 0; font-size: 11pt; color: #333333; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #00796b; border-radius: 4px; background-color: white; }
            QCheckBox::indicator:checked { background-color: #00796b; }
            QCheckBox:hover { color: #004d40; }
            QPushButton { background-color: #00796b; color: white; border: none; border-radius: 8px; padding: 18px; font-size: 18pt; font-weight: 600; margin-top: 25px; box-shadow: 3px 3px 8px rgba(0,0,0,0.25); }
            QPushButton:hover { background-color: #004d40; }
            QPushButton:pressed { background-color: #00382e; padding-top: 20px; padding-bottom: 16px; box-shadow: 1px 1px 3px rgba(0,0,0,0.15); }
        """)
        
        titulo = QLabel("Asesor Financiero Personal")
        titulo.setObjectName("Title") 
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titulo)
        
        subtitulo = QLabel("1. Seleccione los gastos que desea incluir en el análisis:")
        subtitulo.setStyleSheet("font-size: 14pt; margin-top: 15px; margin-bottom: 10px; color: #333333;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitulo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        frame = QWidget()
        self.gastos_layout = QVBoxLayout(frame)
        self.gastos_layout.setContentsMargins(20, 10, 20, 10) 
        self.gastos_layout.setSpacing(5) 
        scroll_area.setWidget(frame)
        main_layout.addWidget(scroll_area)
        
        self.checkbox_vars = {}
        
        gastos_unicos = {}
        for hecho in hechos:
            if hecho[0] == 'gastos':
                nombre_gasto = hecho[2]
                if nombre_gasto not in gastos_unicos: 
                    cb = QCheckBox(f"{nombre_gasto.capitalize()}")
                    self.gastos_layout.addWidget(cb)
                    self.checkbox_vars[nombre_gasto] = cb
                    gastos_unicos[nombre_gasto] = True

        btn_confirmar = QPushButton("2. Confirmar y Pasar a Ingresar Montos")
        btn_confirmar.clicked.connect(self.confirmar)
        main_layout.addWidget(btn_confirmar)

    def confirmar(self):
        gastos_seleccionados = []
        for nombre, cb in self.checkbox_vars.items():
            if cb.isChecked():
                gastos_seleccionados.append(nombre)
        
        self.main_window.view_ingreso_datos.update_fields(gastos_seleccionados)
        self.main_window.navigate_to(self.main_window.view_ingreso_datos_index)


# ----------------------------------------------------------------------
# VENTANA PRINCIPAL (Contenedor de Pila)
# ----------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asesor Financiero Personal")
        self.setMinimumSize(550, 700)
        
        self.stack_widget = QStackedWidget()
        self.setCentralWidget(self.stack_widget)
        
        self.view_seleccion = VistaSeleccion(self)
        self.view_ingreso_datos = VistaIngresoDatos(self)
        self.view_consultas = QWidget() 

        self.view_seleccion_index = self.stack_widget.addWidget(self.view_seleccion)
        self.view_ingreso_datos_index = self.stack_widget.addWidget(self.view_ingreso_datos)
        self.view_consultas_index = self.stack_widget.addWidget(self.view_consultas) 

        self.navigate_to(self.view_seleccion_index)
        
    def navigate_to(self, index):
        self.stack_widget.setCurrentIndex(index)

    def load_and_navigate(self, new_widget, index):
        
        old_widget = self.stack_widget.widget(index)
        
        if old_widget:
             self.stack_widget.removeWidget(old_widget)
             old_widget.deleteLater()
        
        self.stack_widget.insertWidget(index, new_widget)
        
        self.stack_widget.setCurrentIndex(index)


# ----------------------------------------------------------------------
# EJECUCIÓN DE LA APLICACIÓN
# ----------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication([])
    
    app.setFont(QFont("Segoe UI", 10))
    
    main_window = MainWindow()
    main_window.show()
    app.exec()