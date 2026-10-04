import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout, 
                             QVBoxLayout, QLabel, QMessageBox, QMainWindow, QFrame)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QUrl
# Importamos el motor web para el PDF
from PyQt6.QtWebEngineWidgets import QWebEngineView 

class VisorPDF(QMainWindow):
    """Ventana independiente para visualizar el PDF."""
    def __init__(self, ruta_pdf):
        super().__init__()
        self.setWindowTitle("Visor de Documentación")
        self.resize(900, 800)
        
        self.browser = QWebEngineView()
        # Convertimos la ruta local a un formato URL compatible
        ruta_absoluta = os.path.abspath(ruta_pdf)
        self.browser.setUrl(QUrl.fromLocalFile(ruta_absoluta))
        self.setCentralWidget(self.browser)

class LanzadorApps(QMainWindow): # Cambiado a QMainWindow
    def __init__(self):
        super().__init__()
        self.visor = None # Referencia para que no se cierre la ventana al abrirla
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Analizador de Frecuencias')
        # Aumentamos el tamaño para acomodar el banner
        self.setFixedSize(700, 650) 
        
        # --- ESTILOS ---
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QWidget#ContenedorPrincipal { background-color: #1e1e2e; }
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #313244;
            }
            QPushButton:hover { background-color: #f1f1f1; color: #1e1e2e; }
            QLabel#TituloLabel { 
                color: #bac2de; 
                font-size: 20px; 
                font-weight: bold; 
                margin-top: 10px;
                margin-bottom: 10px; 
            }
            QLabel#BannerLabel {
                background-color: #313244; /* Color de fondo si no hay imagen */
                border-bottom: 2px solid #89b4fa;
            }
        """)

        # --- WIDGET CENTRAL Y LAYOUT PRINCIPAL ---
        central_widget = QWidget()
        central_widget.setObjectName("ContenedorPrincipal")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 10) # Márgenes externos
        main_layout.setSpacing(0)

        # --- SECCIÓN 1: BANNER DE IMAGEN ---
        self.banner_label = QLabel()
        self.banner_label.setObjectName("BannerLabel")
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner_label.setFixedSize(700, 150) # Altura fija para el banner

        # Intenta cargar la imagen
        # CAMBIA 'banner.jpg' POR LA RUTA DE TU IMAGEN REAL
        ruta_imagen = "C:\Aplicacion\img\img.jpg" 
        
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            # Escalar imagen para que llene el espacio suavemente
            scaled_pixmap = pixmap.scaled(self.banner_label.size(),Qt.AspectRatioMode.KeepAspectRatioByExpanding,Qt.TransformationMode.SmoothTransformation)
            self.banner_label.setPixmap(scaled_pixmap)
        else:
            self.banner_label.setText("[ IMAGEN DE BANNER NO ENCONTRADA ]\n(Coloca 'banner.jpg' junto al script)")
            self.banner_label.setStyleSheet("color: #7f849c; font-size: 14px; background-color: #a1a1a1;")

        main_layout.addWidget(self.banner_label)

        # --- Contenedor para el contenido (Título y Botones) con márgenes ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 10)
        content_layout.setSpacing(10)

        # --- SECCIÓN 2: TÍTULO ---
        titulo = QLabel("Herramienta didáctica")
        titulo.setObjectName("TituloLabel")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(titulo)

        # --- SECCIÓN 3: REJILLA DE BOTONES ---
        grid = QGridLayout()
        grid.setSpacing(15)

        # Configura aquí tus rutas. Si termina en .pdf, se abrirá en el visor interno.
        apps = [
            ("Analizador de Espectro", r"C:\Aplicacion\SpectrumAnalyzer.exe"),
            ("Polarización Lineal", r"C:\Aplicacion\PolarizacionLineal.exe"),
            ("Polarización Eliptica", r"C:\Aplicacion\PolarizacionEliptica.exe"),
            ("Polarización Circular", r"C:\Aplicacion\Grafico.exe"),
            ("Analizar de Onda 2D", r"C:\Aplicacion\GraficoOnda2D.exe"),
            ("Polarizacion Vertical 3D", r"C:\Aplicacion\PolarizacionVertical.exe"),
            ("Analizador de Polarización Variable", r"C:\Aplicacion\SimuladorPolarizacion.exe"),
            ("Material de  Apoyo", r"C:\Aplicacion\VisorPDF.exe") # <- Cambia a una ruta real .pdf
        ]

        for i, (nombre, ruta) in enumerate(apps):
            btn = QPushButton(nombre)
            # Usamos una función interm_lanzar para evitar problemas de scope con lambda
            btn.clicked.connect(self.crear_conector(ruta))
            # Grid: 2 columnas, filas automáticas (i//2, i%2)
            grid.addWidget(btn, i // 2, i % 2)

        content_layout.addLayout(grid)
        
        # Añadir el layout de contenido al layout principal
        main_layout.addLayout(content_layout)
        # Añadir un stretch al final para empujar todo hacia arriba si se redimensiona
        main_layout.addStretch()

    def crear_conector(self, ruta):
        """Pequeña función helper para capturar la ruta correcta en el lambda."""
        return lambda checked: self.gestionar_apertura(ruta)

    def gestionar_apertura(self, ruta):
        if not os.path.exists(ruta):
            QMessageBox.warning(self, "Error", f"No se encontró el archivo:\n{ruta}")
            return

        # Si el archivo es un PDF, abrir visor interno
        if ruta.lower().endswith(".pdf"):
            self.visor = VisorPDF(ruta)
            self.visor.show()
        else:
            # Si es un ejecutable, lanzar proceso
            try:
                # Usamos os.startfile en Windows para que sea más robusto abriendo exes y carpetas
                if sys.platform == 'win32':
                    os.startfile(ruta)
                else:
                    import subprocess
                    subprocess.Popen([ruta])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al ejecutar: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Establecer un estilo de fuente global más limpio
    fn = app.font()
    fn.setPointSize(10)
    app.setFont(fn)
    
    ex = LanzadorApps()
    ex.show()
    sys.exit(app.exec())