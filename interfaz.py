from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QLineEdit, QMessageBox, QGridLayout, QScrollArea, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QLocale 
from PySide6.QtGui import QDoubleValidator, QFont
import math 

# --- Importación del Módulo de Gráficos ---
from grafica_gastos import GraficoGastosWidget 
# ------------------------------------------

# --- Importaciones del Módulo de Motor de Inferencia ---
from motor_inferencia import (
    cosulta_meses_para_ahorrar, 
    consulta_gastos_requieren_ajuste, 
    consulta_cumple_regla_50_30_20, 
    que_gastos_ajustar
)
from base_conocimiento import hechos
# ---------------------------------------------

# --- Funciones Auxiliares ---
def generar_dict(entrada_gastos, entrada_ingreso, entrada_ahorro):
    """Genera el diccionario de datos financieros."""
    
    locale = QLocale(QLocale.Spanish, QLocale.Mexico)
    
    def limpiar_monto(text):
        text = text.replace('$', '').strip()
        text = text.replace(locale.groupSeparator(), '') 
        return text
    
    ingresos_text = limpiar_monto(entrada_ingreso.text())
    try:
        ingresos = float(ingresos_text)
    except ValueError:
        QMessageBox.critical(None, "Error de Validación", "Por favor ingrese un valor válido para los ingresos.")
        return None
    
    ahorro_text = limpiar_monto(entrada_ahorro.text())
    ahorro = None
    if ahorro_text:
        try:
            ahorro = float(ahorro_text)
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
        gasto_text = limpiar_monto(entry.text())
        try:
            monto = float(gasto_text if gasto_text else 0.0) 
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
# VISTA 3: Analisis y Consultas 
# ----------------------------------------------------------------------

