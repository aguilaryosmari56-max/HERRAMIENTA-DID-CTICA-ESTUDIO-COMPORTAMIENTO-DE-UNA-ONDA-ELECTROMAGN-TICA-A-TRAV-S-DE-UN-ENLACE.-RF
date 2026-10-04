import sys
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QFrame)
from PyQt6.QtCore import Qt

class GraficoOnda2D(FigureCanvas):
    def __init__(self):
        self.fig, (self.ax_h, self.ax_v) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
        super().__init__(self.fig)
        self.fig.tight_layout(pad=3.0)
    def actualizar_grafico(self, angulo_tx, magnitud=1.0):
        # Limpiar ejes
        self.ax_h.clear()
        self.ax_v.clear()
        # Datos de la onda (Distancia d)
        d = np.linspace(0, 10, 500)
        rad = np.radians(angulo_tx)
        
        # Cálculo de componentes máximos
        eh_max = magnitud * np.cos(rad)
        ev_max = magnitud * np.sin(rad)
        # Generación de la onda senoidal para cada componente
        onda_h = eh_max * np.sin(d)
        onda_v = ev_max * np.sin(d)
        # Gráfico Horizontal
        self.ax_h.plot(d, onda_h, color='blue', label=f'Eh (Max: {eh_max:.2f})')
        self.ax_h.axhline(0, color='black', lw=1)
        self.ax_h.set_ylabel('Amplitud H (X)')
        self.ax_h.set_title('Componente de Polarización Horizontal')
        self.ax_h.legend(loc='upper right')
        self.ax_h.grid(True, linestyle='--', alpha=0.7)
        # Gráfico Vertical
        self.ax_v.plot(d, onda_v, color='green', label=f'Ev (Max: {ev_max:.2f})')
        self.ax_v.axhline(0, color='black', lw=1)
        self.ax_v.set_ylabel('Amplitud V (Z)')
        self.ax_v.set_xlabel('Distancia de Propagación')
        self.ax_v.set_title('Componente de Polarización Vertical')
        self.ax_v.legend(loc='upper right')
        self.ax_v.grid(True, linestyle='--', alpha=0.7)
        self.draw()
class CalculadoraAntenas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Polarización de Antenas")
        self.setGeometry(100, 100, 900, 650)
        self.initUI()
    def initUI(self):
        layout_principal = QHBoxLayout()
        # --- Panel de Controles ---
        panel_control = QVBoxLayout()
        # Configuración Tx
        grupo_tx = QGroupBox("Antena 1 (Transmisora)")
        lyt_tx = QVBoxLayout()
        lyt_tx.addWidget(QLabel("Ángulo de Inclinación (θ°):"))
        self.input_ang = QLineEdit("45")
        lyt_tx.addWidget(self.input_ang)
        lyt_tx.addWidget(QLabel("Magnitud del Campo (E):"))
        self.input_mag = QLineEdit("1.0")
        lyt_tx.addWidget(self.input_mag)
        grupo_tx.setLayout(lyt_tx)      
        # Botón
        self.btn_calc = QPushButton("Calcular y Graficar Onda")
        self.btn_calc.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.ejecutar)
        # Resultados
        self.res_label = QLabel("Resultados:\nEh: -\nEv: -")
        self.res_label.setStyleSheet("background: #fdfdfd; border: 1px solid #ccc; padding: 10px;")
        panel_control.addWidget(grupo_tx)
        panel_control.addWidget(self.btn_calc)
        panel_control.addWidget(self.res_label)
        panel_control.addStretch()
        # --- Panel de Gráfica ---
        self.canvas = GraficoOnda2D()
        layout_principal.addLayout(panel_control, 1)
        layout_principal.addWidget(self.canvas, 2)    
        self.setLayout(layout_principal)
        self.ejecutar() # Cálculo inicial
    def ejecutar(self):
        try:
            angulo = float(self.input_ang.text())
            magnitud = float(self.input_mag.text())
            
            rad = np.radians(angulo)
            eh = magnitud * np.cos(rad)
            ev = magnitud * np.sin(rad)
            self.res_label.setText(f"<b>Resultados:</b><br>Eh (Horizontal): {eh:.4f}<br>Ev (Vertical): {ev:.4f}")
            self.canvas.actualizar_grafico(angulo, magnitud)
            
        except ValueError:
            self.res_label.setText("Error: Ingrese valores numéricos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CalculadoraAntenas()
    ventana.show()
    sys.exit(app.exec())