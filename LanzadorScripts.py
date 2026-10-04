import sys
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFrame, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

class LanzadorScripts(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Panel de Control Pro - Ingeniería')
        self.setGeometry(100, 100, 600, 700)
        
        # Estilo CSS modernizado
        self.setStyleSheet("""
            QWidget { background-color: #1e272e; font-family: 'Segoe UI', sans-serif; }
            QLabel#titulo { font-size: 22px; color: #ffffff; font-weight: bold; padding: 10px; }
            
            QPushButton { 
                background-color: #485460; 
                color: white; 
                border-radius: 12px; 
                padding: 20px; 
                font-size: 13px; 
                font-weight: bold;
                border: 2px solid #3c444b;
                text-align: center;
            }
            QPushButton:hover { background-color: #05c46b; border: 2px solid #ffffff; }
            
            QPushButton#btnPDF { 
                background-color: #ff3f34; 
                border: none;
                font-size: 15px;
            }
            QPushButton#btnPDF:hover { background-color: #ff5e57; }

            QPushButton#btnSalir { background-color: #3d3d3d; color: #ef5777; margin-top: 10px; }
        """)

        layout_principal = QVBoxLayout()

        # Título
        titulo = QLabel("SISTEMA DE CONTROL Y ANÁLISIS")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(titulo)

        # Contenedor para la cuadrícula de botones (8 botones)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # Lista de configuraciones (Nombre, Script, Icono opcional)
        scripts = [
            ("Spectrum Analyzer", "SpectrumAnalyzer.py", "telecomunicaciones.png"),
            ("Calculadora Antena", "CalculadoraAntena.py", "antenna.png"),
            ("Gráfico Onda 2D", "GraficoOnda2D.py", "wave.png"),
            ("Simulador RF", "SimRF.py", "chip.png"),
            ("Base de Datos", "DBManager.py", "db.png"),
            ("Polarización Circular", "grafico.py", "map.png"),
            ("Polarización Lineal", "AnimacionAntena3D.py", "gear.png"),
            ("Monitor Red", "NetMonitor.py", "net.png"),
        ]

        # Crear los 8 botones dinámicamente
        for i, (nombre, archivo, icono) in enumerate(scripts):
            btn = QPushButton(f"\n{nombre}")
            # Intentar cargar icono (si existe la carpeta iconos)
            if os.path.exists(f"iconos/{icono}"):
                btn.setIcon(QIcon(f"iconos/{icono}"))
                btn.setIconSize(QSize(40, 40))
            
            btn.clicked.connect(lambda checked, a=archivo: self.ejecutar_script(a))
            
            # Posicionar en grid (2 columnas, 4 filas)
            grid_layout.addWidget(btn, i // 2, i % 2)

        layout_principal.addLayout(grid_layout)

        # --- SECCIÓN REPORTES PDF ---
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("background-color: #485460;")
        layout_principal.addWidget(linea)

        self.btn_pdf = QPushButton(" GENERAR REPORTE TÉCNICO PDF")
        self.btn_pdf.setObjectName("btnPDF")
        # Aquí pones el nombre de tu script que muestra el PDF
        self.btn_pdf.clicked.connect(lambda: self.ejecutar_script("VisorManual.py")) 
        layout_principal.addWidget(self.btn_pdf)

        # Botón Salir
        self.btn_salir = QPushButton("Cerrar Sistema")
        self.btn_salir.setObjectName("btnSalir")
        self.btn_salir.clicked.connect(self.close)
        layout_principal.addWidget(self.btn_salir)

        self.setLayout(layout_principal)

    def ejecutar_script(self, nombre_archivo):
        if os.path.exists(nombre_archivo):
            try:
                subprocess.Popen([sys.executable, nombre_archivo])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo ejecutar:\n{e}")
        else:
            QMessageBox.warning(self, "Error", f"Archivo no encontrado: {nombre_archivo}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LanzadorScripts()
    ex.show()
    sys.exit(app.exec())