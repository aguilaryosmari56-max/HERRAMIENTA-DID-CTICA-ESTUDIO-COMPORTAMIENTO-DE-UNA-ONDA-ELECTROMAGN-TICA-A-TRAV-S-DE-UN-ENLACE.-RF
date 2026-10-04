import sys
import math

import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class CalculadoraPolarizacion(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simulador de Polarización de Antenas')
        self.setGeometry(100, 100, 900, 500)

        # Layout Principal (Horizontal)
        layout_principal = QHBoxLayout()
        
        # --- PANEL IZQUIERDO (CONTROLES) ---
        panel_control = QVBoxLayout()
        
        lbl_titulo = QLabel("Configuración del Campo")
        lbl_titulo.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        panel_control.addWidget(lbl_titulo)

        panel_control.addWidget(QLabel("Magnitud del Campo (E):"))
        self.input_e = QLineEdit()
        self.input_e.setPlaceholderText("Ej: 10")
        self.input_e.setText("10")
        panel_control.addWidget(self.input_e)

        panel_control.addWidget(QLabel("Ángulo de Inclinación (θ°):"))
        self.input_angulo = QLineEdit()
        self.input_angulo.setPlaceholderText("Ej: 45")
        self.input_angulo.setText("45")
        panel_control.addWidget(self.input_angulo)

        self.btn_calcular = QPushButton("Actualizar Gráfica")
        self.btn_calcular.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        self.btn_calcular.clicked.connect(self.graficar)
        panel_control.addWidget(self.btn_calcular)

        # Resultados
        self.res_h = QLabel("Eh (Horizontal): -")
        self.res_v = QLabel("Ev (Vertical): -")
        panel_control.addWidget(self.res_h)
        panel_control.addWidget(self.res_v)
        
        panel_control.addStretch()
        
        # --- PANEL DERECHO (GRÁFICA) ---
        self.figura, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvas(self.figura)
        
        # Agregar paneles al layout principal
        layout_principal.addLayout(panel_control, 1)
        layout_principal.addWidget(self.canvas, 3)

        self.setLayout(layout_principal)
        self.graficar() # Carga inicial

    def graficar(self):
        try:
            e = float(self.input_e.text())
            angulo_deg = float(self.input_angulo.text())
            angulo_rad = math.radians(angulo_deg)

            # Cálculos
            eh = e * math.cos(angulo_rad)
            ev = e * math.sin(angulo_rad)

            # Actualizar Etiquetas
            self.res_h.setText(f"<b>Eh (Horizontal):</b> {eh:.2f}")
            self.res_v.setText(f"<b>Ev (Vertical):</b> {ev:.2f}")

            # Configuración de la Gráfica
            self.ax.clear()
            self.ax.set_title(f"Vectores de Campo Eléctrico (θ = {angulo_deg}°)")
            
            # Dibujar componentes y vector resultante
            self.ax.quiver(0, 0, eh, 0, angles='xy', scale_units='xy', scale=1, color='blue', label='Componente H')
            self.ax.quiver(0, 0, 0, ev, angles='xy', scale_units='xy', scale=1, color='green', label='Componente V')
            self.ax.quiver(0, 0, eh, ev, angles='xy', scale_units='xy', scale=1, color='red', label='Vector Total E')

            # Ajustes de ejes
            limite = e * 1.2
            self.ax.set_xlim([-limite/4, limite])
            self.ax.set_ylim([-limite/4, limite])
            self.ax.axhline(0, color='black', linewidth=0.5)
            self.ax.axvline(0, color='black', linewidth=0.5)
            self.ax.grid(True, linestyle='--', alpha=0.6)
            self.ax.legend()
            
            self.canvas.draw()

        except ValueError:
            self.res_h.setText("Error: Ingrese números válidos")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = CalculadoraPolarizacion()
    ventana.show()
    sys.exit(app.exec())