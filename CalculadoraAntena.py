import sys
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class CalculadoraAntena(QWidget):
    def __init__(self):
        super().__init__()
        self.eh = 0.0
        self.ev = 0.0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculadora de Polarización - PyQt6')
        self.setGeometry(100, 100, 1000, 600)

        main_layout = QHBoxLayout()
        panel_control = QVBoxLayout()
        
        # Estilos CSS para evitar usar métodos inexistentes
        self.setStyleSheet("""
            QLabel { font-size: 13px; margin-bottom: 2px; }
            QLineEdit { padding: 8px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 10px; }
            QPushButton { background-color: #3498db; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton#btnPdf { background-color: #e67e22; }
        """)

        # Inputs
        panel_control.addWidget(QLabel("<b>Magnitud del Campo (E):</b>"))
        self.input_e = QLineEdit()
        self.input_e.setPlaceholderText("Ej: 100")
        panel_control.addWidget(self.input_e)

        panel_control.addWidget(QLabel("<b>Ángulo de Inclinación (°):</b>"))
        self.input_angulo = QLineEdit()
        self.input_angulo.setPlaceholderText("Ej: 45")
        panel_control.addWidget(self.input_angulo)

        self.btn_calcular = QPushButton("CALCULAR Y GRAFICAR")
        self.btn_calcular.clicked.connect(self.actualizar_grafica)
        panel_control.addWidget(self.btn_calcular)

        # Resultados con padding vía StyleSheet
        self.lbl_res = QLabel("Resultados:\nEh: -\nEv: -")
        self.lbl_res.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin-top: 10px;")
        panel_control.addWidget(self.lbl_res)

        self.btn_pdf = QPushButton("DESCARGAR REPORTE PDF")
        self.btn_pdf.setObjectName("btnPdf")
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.clicked.connect(self.exportar_pdf)
        panel_control.addWidget(self.btn_pdf)
        
        panel_control.addStretch()

        # Configuración de Gráfica
        self.figure, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvas(self.figure)
        
        main_layout.addLayout(panel_control, 1)
        main_layout.addWidget(self.canvas, 2)
        self.setLayout(main_layout)

    def actualizar_grafica(self):
        try:
            e = float(self.input_e.text())
            theta_deg = float(self.input_angulo.text())
            theta_rad = math.radians(theta_deg)

            self.eh = e * math.cos(theta_rad)
            self.ev = e * math.sin(theta_rad)

            self.lbl_res.setText(f"<b>Componentes:</b><br>Horizontal (Eh): {self.eh:.3f}<br>Vertical (Ev): {self.ev:.3f}")

            self.ax.clear()
            # Dibujar vectores componentes
            self.ax.quiver(0, 0, self.eh, 0, angles='xy', scale_units='xy', scale=1, color='blue', alpha=0.3, label='Eh')
            self.ax.quiver(0, 0, 0, self.ev, angles='xy', scale_units='xy', scale=1, color='green', alpha=0.3, label='Ev')
            # Dibujar vector resultante
            self.ax.quiver(0, 0, self.eh, self.ev, angles='xy', scale_units='xy', scale=1, color='red', label='Vector E')
            
            lim = e * 1.2
            self.ax.set_xlim([-lim, lim])
            self.ax.set_ylim([-lim, lim])
            self.ax.axhline(0, color='black', lw=1)
            self.ax.axvline(0, color='black', lw=1)
            self.ax.grid(True, linestyle=':')
            self.ax.legend()
            self.ax.set_title(f"Polarización de Antena a {theta_deg}°")
            
            self.canvas.draw()
            self.btn_pdf.setEnabled(True)

        except ValueError:
            QMessageBox.warning(self, "Datos incorrectos", "Asegúrate de ingresar solo números.")

    def exportar_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "Reporte_Antena.pdf", "PDF Files (*.pdf)")
        if path:
            temp_img = "temp_plot.png"
            self.figure.savefig(temp_img)

            c = canvas.Canvas(path, pagesize=letter)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, 750, "Reporte de Cálculo de Antena")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, 720, f"Magnitud (E): {self.input_e.text()}")
            c.drawString(50, 705, f"Ángulo: {self.input_angulo.text()}°")
            c.line(50, 695, 550, 695)
            
            c.drawString(50, 675, f"Componente Horizontal (Eh): {self.eh:.4f}")
            c.drawString(50, 660, f"Componente Vertical (Ev): {self.ev:.4f}")

            c.drawImage(temp_img, 100, 300, width=400, height=300)
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(50, 50, "Generado por Calculadora de Polarización PyQt6.")
            
            c.save()
            QMessageBox.information(self, "PDF Guardado", "El reporte se ha generado con éxito.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculadoraAntena()
    window.show()
    sys.exit(app.exec())