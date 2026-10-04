import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Estilo CSS para la interfaz
ESTILO_DARK = """
    QMainWindow { background-color: #121212; }
    QLabel { color: #00f2ff; font-weight: bold; font-family: 'Segoe UI'; }
    QLineEdit { 
        background-color: #1e1e1e; color: white; 
        border: 1px solid #333; padding: 5px; border-radius: 4px;
    }
    QPushButton { 
        background-color: #bcff00; color: black; 
        font-weight: bold; border-radius: 5px; padding: 10px;
    }
    QPushButton:hover { background-color: #9ecc00; }
    QFrame#ControlPanel { background-color: #1a1a1a; border-right: 1px solid #333; }
"""

class Canvas3D(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6), facecolor='#121212')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#121212')
        super().__init__(self.fig)
        
        self.z = np.linspace(0, 10, 400)
        self.t = 0
        self.ex0, self.ey0, self.fase = 1.0, 1.0, np.pi/2

    def plot_wave(self):
        self.ax.clear()
        k, w = 2 * np.pi / 4, 2 * np.pi
        
        Ex = self.ex0 * np.cos(k * self.z - w * self.t)
        Ey = self.ey0 * np.cos(k * self.z - w * self.t + self.fase)
        
        # Dibujar componentes con transparencias (estilo laboratorio)
        self.ax.plot(self.z, Ex, zs=-2, zdir='z', color='#00f2ff', alpha=0.3) # Plano H
        self.ax.plot(self.z, Ey, zs=2, zdir='y', color='#ff0077', alpha=0.3)  # Plano V
        
        # Vector resultante (E)
        self.ax.plot(self.z, Ex, Ey, color='#bcff00', lw=2.5)
        
        # Configuración estética
        self.ax.set_xlim(0, 10); self.ax.set_ylim(-2, 2); self.ax.set_zlim(-2, 2)
        self.ax.xaxis.pane.set_visible(False); self.ax.yaxis.pane.set_visible(False)
        self.ax.zaxis.pane.set_visible(False)
        self.ax.set_title("Onda Electromagnética en Tiempo Real", color='white')
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Polarización EM - PyQt6 Edition")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(ESTILO_DARK)

        # Layout Principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- Panel de Controles ---
        control_panel = QFrame()
        control_panel.setObjectName("ControlPanel")
        control_panel.setFixedWidth(250)
        control_layout = QVBoxLayout(control_panel)

        control_layout.addWidget(QLabel("AMPLITUD H (Ex)"))
        self.input_ex = QLineEdit("1.0")
        control_layout.addWidget(self.input_ex)

        control_layout.addWidget(QLabel("AMPLITUD V (Ey)"))
        self.input_ey = QLineEdit("1.0")
        control_layout.addWidget(self.input_ey)

        control_layout.addWidget(QLabel("DESFASE (Grados)"))
        self.input_fase = QLineEdit("90")
        control_layout.addWidget(self.input_fase)

        self.btn_update = QPushButton("APLICAR CAMBIOS")
        self.btn_update.clicked.connect(self.update_parameters)
        control_layout.addWidget(self.btn_update)
        control_layout.addStretch()

        # --- Panel de Gráfica ---
        self.canvas = Canvas3D()
        
        layout.addWidget(control_panel)
        layout.addWidget(self.canvas)

        # Timer para la animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def update_parameters(self):
        try:
            self.canvas.ex0 = float(self.input_ex.text())
            self.canvas.ey0 = float(self.input_ey.text())
            self.canvas.fase = np.radians(float(self.input_fase.text()))
        except ValueError:
            print("Error: Ingrese valores numéricos válidos.")

    def animate(self):
        self.canvas.t += 0.05
        self.canvas.plot_wave()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())