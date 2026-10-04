import sys
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class OndaCanvas(FigureCanvas):
    def __init__(self):
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.configurar_ejes()

    def configurar_ejes(self):
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-3, 3) # Eje de propagación
        self.ax.set_zlim(-1.5, 1.5)
        self.ax.set_xlabel('Horizontal (X)')
        self.ax.set_ylabel('Propagación (Y)')
        self.ax.set_zlabel('Vertical (Z)')
        self.ax.view_init(elev=20, azim=-45)

    def graficar(self, ang1, ang2):
        self.ax.clear()
        self.configurar_ejes()

        # Parámetros de la onda
        y = np.linspace(-2.5, 2.5, 200)
        rad1 = np.radians(ang1)
        rad2 = np.radians(ang2)

        # Magnitudes de componentes para Tx (Antena 1)
        eh1 = np.cos(rad1)
        ev1 = np.sin(rad1)

        # Dibujar la onda viajera (Senoide 3D)
        x_onda = eh1 * np.sin(2 * np.pi * y)
        z_onda = ev1 * np.sin(2 * np.pi * y)
        self.ax.plot(x_onda, y, z_onda, color='red', lw=2, label='Campo Eléctrico (E)')

        # Dibujar vector de la Antena 1 (Tx) en Y = -2.5
        self.ax.quiver(0, -2.5, 0, eh1, 0, ev1, color='darkred', length=1, label='Polarización Tx')
        
        # Dibujar vector de la Antena 2 (Rx) en Y = 2.5
        eh2 = np.cos(rad2)
        ev2 = np.sin(rad2)
        self.ax.quiver(0, 2.5, 0, eh2, 0, ev2, color='blue', length=1, label='Polarización Rx')

        self.ax.legend(loc='upper left', fontsize='small')
        self.draw()

class AppAntena(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Polarización 3D - 2 Antenas")
        self.resize(1100, 700)
        self.initUI()

    def initUI(self):
        layout_principal = QHBoxLayout()
        
        # Panel de Controles
        controles = QVBoxLayout()
        
        # Grupo Antena 1
        g1 = QGroupBox("Antena 1: Transmisora (Tx)")
        l1 = QGridLayout(); g1.setLayout(l1)
        self.input_a1 = QLineEdit("45")
        l1.addWidget(QLabel("Ángulo θ (deg):"), 0, 0)
        l1.addWidget(self.input_a1, 0, 1)
        controles.addWidget(g1)

        # Grupo Antena 2
        g2 = QGroupBox("Antena 2: Receptora (Rx)")
        l2 = QGridLayout(); g2.setLayout(l2)
        self.input_a2 = QLineEdit("0")
        l2.addWidget(QLabel("Ángulo θ (deg):"), 0, 0)
        l2.addWidget(self.input_a2, 0, 1)
        controles.addWidget(g2)

        # Botón
        btn = QPushButton("Calcular y Graficar")
        btn.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold; padding: 10px;")
        btn.clicked.connect(self.actualizar)
        controles.addWidget(btn)

        # Resultados
        self.res = QLabel("<b>Componentes Tx:</b><br>Eh: 0.71<br>Ev: 0.71")
        self.res.setStyleSheet("background: #ecf0f1; padding: 10px; border-radius: 5px;")
        controles.addWidget(self.res)
        
        controles.addStretch()
        
        # Gráfico
        self.canvas = OndaCanvas()
        
        layout_principal.addLayout(controles, 1)
        layout_principal.addWidget(self.canvas, 3)
        self.setLayout(layout_principal)
        self.actualizar()

    def actualizar(self):
        try:
            a1 = float(self.input_a1.text())
            a2 = float(self.input_a2.text())
            
            # Cálculos de componentes (Normalizados a 1)
            eh = np.cos(np.radians(a1))
            ev = np.sin(np.radians(a1))
            
            self.res.setText(f"<b>Componentes Tx:</b><br>Horizontal (Eh): {eh:.2f}<br>Vertical (Ev): {ev:.2f}")
            self.canvas.graficar(a1, a2)
        except ValueError:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppAntena()
    window.show()
    sys.exit(app.exec())