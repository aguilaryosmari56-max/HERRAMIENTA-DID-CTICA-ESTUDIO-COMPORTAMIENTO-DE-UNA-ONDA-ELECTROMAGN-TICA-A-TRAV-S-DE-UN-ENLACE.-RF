import sys
import math
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Integración de Matplotlib con PyQt6
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Generación de PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class CalculadoraAntena3D(QWidget):
    def __init__(self):
        super().__init__()
        # Variables para almacenar resultados
        self.E_total = 0.0
        self.theta_deg = 0.0
        self.Eh = 0.0
        self.Ev = 0.0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simulador de Polarización Lineal ')
        self.setGeometry(100, 100, 1100, 700)

        # --- Hoja de Estilo (CSS moderno) ---
        self.setStyleSheet("""
            QWidget { font-family: 'Segoe UI', sans-serif; font-size: 14px; background-color: #f4f7f6; }
            QGroupBox { font-weight: bold; border: 2px solid #3498db; border-radius: 8px; padding-top: 15px; margin-top: 10px; background-color: white; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; color: #3498db; }
            QLabel { color: #2c3e50; }
            QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; background-color: #fbfcfc; }
            QLineEdit:focus { border: 2px solid #3498db; }
            QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; text-transform: uppercase; }
            QPushButton#btnCalcular { background-color: #3498db; color: white; border: none; }
            QPushButton#btnCalcular:hover { background-color: #2980b9; }
            QPushButton#btnPdf { background-color: #e74c3c; color: white; border: none; margin-top: 10px;}
            QPushButton#btnPdf:hover { background-color: #c0392b; }
            QPushButton#btnPdf:disabled { background-color: #95a5a6; }
            QLabel#lblRes { background-color: #ecf0f1; padding: 15px; border-radius: 4px; border-left: 5px solid #27ae60; color: #27ae60; font-weight: bold;}
        """)

        # --- Layout Principal ---
        main_layout = QHBoxLayout()
        
        # ==========================================
        # PANEL IZQUIERDO - Controles y Resultados
        # ==========================================
        panel_control = QVBoxLayout()
        panel_control.setSpacing(15)

        # Grupo de Entrada de Datos
        grupo_entrada = QGroupBox("Parámetros de la Onda")
        layout_entrada = QVBoxLayout()
        
        layout_entrada.addWidget(QLabel("Magnitud Campo Eléctrico Total (E):"))
        self.input_e = QLineEdit()
        self.input_e.setPlaceholderText("Ej: 120.0")
        layout_entrada.addWidget(self.input_e)

        layout_entrada.addWidget(QLabel("Ángulo de Inclinación (θ) en Grados:"))
        self.input_angulo = QLineEdit()
        self.input_angulo.setPlaceholderText("Ej: 45.0 (0°=Horiz, 90°=Vert)")
        layout_entrada.addWidget(self.input_angulo)
        
        self.btn_calcular = QPushButton("Calcular y Graficar 3D")
        self.btn_calcular.setObjectName("btnCalcular")
        self.btn_calcular.clicked.connect(self.procesar_calculo)
        layout_entrada.addWidget(self.btn_calcular)
        
        grupo_entrada.setLayout(layout_entrada)
        panel_control.addWidget(grupo_entrada)

        # Grupo de Resultados
        grupo_resultados = QGroupBox("Componentes Calculados")
        layout_resultados = QVBoxLayout()
        
        self.lbl_resultados = QLabel("Introduce datos y pulsa calcular...")
        self.lbl_resultados.setObjectName("lblRes")
        self.lbl_resultados.setWordWrap(True)
        self.lbl_resultados.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_resultados.addWidget(self.lbl_resultados)
        
        grupo_resultados.setLayout(layout_resultados)
        panel_control.addWidget(grupo_resultados)

        # Botón PDF
        self.btn_pdf = QPushButton("Descargar Reporte PDF con Gráfica")
        self.btn_pdf.setObjectName("btnPdf")
        self.btn_pdf.setEnabled(False) # Deshabilitado hasta que haya cálculo
        self.btn_pdf.clicked.connect(self.generar_pdf)
        panel_control.addWidget(self.btn_pdf)

        panel_control.addStretch() # Empuja todo hacia arriba
        
        # ==========================================
        # PANEL DERECHO - Gráfica 3D
        # ==========================================
        # Creamos la figura de Matplotlib y el canvas para 3D
        self.figure = plt.figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # Añadir paneles al layout principal
        main_layout.addLayout(panel_control, 1) # Proporción 1
        main_layout.addWidget(self.canvas, 2)  # Proporción 2 (más grande)

        self.setLayout(main_layout)

    def procesar_calculo(self):
        """Obtiene datos, hace matemáticas, actualiza label y gráfica."""
        try:
            # 1. Obtener y validar entradas
            txt_e = self.input_e.text()
            txt_angulo = self.input_angulo.text()
            
            if not txt_e or not txt_angulo:
                raise ValueError("Campos vacíos")
                
            self.E_total = float(txt_e)
            self.theta_deg = float(txt_angulo)
            
            if self.E_total <= 0:
                raise ValueError("La magnitud debe ser positiva")

            # 2. Cálculos Matemáticos
            theta_rad = math.radians(self.theta_deg)
            # Eh = E * cos(theta), Ev = E * sin(theta)
            self.Eh = self.E_total * math.cos(theta_rad)
            self.Ev = self.E_total * math.sin(theta_rad)

            # 3. Actualizar Interfaz de usuario
            texto_res = (f"E Total: {self.E_total:.2f}\n"
                         f"Ángulo: {self.theta_deg:.1f}°\n\n"
                         f"Polarización Horizontal (Eh): {self.Eh:.3f}\n"
                         f"Polarización Vertical (Ev): {self.Ev:.3f}")
            self.lbl_resultados.setText(texto_res)
            
            # Habilitar botón PDF
            self.btn_pdf.setEnabled(True)
            
            # 4. Actualizar Gráfica 3D
            self.actualizar_grafica_3d()

        except ValueError as e:
            QMessageBox.warning(self, "Error de Entrada", f"Por favor, introduce números válidos.\nDetalle: {e}")
            self.btn_pdf.setEnabled(False)
            self.lbl_resultados.setText("Error en los datos.")

    def actualizar_grafica_3d(self):
        """Dibuja el vector E en un espacio 3D."""
        self.figure.clear() # Limpiar figura anterior
        
        # Crear ejes 3D
        ax = self.figure.add_subplot(111, projection='3d')
        
        # Definir el vector resultante E. 
        # Asumimos que la onda se propaga en el eje Z. 
        # La polarización está en el plano X-Y.
        # X = Horizontal, Y = Vertical
        
        # Coordenadas del vector [origen_x, origen_y, origen_z, componentes_x, componentes_y, componentes_z]
        # Dibujamos el vector desde el origen (0,0,0) hasta (Eh, Ev, 0)
        ax.quiver(0, 0, 0, self.Eh, self.Ev, 0, color='red', linewidth=3, arrow_length_ratio=0.1, label='Vector E Resultante')
        
        # Dibujar líneas auxiliares para los componentes en el plano X-Y
        ax.plot([0, self.Eh], [0, 0], [0, 0], 'b--', alpha=0.5, label='Componente Eh (X)')
        ax.plot([0, 0], [0, self.Ev], [0, 0], 'g--', alpha=0.5, label='Componente Ev (Y)')
        # Línea desde Eh hasta el punto final
        ax.plot([self.Eh, self.Eh], [0, self.Ev], [0, 0], 'k:', alpha=0.3)
        ax.plot([0, self.Eh], [self.Ev, self.Ev], [0, 0], 'k:', alpha=0.3)

        # Configuración de límites de los ejes (ligeramente más grandes que E para que se vea bien)
        limite = self.E_total * 1.1
        ax.set_xlim([-limite, limite])
        ax.set_ylim([-limite, limite])
        ax.set_zlim([-limite/2, limite/2]) # El eje Z no tiene componente pero da perspectiva

        # Etiquetas de los ejes
        ax.set_xlabel('Eje Horizontal (X)')
        ax.set_ylabel('Eje Vertical (Y)')
        ax.set_zlabel('Dirección Propagación (Z)')
        
        ax.set_title(f'Vector de Polarización E a {self.theta_deg}°\n(Plano X-Y)')
        ax.legend(loc='upper left', fontsize='small')
        
        # Ajustar vista inicial para mejor perspectiva
        ax.view_init(elev=20, azim=30)
        
        self.canvas.draw() # Refrescar canvas

    def generar_pdf(self):
        """Exporta cálculos y una captura de la gráfica 3D actual a PDF."""
        # 1. Preguntar dónde guardar el archivo
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte PDF", "Reporte_Polarizacion_3D.pdf", "PDF Files (*.pdf)")
        
        if not file_path:
            return # El usuario canceló

        # 2. Capturar la gráfica actual como imagen temporal
        temp_image_path = "temp_graph_3d.png"
        try:
            self.figure.savefig(temp_image_path, dpi=100, bbox_inches='tight')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo capturar la gráfica.\n{e}")
            return

        # 3. Crear el documento PDF
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter # 8.5x11 pulgadas

            # --- Encabezado ---
            c.setFont("Helvetica-Bold", 20)
            c.setFillColorRGB(0.2, 0.4, 0.6) # Color azul
            c.drawCentredString(width/2, height - 1*inch, "Reporte de Polarización de Antena")
            
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.line(1*inch, height - 1.2*inch, width - 1*inch, height - 1.2*inch)

            # --- Sección de Datos y Cálculos ---
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0, 0, 0)
            text_y = height - 1.7*inch
            c.drawString(1*inch, text_y, "1. Parámetros de Entrada:")
            
            c.setFont("Helvetica", 12)
            text_y -= 0.3*inch
            c.drawString(1.3*inch, text_y, f"• Magnitud del Campo Eléctrico Total (E): {self.E_total:.2f}")
            text_y -= 0.25*inch
            c.drawString(1.3*inch, text_y, f"• Ángulo de Inclinación (θ): {self.theta_deg:.1f} grados")

            text_y -= 0.5*inch
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, text_y, "2. Resultados del Cálculo (Descomposición):")
            
            # Recuadro gris para resultados
            c.setFillColorRGB(0.95, 0.95, 0.95)
            c.rect(1.2*inch, text_y - 0.9*inch, 4*inch, 0.7*inch, fill=1, stroke=0)
            
            c.setFont("Helvetica-Bold", 13)
            c.setFillColorRGB(0.15, 0.6, 0.3) # Verde
            text_y -= 0.4*inch
            c.drawString(1.5*inch, text_y, f"Polarización Horizontal (Eh): {self.Eh:.4f}")
            text_y -= 0.25*inch
            c.drawString(1.5*inch, text_y, f"Polarización Vertical (Ev):   {self.Ev:.4f}")

            # --- Sección de Gráfica ---
            c.setFillColorRGB(0, 0, 0)
            text_y -= 0.8*inch
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, text_y, "3. Visualización del Vector en Espacio 3D:")
            
            # Insertar la imagen temporal de la gráfica
            # c.drawImage(path, x, y, width, height)
            if os.path.exists(temp_image_path):
                # Ajustar tamaño imagen para que quepa en el PDF
                img_width = 6*inch
                img_height = 5*inch
                c.drawImage(temp_image_path, (width - img_width)/2, text_y - 5.2*inch, width=img_width, height=img_height)

            # Pie de página
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColorRGB(0.5, 0.5, 0.5)
            c.drawCentredString(width/2, 0.5*inch, "Generado automáticamente por Simulador Antena 3D PyQt6.")

            # Finalizar y guardar PDF
            c.showPage()
            c.save()
            
            QMessageBox.information(self, "Éxito", f"Reporte PDF guardado correctamente en:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF.\n{e}")
        finally:
            # Borrar la imagen temporal
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

if __name__ == '__main__':
    # Configuración para pantallas de alta resolución (High DPI)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Estilo multiplataforma limpio
    
    window = CalculadoraAntena3D()
    window.show()
    sys.exit(app.exec())