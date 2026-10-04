import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton)

class AntennaPolarizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Polarización de Antenas")
        self.setGeometry(100, 100, 900, 600)

        # Widget principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)

        # Panel de Control (Izquierda)
        self.controls = QVBoxLayout()
        
        self.label_ex = QLabel("Amplitud Ex (Horizontal):")
        self.spin_ex = QDoubleSpinBox()
        self.spin_ex.setValue(1.0)
        
        self.label_ey = QLabel("Amplitud Ey (Vertical):")
        self.spin_ey = QDoubleSpinBox()
        self.spin_ey.setValue(1.0)
        
        self.label_phase = QLabel("Desfase (grados):")
        self.spin_phase = QDoubleSpinBox()
        self.spin_phase.setRange(-360, 360)
        self.spin_phase.setValue(90.0)

        self.btn_calc = QPushButton("Calcular y Graficar")
        self.btn_calc.clicked.connect(self.update_plot)

        self.result_label = QLabel("Polarización: Desconocida")
        self.result_label.setStyleSheet("font-weight: bold; color: blue;")

        # Agregar controles al layout
        for w in [self.label_ex, self.spin_ex, self.label_ey, self.spin_ey, 
                  self.label_phase, self.spin_phase, self.btn_calc, self.result_label]:
            self.controls.addWidget(w)
        self.controls.addStretch()

        # Gráfico (Derecha)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.layout.addLayout(self.controls, 1)
        self.layout.addWidget(self.canvas, 3)

        self.update_plot()

    def update_plot(self):
        Ex0 = self.spin_ex.value()
        Ey0 = self.spin_ey.value()
        delta_deg = self.spin_phase.value()
        delta = np.radians(delta_deg)

        # Tiempo y propagación (z)
        t = np.linspace(0, 2 * np.pi, 200)
        Ex = Ex0 * np.cos(t)
        Ey = Ey0 * np.cos(t + delta)

        # Determinar tipo de polarización
        tipo = self.get_polarization_type(Ex0, Ey0, delta_deg)
        self.result_label.setText(f"Polarización: {tipo}")

        # Graficar
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        
        # Elipse de polarización en el plano z=0
        ax.plot(Ex, Ey, 0, label='Traza del vector E', color='red', lw=2)
        
        # Ejes de referencia
        limit = max(Ex0, Ey0, 1)
        ax.set_xlim([-limit, limit])
        ax.set_ylim([-limit, limit])
        ax.set_zlim([0, 1])
        ax.set_xlabel('Ex (Horizontal)')
        ax.set_ylabel('Ey (Vertical)')
        ax.set_title(f"Estado de Polarización ({tipo})")
        
        self.canvas.draw()

    def get_polarization_type(self, Ex, Ey, delta):
        delta = delta % 360
        if delta == 0 or delta == 180:
            return "Lineal"
        elif (delta == 90 or delta == 270) and np.isclose(Ex, Ey):
            sentido = "Circular Izquierda (LHC)" if delta == 90 else "Circular Derecha (RHC)"
            return sentido
        else:
            return "Elíptica"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AntennaPolarizationApp()
    window.show()
    sys.exit(app.exec())