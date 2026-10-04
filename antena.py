import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFrame, QSlider, QGroupBox, QFormLayout)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- Estilos CSS para PyQt6 (Dark Mode Profesional) ---
ESTILO_UI = """
    QMainWindow { background-color: #121212; }
    QGroupBox { 
        color: #bcff00; font-weight: bold; font-family: 'Segoe UI';
        border: 2px solid #333; border-radius: 8px; margin-top: 15px; padding-top: 10px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
    QLabel { color: #e0e0e0; font-family: 'Segoe UI'; font-size: 13px;}
    QLineEdit { 
        background-color: #1e1e1e; color: white; border: 1px solid #444; 
        padding: 6px; border-radius: 4px; font-family: 'Consolas';
    }
    QLineEdit:focus { border: 1px solid #bcff00; }
    QSlider::groove:horizontal { border: 1px solid #333; height: 8px; background: #1e1e1e; border-radius: 4px; }
    QSlider::handle:horizontal { 
        background: #bcff00; border: 1px solid #333; width: 18px; 
        margin: -6px 0; border-radius: 9px; 
    }
    QPushButton { 
        background-color: #bcff00; color: black; font-weight: bold; 
        font-family: 'Segoe UI'; font-size: 14px; border-radius: 6px; padding: 12px; margin-top: 15px;
    }
    QPushButton:hover { background-color: #d4ff55; }
    QPushButton:pressed { background-color: #a3d900; }
    #ValorLabel { color: #00f2ff; font-family: 'Consolas'; font-weight: bold; }
"""

class ScientificCanvas(FigureCanvas):
    """Lienzo de Matplotlib optimizado para renderizado 3D en tiempo real."""
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 8), facecolor='#121212', dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Parámetros físicos internos (valores por defecto)
        self.z = np.linspace(0, 10, 500) # Eje de propagación
        self.time = 0
        self.k = 2 * np.pi / 2  # Número de onda (proporcional a frecuencia)
        self.w = 2 * np.pi      # Frecuencia angular
        
        # Componentes del campo E (Amplitud y Fase)
        self.Amplitud_H = 1.0 # Ex0
        self.Amplitud_V = 0.5 # Ey0
        self.Fase_V_rad = 0.0  # Desfase de Ey respecto a Ex
        
        # Factor de escala (calculado por la UI basado en distancia/ganancia)
        self.factor_escala_global = 1.0

    def actualizar_onda(self):
        self.ax.clear()
        self.ax.set_facecolor('#121212')
        
        # Escalar amplitudes locales basadas en los cálculos de RF
        Eh0 = self.Amplitud_H * self.factor_escala_global
        Ev0 = self.Amplitud_V * self.factor_escala_global
        
        # --- Cálculo de Campos Eléctricos (Ecuaciones de Maxwell simplificadas) ---
        # Componente Horizontal (Eje X)
        Ex = Eh0 * np.cos(self.k * self.z - self.w * self.time)
        # Componente Vertical (Eje Y) con desfase
        Ey = Ev0 * np.cos(self.k * self.z - self.w * self.time + self.Fase_V_rad)
        
        # --- Visualización de Proyecciones ---
        # Proyección Horizontal (Cian, fondo)
        self.ax.plot(self.z, Ex, zs=-2, zdir='z', color='#00f2ff', alpha=0.2, lw=1)
        # Proyección Vertical (Rosa, atrás)
        self.ax.plot(self.z, Ey, zs=2, zdir='y', color='#ff0077', alpha=0.2, lw=1)
        
        # --- Vector E Resultante (Verde Neón, principal) ---
        self.ax.plot(self.z, Ex, Ey, color='#bcff00', lw=2.5, label='Campo E Resultante', zorder=10)
        
        # --- Dibujar la Antena (Simplificada como un array direccional) ---
        # Representamos la antena en z=0
        self.ax.scatter([0], [0], [0], color='#bcff00', s=100, marker='D', zorder=20)
        self.ax.plot([0, 0], [-1, 1], [0, 0], color='#444', lw=4, alpha=0.5) # Estructura física

        # Estética científica de laboratorio
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-2, 2)
        self.ax.set_zlim(-2, 2)
        self.ax.set_xlabel('Distancia (Z)', color='white')
        self.ax.set_ylabel('Eje Horizontal (X)', color='#00f2ff')
        self.ax.set_zlabel('Eje Vertical (Y)', color='#ff0077')
        self.ax.set_title("Animación de Campo EM - Onda Plana", color='white', fontsize=14)
        
        # Ocultar paneles para minimalismo neón
        self.ax.xaxis.pane.set_visible(False)
        self.ax.yaxis.pane.set_visible(False)
        self.ax.zaxis.pane.set_visible(False)
        self.ax.grid(color='#333', linestyle='--', alpha=0.5)
        
        self.draw()

class AntennaFieldPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AntennaField Pro - Simulador de RF y Polarización 3D")
        self.setMinimumSize(1300, 900)
        self.setStyleSheet(ESTILO_UI)

        # Widget central y layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        h_layout = QHBoxLayout(main_widget)

        # =========================================================
        # --- PANEL DE CONTROLES (IZQUIERDA) ---
        # =========================================================
        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(350)
        v_layout_controls = QVBoxLayout(self.control_panel)
        v_layout_controls.setContentsMargins(10, 10, 10, 10)

        # 1. Grupo de Parámetros de Antena/RF
        group_rf = QGroupBox("Parámetros de RF (Cálculo Intensidad)")
        form_rf = QFormLayout(group_rf)
        self.in_ganancia = QLineEdit("15") # dBi
        self.in_voltaje = QLineEdit("10")   # V (suponemos V_peak alimentado)
        self.in_frecuencia = QLineEdit("2.4") # GHz
        self.in_distancia = QLineEdit("50")  # Metros
        form_rf.addRow("Ganancia (dBi):", self.in_ganancia)
        form_rf.addRow("Voltaje Fuente (V):", self.in_voltaje)
        form_rf.addRow("Frecuencia (GHz):", self.in_frecuencia)
        form_rf.addRow("Distancia Punto (m):", self.in_distancia)
        v_layout_controls.addWidget(group_rf)

        # 2. Grupo de Polarización (Entrada Gráfica Directa)
        group_pol = QGroupBox("Configuración de Polarización Directa")
        v_layout_pol = QVBoxLayout(group_pol)
        
        # Sliders para controlar qué tanto radia en cada eje
        self.add_slider_control(v_layout_pol, "Amplitud Horizontal (Eh)", 0, 100, 100, "lbl_val_eh")
        self.add_slider_control(v_layout_pol, "Amplitud Vertical (Ev)", 0, 100, 0, "lbl_val_ev")
        self.add_slider_control(v_layout_pol, "Desfase V (Grados)", -180, 180, 0, "lbl_val_fase")
        
        v_layout_controls.addWidget(group_pol)
        
        # 3. Grupo de Ángulo de Observación (Direccionalidad simplificada)
        group_angle = QGroupBox("Ángulo de Observación (Direccionalidad)")
        v_layout_angle = QVBoxLayout(group_angle)
        self.add_slider_control(v_layout_angle, "Ángulo Off-Axis (θ)", 0, 90, 0, "lbl_val_theta")
        v_layout_controls.addWidget(group_angle)

        # Botón de Cálculo y Actualización
        self.btn_apply = QPushButton("CALCULAR Y SIMULAR FIELD")
        self.btn_apply.clicked.connect(self.ejecutar_calculos_rf)
        v_layout_controls.addWidget(self.btn_apply)
        
        # Panel de Resultados (Lectura)
        group_res = QGroupBox("Resultados Calculados")
        form_res = QFormLayout(group_res)
        self.res_lambda = QLabel("-- m")
        self.res_lambda.setStyleSheet("color: #00f2ff;")
        self.res_campo_e = QLabel("-- V/m")
        self.res_campo_e.setStyleSheet("color: #bcff00; font-weight: bold;")
        self.res_pol_tipo = QLabel("Lineal H")
        form_res.addRow("Longitud Onda (λ):", self.res_lambda)
        form_res.addRow("Campo E Peak (Friis):", self.res_campo_e)
        form_res.addRow("Tipo Polarización:", self.res_pol_tipo)
        v_layout_controls.addWidget(group_res)

        v_layout_controls.addStretch()

        # =========================================================
        # --- PANEL DE VISUALIZACIÓN (DERECHA) ---
        # =========================================================
        self.canvas = ScientificCanvas(self)
        
        # Integrar paneles al layout principal
        h_layout.addWidget(self.control_panel)
        h_layout.addWidget(self.canvas)

        # --- Timer para la Animación (30 FPS) ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.avanzar_animacion)
        self.timer.start(33)

        # Ejecutar cálculo inicial
        self.ejecutar_calculos_rf()

    def add_slider_control(self, layout, name, min_v, max_v, default, label_id):
        h_layout = QHBoxLayout()
        label_name = QLabel(f"{name}:")
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(default)
        label_value = QLabel(str(default))
        label_value.setObjectName("ValorLabel")
        setattr(self, label_id, label_value) # Guardar referencia
        h_layout.addWidget(label_name)
        h_layout.addWidget(slider)
        h_layout.addWidget(label_value)
        layout.addLayout(h_layout)
        # Conectar actualización de etiqueta
        slider.valueChanged.connect(lambda v: label_value.setText(str(v)))
        # Guardar referencia al slider
        setattr(self, f"slider_{label_id.replace('lbl_val_', '')}", slider)

    def ejecutar_calculos_rf(self):
        """Usa las entradas de texto para calcular parámetros físicos reales y escalar la onda."""
        try:
            # 1. Leer entradas numéricas
            G_dBi = float(self.in_ganancia.text())
            V_fuente = float(self.in_voltaje.text())
            f_GHz = float(self.in_frecuencia.text())
            R_m = float(self.in_distancia.text())
            
            # Impedancia del espacio libre (Ohm)
            Z0 = 377 
            
            # 2. Cálculos básicos de RF
            # Frecuencia en Hz y Longitud de onda
            f_Hz = f_GHz * 1e9
            c = 3e8
            lamda = c / f_Hz
            self.res_lambda.setText(f"{lamda:.4f} m")
            
            # Ganancia lineal
            G_linear = 10**(G_dBi / 10)
            
            # Potencia Radiada (Simplificación: asumimos antena dipolo ideal y V fuente es V peak en antena)
            # P = V^2 / (2 * R_antena). Asumimos R_antena=73 Ohm para dipolo.
            P_radiada = (V_fuente**2) / (2 * 73)
            
            # 3. Ecuación de Friis para Campo Eléctrico en punto R (V/m)
            # Densidad de potencia S = (P * G) / (4 * PI * R^2)
            # S = E^2 / (2 * Z0)  =>  E = sqrt(2 * S * Z0)
            
            if R_m <= 0: R_m = 0.1 # Evitar división por cero
                
            S_densidad = (P_radiada * G_linear) / (4 * np.pi * (R_m**2))
            E_peak = np.sqrt(2 * S_densidad * Z0)
            
            self.res_campo_e.setText(f"{E_peak:.4f} V/m")

            # --- Aplicar Direccionalidad (Ángulo off-axis) ---
            theta_deg = self.slider_theta.value()
            # Modelo simplificado de diagrama de radiación: cos(theta)
            factor_angular = np.cos(np.radians(theta_deg))
            if factor_angular < 0: factor_angular = 0 # Solo radiación frontal

            # 4. Actualizar el Canvas 3D con los valores físicos
            # Usamos E_peak como el factor de escala que multiplica las amplitudes relativas de los sliders
            self.canvas.factor_escala_global = E_peak * factor_angular
            
            # Actualizar frecuencia interna de simulación (relativa para visualización)
            self.canvas.k = 2 * np.pi / (lamda * 10) # Escalado para que quepa en z=10
            self.canvas.w = 2 * np.pi * 1 # Velocidad angular de animación

            self.actualizar_parametros_polarizacion()

        except ValueError:
            self.res_campo_e.setText("Error Entrada")

    def actualizar_parametros_polarizacion(self):
        """Lee los sliders gráficos y actualiza la forma de la onda."""
        # Leer amplitudes relativas (0-100) y normalizar
        eh_raw = self.slider_eh.value()
        ev_raw = self.slider_ev.value()
        
        total = np.sqrt(eh_raw**2 + ev_raw**2)
        if total == 0: eh_norm, ev_norm = 1.0, 0.0 # Por defecto H
        else: eh_norm, ev_norm = eh_raw/total, ev_raw/total
            
        self.canvas.Amplitud_H = eh_norm
        self.canvas.Amplitud_V = ev_norm
        
        fase_deg = self.slider_fase.value()
        self.canvas.Fase_V_rad = np.radians(fase_deg)
        
        # Determinar tipo de polarización (Lectura)
        tipo = "Lineal MIX"
        if ev_raw == 0: tipo = "Lineal Horizontal"
        elif eh_raw == 0: tipo = "Lineal Vertical"
        elif eh_raw == ev_raw and fase_deg == 90: tipo = "Circular Derecha (RHCP)"
        elif eh_raw == ev_raw and fase_deg == -90: tipo = "Circular Izquierda (LHCP)"
        elif fase_deg != 0 and fase_deg != 180 and fase_deg != -180: tipo = "Elíptica"
        
        self.res_pol_tipo.setText(tipo)

    def avanzar_animacion(self):
        """Paso de tiempo de la simulación."""
        # Si cambiaron los sliders, actualizar antes del frame
        self.actualizar_parametros_polarizacion()
        self.canvas.time += 0.1 # Velocidad de la onda
        self.canvas.actualizar_onda()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Base moderna
    window = AntennaFieldPro()
    window.show()
    sys.exit(app.exec())