class VistaAnalisis(QWidget):
    def __init__(self, datos, main_window):
        super().__init__()
        self.datos = datos
        self.main_window = main_window 
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        
        self.setStyleSheet("""
            QWidget { 
                background-color: #f7f7f7; /* Gris claro neutro */
                font-family: Georgia, serif; 
                color: #333333; 
            }
            QLabel#Title { 
                color: #0d47a1; /* Azul Marino (Confianza) */
                font-family: Montserrat, "Berlin Sans", sans-serif; 
                font-size: 26pt; 
                font-weight: bold; 
                padding: 15px 0; 
            }
            QLabel { font-size: 11pt; color: #424242; }
            
            /* Botones de Consulta */
            QPushButton { 
                background-color: #42a5f5; /* Azul brillante */
                color: white; 
                border: none; 
                border-radius: 6px; 
                padding: 12px; 
                font-size: 12pt; 
                font-family: Montserrat, sans-serif;
                font-weight: 600; 
                margin-top: 8px; 
            }
            QPushButton:hover { background-color: #1e88e5; }
            QPushButton:pressed { background-color: #1565c0; }
            
            /* Botón de Retorno (Rojo para salir de la fase de análisis) */
            #BtnBack { 
                background-color: #e57373; /* Rojo suave */
                font-family: Georgia, serif;
            }
            #BtnBack:hover { background-color: #d32f2f; }
        """)
        
        titulo = QLabel("Análisis Financiero Detallado")
        titulo.setObjectName("Title")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        content_layout = QHBoxLayout()
        
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self._add_button(btn_layout, "Evaluar Gastos (Vs. Ingresos)", consulta_gastos_requieren_ajuste)
        self._add_button(btn_layout, "Analizar Regla 50/30/20", consulta_cumple_regla_50_30_20)
        self._add_button(btn_layout, "Obtener Sugerencias de Ajuste", que_gastos_ajustar)
        self._add_button(btn_layout, "Calcular Tiempo para Meta de Ahorro", cosulta_meses_para_ahorrar)
        
        content_layout.addLayout(btn_layout, 40) 

        self.grafico = GraficoGastosWidget(self.datos) 
        content_layout.addWidget(self.grafico, 60) 
        
        layout.addLayout(content_layout)
        
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
        locale = QLocale(QLocale.Spanish, QLocale.Mexico)
        
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
                    f"\n\nNOTA!: El cálculo se basa en tu ¡Ingreso Mensual de ¡${locale.toString(ingresos, 'f', 2)}! "
                    f"(¡${locale.toString(ingresos, 'f', 2)}!) ya que no se ingresaron montos de gastos."
                )

            final_text = (
                f"🎯 Meta: ¡${locale.toString(meta, 'f', 2)}!\n"
                f" - Ahorro Mensual Disponible: ¡${locale.toString(ahorro_mensual, 'f', 2)}!\n"
                f" - Se necesitan ¡{meses_total} meses! (aprox. {años} años y {meses_restantes} meses)."
                f"{nota_ahorro}"
            )

        elif isinstance(resultado, str):
            final_text = resultado
            
        else:
            final_text = "Error de datos: Resultado inesperado de la consulta."

        msg.setText(final_text)
        # Usamos Georgia para el texto de la asesoría
        msg.setFont(QFont("Georgia", 10)) 
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; color: #333333; font-family: Georgia, serif; }
            QMessageBox QLabel { color: #333333; font-size: 10pt; }
            QMessageBox QPushButton { background-color: #00796b; color: white; border-radius: 5px; padding: 8px 15px; font-size: 10pt; }
            QMessageBox QPushButton:hover { background-color: #004d40; }
        """)
        msg.exec()


# ----------------------------------------------------------------------
# VISTA 2: Ingreso de Datos (Ajustes de Fuente y Color)
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
        
        self.gastos_widget = QWidget()
        self.gastos_layout = QVBoxLayout(self.gastos_widget) 

        self.locale_mx = QLocale(QLocale.Spanish, QLocale.Mexico) 
        
        self.setup_ui()

    def _load_gastos_info(self):
        info = {}
        for hecho in hechos:
            if hecho[0] == 'gastos':
                info[hecho[2]] = hecho[1] # nombre_gasto: tipo_gasto
        return info
    
    def format_money(self, entry: QLineEdit):
        """Formatea el texto en el QLineEdit con el símbolo $ y separadores de miles."""
        try:
            text = entry.text().replace('$', '').replace(self.locale_mx.groupSeparator(), '')
            if not text:
                entry.setText("")
                return
            
            value = float(text)
            
            formatted_value = self.locale_mx.toString(value, 'f', 2)
            entry.setText(f"${formatted_value}")
            
        except ValueError:
            entry.setText("")

    def handle_enter_key(self):
        """Mueve el foco al siguiente widget al presionar Enter."""
        if self.focusWidget():
            self.format_money(self.focusWidget()) 
        self.focusNextChild()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
      
        self.setStyleSheet("""
            QWidget { background-color: #ffffff; font-family: Georgia, serif; color: #333333; }
            QLabel#Title { color: #0d47a1; font-family: Montserrat, "Berlin Sans", sans-serif; font-size: 24pt; font-weight: bold; padding: 15px 0; }
            QLabel { color: #333333; font-size: 11pt; }
            
            /* Montos - Aplicando Rojo/Verde para Gastos/Ingresos */
            QLineEdit { 
                border: 1px solid #bdbdbd; border-radius: 5px; padding: 8px; font-size: 11pt; background-color: #ffffff; 
                font-family: "Roboto Mono", monospace; /* Fuente Geométrica/Monoespacio para precisión */
            }
            QLineEdit:focus { border: 1px solid #1e88e5; }
            
            /* Botón de Acción Principal (Azul) */
            QPushButton { 
                background-color: #1e88e5; 
                color: white; border: none; border-radius: 8px; padding: 15px; font-size: 16pt; font-family: Montserrat, sans-serif; font-weight: bold; margin-top: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); 
            }
            QPushButton:hover { background-color: #1565c0; }
            
            /* Encabezados y Tips */
            QLabel#SectionHeader { color: #0d47a1; font-size: 16pt; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
            QLabel#Tip { color: #ff9800; font-style: italic; font-size: 11pt; margin-bottom: 10px; }
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
        self.gastos_layout.setContentsMargins(15, 15, 15, 15)
        self.gastos_layout.setSpacing(0)
        self.scroll_area.setWidget(self.gastos_widget)
        main_layout.addWidget(self.scroll_area)

        self.validator_ingreso = QDoubleValidator(0.0, 9999999.0, 2, self)
        self.validator_ingreso.setLocale(self.locale_mx) 
        self.validator_ingreso.setNotation(QDoubleValidator.StandardNotation)
        
        self.validator_gastos = QDoubleValidator(0.0, 9999999.0, 2, self)
        self.validator_gastos.setLocale(self.locale_mx)
        self.validator_gastos.setNotation(QDoubleValidator.StandardNotation)
        
        # Ingresos (VERDE)
        frame_ingreso = self._create_input_frame("💰 Ingresos mensuales:", self.validator_ingreso, False)
        self.entry_ingreso = frame_ingreso.findChild(QLineEdit)
        self.entry_ingreso.setStyleSheet("color: #43a047; font-weight: 600;") # Verde para Ingreso
        self.entry_ingreso.editingFinished.connect(lambda: self.format_money(self.entry_ingreso)) 
        self.entry_ingreso.returnPressed.connect(self.handle_enter_key)
        main_layout.addWidget(frame_ingreso)

        # Meta de Ahorro (VERDE)
        frame_ahorro = self._create_input_frame("📈 Meta de ahorro (opcional):", self.validator_gastos, True) 
        self.entry_ahorro = frame_ahorro.findChild(QLineEdit)
        self.entry_ahorro.setStyleSheet("color: #43a047; font-weight: 600;") # Verde para Ahorro
        self.entry_ahorro.editingFinished.connect(lambda: self.format_money(self.entry_ahorro)) 
        self.entry_ahorro.returnPressed.connect(self.handle_enter_key)
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

    def _create_input_frame(self, label_text, validator, is_optional):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet("QFrame { background-color: #eaf5f8; border-radius: 8px; padding: 10px; margin-top: 10px; }")
        layout_frame = QHBoxLayout(frame)
        label = QLabel(label_text)
        entry = QLineEdit()
        entry.setValidator(validator) 
        entry.setPlaceholderText("0.00" if not is_optional else "Dejar vacío si no aplica")
        entry.setObjectName(label_text.split()[1].lower()) 
        layout_frame.addWidget(label)
        layout_frame.addWidget(entry)
        return frame

    def update_fields(self, gastos_seleccionados):
        """Clasifica los gastos y actualiza la interfaz de ingresos."""
        self.gastos_seleccionados = gastos_seleccionados
        self.entrada_gastos = {}
        
        while self.gastos_layout.count():
            item = self.gastos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        gastos_fijos_lista = []
        gastos_variables_lista = []

        for gasto in gastos_seleccionados:
            tipo = self.gastos_info.get(gasto)
            if tipo == 'fijos':
                gastos_fijos_lista.append(gasto)
            elif tipo == 'variables':
                gastos_variables_lista.append(gasto)

        self.fijos_container = QWidget()
        self.fijos_layout = QGridLayout(self.fijos_container)

        self.variables_container = QWidget()
        self.variables_layout = QGridLayout(self.variables_container)

        if gastos_fijos_lista:
            header = QLabel("Gastos Fijos")
            header.setObjectName("SectionHeader")
            self.gastos_layout.addWidget(header)
            
            for row, gasto in enumerate(gastos_fijos_lista):
                label = QLabel(f"{gasto.capitalize()}: ")
                entry = QLineEdit()
                entry.setPlaceholderText("0.00")
                entry.setValidator(self.validator_gastos)
                entry.setStyleSheet("color: #e53935;") # Rojo para Gastos
                entry.editingFinished.connect(lambda entry=entry: self.format_money(entry)) 
                entry.returnPressed.connect(self.handle_enter_key)
                
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
                entry.setValidator(self.validator_gastos)
                entry.setStyleSheet("color: #e53935;") # Rojo para Gastos
                entry.editingFinished.connect(lambda entry=entry: self.format_money(entry)) 
                entry.returnPressed.connect(self.handle_enter_key)

                self.variables_layout.addWidget(label, row, 0)
                self.variables_layout.addWidget(entry, row, 1)
                self.entrada_gastos[gasto] = entry
            
            self.gastos_layout.addWidget(self.variables_container)


    def enviar(self):
        """Genera el diccionario y navega a la vista de consultas."""
        datos = generar_dict(self.entrada_gastos, self.entry_ingreso, self.entry_ahorro)
        if datos:
            vista_analisis = VistaAnalisis(datos, self.main_window) 
            self.main_window.load_and_navigate(vista_analisis, self.main_window.view_consultas_index)
            

# ----------------------------------------------------------------------
# VISTA 1: Selección (Ajustes de Fuente y Color)
# ----------------------------------------------------------------------

class VistaSeleccion(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.checkbox_vars = {}
        self.setup_ui() 
    
    def seleccionar_todos(self):
        for cb in self.checkbox_vars.values():
            cb.setChecked(True)

    def deseleccionar_todos(self):
        for cb in self.checkbox_vars.values():
            cb.setChecked(False)

    def setup_ui(self): 
        main_layout = QVBoxLayout(self)
      
        self.setStyleSheet("""
            QWidget { background-color: #e0f7fa; font-family: Georgia, serif; color: #212121; }
            QLabel#Title { 
                color: #0d47a1; /* Azul Marino */
                font-family: Montserrat, "Berlin Sans", sans-serif; 
                font-size: 30pt; 
                font-weight: bold; 
                padding: 20px 0; 
            }
            QLabel { color: #424242; font-size: 12pt; }
            
            QCheckBox { padding: 8px 0; font-size: 11pt; color: #333333; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #0d47a1; border-radius: 4px; background-color: white; }
            QCheckBox::indicator:checked { background-color: #0d47a1; } /* Azul Marino */
            QCheckBox:hover { color: #0d47a1; }
            
            /* Botón de Confirmación Principal */
            QPushButton#BtnConfirm { 
                background-color: #0d47a1; 
                color: white; border: none; border-radius: 8px; padding: 18px; font-size: 18pt; 
                font-family: Montserrat, sans-serif; 
                font-weight: bold; 
                margin-top: 25px; box-shadow: 3px 3px 8px rgba(0,0,0,0.25); 
            }
            QPushButton#BtnConfirm:hover { background-color: #1565c0; }
            
            /* Botones Auxiliares */
            QPushButton#AuxButton {
                background-color: #90a4ae; /* Azul grisáceo */
                color: #212121;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                font-family: Georgia, serif;
            }
            QPushButton#AuxButton:hover {
                background-color: #78909c;
            }
        """)
        
        titulo = QLabel("Asesor Financiero Personal")
        titulo.setObjectName("Title") 
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titulo)
         
        frase_bienvenida = QLabel("¡Bienvenido! Empecemos a organizar tus finanzas.")
        frase_bienvenida.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frase_bienvenida.setStyleSheet("font-size: 16pt; color: #4CAF50; margin-bottom: 20px; font-family: Georgia, serif;")
        main_layout.addWidget(frase_bienvenida)
        
        subtitulo = QLabel("1. Seleccione los gastos que desea incluir en el análisis:")
        subtitulo.setStyleSheet("font-size: 14pt; margin-top: 15px; margin-bottom: 10px; color: #333333;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitulo)

        control_layout = QHBoxLayout()
        
        btn_select_all = QPushButton("Seleccionar Todos")
        btn_select_all.setObjectName("AuxButton")
        btn_select_all.clicked.connect(self.seleccionar_todos)
        
        btn_deselect_all = QPushButton("Deseleccionar Todos")
        btn_deselect_all.setObjectName("AuxButton")
        btn_deselect_all.clicked.connect(self.deseleccionar_todos)
        
        control_layout.addWidget(btn_select_all)
        control_layout.addWidget(btn_deselect_all)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(control_layout)

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
        btn_confirmar.setObjectName("BtnConfirm") 
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
# VENTANA Principal (Contenedor de Pila)
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
    
    # Aplicar Georgia como fuente base si está disponible
    app.setFont(QFont("Georgia", 10))
    
    main_window = MainWindow()
    main_window.show()
    app.exec()