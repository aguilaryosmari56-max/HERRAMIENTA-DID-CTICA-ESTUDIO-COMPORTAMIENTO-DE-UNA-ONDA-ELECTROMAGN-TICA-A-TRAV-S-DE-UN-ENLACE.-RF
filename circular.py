import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFrame, QSlider, QGroupBox, QFormLayout)
from PyQt6.QtCore import QTimer, Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- Estilo Visual ---
ESTILO_CSS = """
    QMainWindow { background-color: #0f0f0f; }
    QGroupBox { 
        color: #00ffaa; font-weight: bold; font-family: 'Segoe UI';
        border: 1px solid #333; border-radius: 5px; margin-top: 15px;
    }
    QLabel { color: #cccccc; font-size: 12px; }
    QLineEdit { 
        background-color: #1a1a1a; color: #fff; border: 1px solid #444; 
        padding: 4px; border-radius: 3px; 
    }
    QPushButton { 
        background-color: #00ffaa; color: #000; font-weight: bold; 
        border-radius: 4px; padding: 10px; margin-top: 10px;
    }
    QPushButton:hover { background-color: #00cc88; }
    #DataRes { color: #ff3366; font-family: 'Consolas'; font-weight: bold; }
"""

class AntennaCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 8), facecolor='#0f0f0f')
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        
        self.z = np.linspace(0, 10, 400)
        self.t = 0
        self.amp_v = 1.0  # Polarización Principal (Vertical)
        self.amp_h = 0.1  # Polarización Cruzada (Horizontal)
        self.fase_rad = 0
        self.scale = 1.0

    def plot_fields(self):
        self.ax.clear()
        self.ax.set_facecolor('#0f0f0f')
        
        # Ecuaciones de onda
        k, w = 2 * np.pi / 3, 2 * np.pi
        
        # Campo Vertical (Deseado)
        Ev = (self.amp_v * self.scale) * np.cos(k * self.z - w * self.t)
        # Campo Horizontal (Polarización Cruzada / Cross-Pol)
        Eh = (self.amp_h * self.scale) * np.cos(k * self.z - w * self.t + self.fase_rad)
        
        # Visualización 3D
        # Proyecciones en los ejes
        self.ax.plot(self.z, np.zeros_like(self.z), Ev, color='#ff3366', alpha=0.4, label='Vertical')
        self.ax.plot(self.z, Eh, np.zeros_like(self.z), color='#3399ff', alpha=0.4, label='Cruzada')
        
        # Vector resultante (Polarización real de la antena)
        self.ax.plot(self.z, Eh, Ev, color='#00ffaa', lw=2)
        
        # Estética
        self.ax.set_xlim(0, 10); self.ax.set_ylim(-2, 2); self.ax.set_zlim(-2, 2)
        self.ax.set_axis_off() # Limpieza total para enfoque en la onda
        self.draw()

class AntennaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antenna Cross-Pol Analyzer Pro")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(ESTILO_CSS)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- Panel Lateral ---
        controls = QFrame()
        controls.setFixedWidth(320)
        c_layout = QVBoxLayout(controls)

        # Entradas de RF
        rf_group = QGroupBox("Parámetros de Diseño")
        rf_form = QFormLayout(rf_group)
        self.in_gain = QLineEdit("20") # dBi
        self.in_volt = QLineEdit("12") # V
        self.in_freq = QLineEdit("5.8") # GHz
        self.in_dist = QLineEdit("100") # m
        rf_form.addRow("Ganancia (dBi):", self.in_gain)
        rf_form.addRow("Voltaje (V):", self.in_volt)
        rf_form.addRow("Frecuencia (GHz):", self.in_freq)
        rf_form.addRow("Distancia (m):", self.in_dist)
        c_layout.addWidget(rf_group)

        # Sliders de Polarización
        pol_group = QGroupBox("Geometría y Cruzamiento")
        pol_v = QVBoxLayout(pol_group)
        
        self.label_xpd = QLabel("Aislamiento Cross-Pol (XPD): 20 dB")
        self.sl_xpd = QSlider(Qt.Orientation.Horizontal)
        self.sl_xpd.setRange(5, 50); self.sl_xpd.setValue(20)
        
        self.label_angle = QLabel("Ángulo de Desalineación: 0°")
        self.sl_angle = QSlider(Qt.Orientation.Horizontal)
        self.sl_angle.setRange(0, 90); self.sl_angle.setValue(0)
        
        pol_v.addWidget(self.label_xpd); pol_v.addWidget(self.sl_xpd)
        pol_v.addWidget(self.label_angle); pol_v.addWidget(self.sl_angle)
        c_layout.addWidget(pol_group)

        # Resultados
        self.res_label = QLabel("Potencia Recibida: -- dBm\nCampo E: -- V/m")
        self.res_label.setObjectName("DataRes")
        c_layout.addWidget(self.res_label)

        btn_calc = QPushButton("CALCULAR SISTEMA")
        btn_calc.clicked.connect(self.calculate_all)
        c_layout.addWidget(btn_calc)
        c_layout.addStretch()

        # --- Canvas ---
        self.canvas = AntennaCanvas()
        layout.addWidget(controls)
        layout.addWidget(self.canvas)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(30)

    def calculate_all(self):
        try:
            # Física de la Antena
            gain_dbi = float(self.in_gain.text())
            v_src = float(self.in_volt.text())
            freq = float(self.in_freq.text()) * 1e9
            dist = float(self.in_dist.text())
            
            # Ecuación de Friis simplificada
            c = 3e8
            lam = c / freq
            gain_lin = 10**(gain_dbi/10)
            power_tx = (v_src**2) / 100 # Asumiendo impedancia
            
            # Campo E en el punto (V/m)
            e_field = np.sqrt((60 * power_tx * gain_lin)) / dist
            self.canvas.scale = e_field * 10 # Escalar para visualización
            
            # Cálculo de Polarización Cruzada
            xpd_db = self.sl_xpd.value()
            self.label_xpd.setText(f"Aislamiento Cross-Pol (XPD): {xpd_db} dB")
            
            # Relación de amplitudes Eh/Ev = 10^(-XPD/20)
            ratio_crosspol = 10**(-xpd_db/20)
            
            # Efecto del ángulo de desalineación
            theta = np.radians(self.sl_angle.value())
            self.label_angle.setText(f"Ángulo de Desalineación: {self.sl_angle.value()}°")
            
            # Amplitudes resultantes
            self.canvas.amp_v = np.cos(theta)
            self.canvas.amp_h = np.sin(theta) + ratio_crosspol # Suma de desalineación + fuga natural
            
            self.res_label.setText(f"Campo E Peak: {e_field:.4f} V/m\nRatio H/V: {ratio_crosspol:.4f}")

        except Exception as e:
            print(f"Error: {e}")

    def update_anim(self):
        self.canvas.t += 0.05
        self.canvas.plot_fields()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AntennaApp()
    win.show()
    sys.exit(app.exec())