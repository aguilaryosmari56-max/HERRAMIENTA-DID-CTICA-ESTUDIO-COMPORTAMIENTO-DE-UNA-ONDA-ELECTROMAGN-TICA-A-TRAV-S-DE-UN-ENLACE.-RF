import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                             QToolBar, QVBoxLayout, QWidget)
from PyQt6.QtGui import QAction
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView

class LectorPDFPredeterminado(QMainWindow):
    def __init__(self, ruta_pdf):
        super().__init__()

        self.setWindowTitle("Visor PDF Automático")
        self.resize(1000, 900)

        # 1. Configuración del motor y la vista
        self.documento = QPdfDocument(self)
        self.vista_pdf = QPdfView(self)
        self.vista_pdf.setDocument(self.documento)
        
        # Configuración de scroll continuo y ajuste de ancho
        self.vista_pdf.setPageMode(QPdfView.PageMode.MultiPage)
        self.vista_pdf.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        self.setCentralWidget(self.vista_pdf)
        self.crear_interfaz()

        # 2. CARGA AUTOMÁTICA AL INICIAR
        self.cargar_pdf_inicial(ruta_pdf)

    def cargar_pdf_inicial(self, ruta):
        if os.path.exists(ruta):
            self.documento.load(ruta)
        else:
            print(f"Error: El archivo no se encontró en {ruta}")

    def crear_interfaz(self):
        toolbar = QToolBar("Controles")
        self.addToolBar(toolbar)

        # Botón para abrir otros archivos si se desea
       # accion_abrir = QAction("📂 Abrir otro...", self)
        #accion_abrir.triggered.connect(self.seleccionar_pdf)
        #toolbar.addAction(accion_abrir)

        toolbar.addSeparator()

        # Zoom
        zoom_in = QAction("➕ Aumentar", self)
        zoom_in.triggered.connect(lambda: self.cambiar_zoom(1.1))
        toolbar.addAction(zoom_in)

        zoom_out = QAction("➖ Reducir", self)
        zoom_out.triggered.connect(lambda: self.cambiar_zoom(0.9))
        toolbar.addAction(zoom_out)

    def seleccionar_pdf(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "PDF (*.pdf)")
        if ruta:
            self.documento.load(ruta)

    def cambiar_zoom(self, factor):
        self.vista_pdf.setZoomMode(QPdfView.ZoomMode.Custom)
        nuevo_valor = self.vista_pdf.zoomFactor() * factor
        self.vista_pdf.setZoomFactor(nuevo_valor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Define aquí la ruta de tu PDF por defecto
    # Puede ser una ruta absoluta o relativa
    archivo_por_defecto = "ENLACES INVISIBLES.pdf" 
    
    ventana = LectorPDFPredeterminado(archivo_por_defecto)
    ventana.show()
    sys.exit(app.exec())