import sys
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from mpl_toolkits.mplot3d import Axes3D # Necesario para proyecciones 3D antiguas
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

class PlotCanvas3D(FigureCanvas):
    def __init__(self, parent=None, width=7, height=6, dpi=100):
        # Crear la figura y el layout 3D
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Configuraciones estéticas iniciales
        self.setup_plot_axes()
        self.fig.tight_layout()

    def setup_plot_axes(self):
        """Configura los límites, etiquetas y vista inicial del cubo 3D."""
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-4, 4) # Eje de propagación
        self.ax.set_zlim(-1.5, 1.5)
        
        self.ax.set_xlabel('Horizontal (X)', fontsize=9)
        self.ax.set_ylabel('Eje Propagación (Y)', fontsize=9)
        self.ax.set_zlabel('Vertical (Z)', fontsize=9)
        
        # Vista inicial inclinada para apreciar la tridimensionalidad
        self.ax.view_init(elev=20, azim=-45)
        self.ax.grid(True, linestyle='--', alpha=0.5)

    def graficar_polarizacion(self, ant1_deg, ant2_deg):
        """Calcula los componentes y dibuja la onda y los vectores 3D."""
        self.ax.clear() # Limpiar gráfico anterior
        self.setup_plot_axes()
        
        # Magnitud normalizada del campo E = 1
        magnitud = 1.0
        
        # --- CÁLCULOS TRIGONOMÉTRICOS (Normalizados a Magnitud 1) ---
        # Antena 1 (Tx) - Origen de la onda en Y = -3
        rad1 = np.radians(ant1_deg)
        eh1 = magnitud * np.cos(rad1) # Componente X
        ev1 = magnitud * np.sin(rad1) # Componente Z
        
        # Antena 2 (Rx) - Punto de recepción en Y = 3
        rad2 = np.radians(ant2_deg)
        eh2 = magnitud * np.cos(rad2) # Componente X
        ev2 = magnitud * np.sin(rad2) # Componente Z

        # --- DIBUJAR VECTORES DE COMPONENTES EN EL ORIGEN (Y=-3 y Y=3) ---
        # Auxiliar para dibujar flechas Quiver
        def draw_quiver(x, y, z, u, v, w, color, label):
            self.ax.quiver(x, y, z, u, v, w, color=color, length=1, normalize=True, arrow_length_ratio=0.3, label=label)

        # Antena 1 (Tx) - Roja
        # Vector Eh (Horizontal/X)
        draw_quiver(0, -3, 0, eh1, 0, 0, '#c0392b', 'Tx: Eh (X)')
        # Vector Ev (Vertical/Z)
        draw_quiver(0, -3, 0, 0, 0, ev1, '#e74c3c', 'Tx: Ev (Z)')
        # Vector Total
        draw_quiver(0, -3, 0, eh1, 0, ev1, 'black', 'Tx: E Total')

        # Antena 2 (Rx) - Azul
        # Vector Eh (Horizontal/X)
        draw_quiver(0, 3, 0, eh2, 0, 0, '#2980b9', 'Rx: Eh (X)')
        # Vector Ev (Vertical/Z)
        draw_quiver(0, 3, 0, 0, 0, ev2, '#3498db', 'Rx: Ev (Z)')
        # Vector Total
        draw_quiver(0, 3, 0, eh2, 0, ev2, '#2c3e50', 'Rx: E Total')

        # --- DIBUJAR LA ONDA ELECTROMAGNÉTICA VIAJERA (Y=-3 a Y=3) ---
        # Crear puntos a lo largo del eje Y (propagación)
        y_puntos = np.linspace(-3, 3, 200)
        
        # La onda oscila en X y Z basándose en la polarización de la Tx
        # Simulamos una fase espacial para que parezca una onda viajera
        puntos_onda_x = eh1 * np.cos(y_puntos * 2) # Oscilación Horizontal
        puntos_onda_z = ev1 * np.cos(y_puntos * 2) # Oscilación Vertical

        # Graficar la línea de la onda en 3D (Hélice o línea inclinada)
        self.ax.plot(puntos_onda_x, y_puntos, puntos_onda_z, color='#8e44ad', lw=2, label='Onda E (viajera)')

        # Añadir leyenda pequeña
        self.ax.legend(loc='upper left', fontsize='xs', frameon=False)
        
        self.draw() # Actualizar el canvas

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Polarización de 2 Antenas 3D")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Estilo general (Fusion)
        QApplication.setStyle("Fusion")
        
        self.initUI()
        
        # Ejecutar cálculo inicial por defecto (45° y 45°)
        self.calcular_y_graficar()

    def initUI(self):
        # Layout Principal: Horizontal (Controles | Gráfico)
        layout_principal = QHBoxLayout()
        self.setLayout(layout_principal)

        # --- PANEL IZQUIERDO: CONTROLES ---
        panel_controles = QVBoxLayout()
        panel_controles.setSpacing(15)
        layout_principal.addLayout(panel_controles, 1) # Proporción de tamaño 1

        # Título del panel
        lbl_titulo = QLabel("Configuración de Antenas")
        lbl_titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_controles.addWidget(lbl_titulo)

        # Grupo Antena 1 (Tx)
        grupo_ant1 = QGroupBox("Antena 1: Transmisora (Tx)")
        layout_grid1 = QGridLayout()
        grupo_ant1.setLayout(layout_grid1)
        
        lbl_ang1 = QLabel("Ángulo de Inclinación (θ₁):")
        self.in_ang1 = QLineEdit("45")
        self.in_ang1.setPlaceholderText("Ej: 0, 45, 90")
        layout_grid1.addWidget(lbl_ang1, 0, 0)
        layout_grid1.addWidget(self.in_ang1, 0, 1)
        layout_grid1.addWidget(QLabel("grados (°)"), 0, 2)
        
        panel_controles.addWidget(grupo_ant1)

        # Grupo Antena 2 (Rx)
        grupo_ant2 = QGroupBox("Antena 2: Receptora (Rx)")
        layout_grid2 = QGridLayout()
        grupo_ant2.setLayout(layout_grid2)
        
        lbl_ang2 = QLabel("Ángulo de Inclinación (θ₂):")
        self.in_ang2 = QLineEdit("45")
        self.in_ang2.setPlaceholderText("Ej: 0, 45, 90")
        layout_grid2.addWidget(lbl_ang2, 0, 0)
        layout_grid2.addWidget(self.in_ang2, 0, 1)
        layout_grid2.addWidget(QLabel("grados (°)"), 0, 2)
        
        panel_controles.addWidget(grupo_ant2)

        # Botón Calcular
        self.btn_calcular = QPushButton("Actualizar Gráfico 3D")
        self.btn_calcular.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_calcular.setMinimumHeight(40)
        # Estilo CSS para el botón
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1a252f;
            }
        """)
        self.btn_calcular.clicked.connect(self.calcular_y_graficar)
        panel_controles.addWidget(self.btn_calcular)

        # Panel de Resultados Numéricos
        grupo_resultados = QGroupBox("Resultados de Componentes (Magnitud 1)")
        layout_res = QVBoxLayout()
        grupo_resultados.setLayout(layout_res)
        
        self.lbl_res1 = QLabel("Antena 1 (Tx): Eh = - , Ev = -")
        self.lbl_res1.setWordWrap(True)
        self.lbl_res2 = QLabel("Antena 2 (Rx): Eh = - , Ev = -")
        self.lbl_res2.setWordWrap(True)
        
        # Label para desajuste (Mismatch)
        self.lbl_mismatch = QLabel("Pérdida por Desajuste: - dB")
        self.lbl_mismatch.setStyleSheet("color: #c0392b; font-weight: bold;")
        
        layout_res.addWidget(self.lbl_res1)
        layout_res.addWidget(self.lbl_res2)
        layout_res.addWidget(self.lbl_mismatch)
        
        panel_controles.addWidget(grupo_resultados)

        # Información de ayuda
        lbl_info = QLabel("Ayuda:\n"
                          "0° = Polarización Horizontal pura (X)\n"
                          "90° = Polarización Vertical pura (Z)\n"
                          "Cualquier otro = Combinación lineal.")
        lbl_info.setStyleSheet("color: gray; font-style: italic;")
        lbl_info.setWordWrap(True)
        panel_controles.addWidget(lbl_info)

        panel_controles.addStretch() # Empujar todo hacia arriba

        # --- PANEL DERECHO: GRÁFICO 3D ---
        self.canvas3d = PlotCanvas3D(self)
        
        # Frame contenedor para darle borde al gráfico
        frame_grafico = QFrame()
        frame_grafico.setFrameShape(QFrame.Shape.StyledPanel)
        layout_grafico = QVBoxLayout()
        layout_grafico.addWidget(self.canvas3d)
        frame_grafico.setLayout(layout_grafico)
        
        layout_principal.addWidget(frame_grafico, 3) # Proporción de tamaño 3

    def calcular_y_graficar(self):
        """Lee inputs, calcula componentes numéricos y llama al graficador."""
        try:
            # 1. Leer valores de los inputs
            ang1_deg = float(self.in_ang1.text())
            ang2_deg = float(self.in_ang2.text())
            
            # 2. Actualizar el gráfico 3D
            self.canvas3d.graficar_polarizacion(ang1_deg, ang2_deg)
            
            # 3. Calcular componentes numéricos para mostrar (Magnitud E=1)
            # Normalizado
            rad1 = np.radians(ang1_deg)
            eh1 = np.cos(rad1)
            ev1 = np.sin(rad1)
            
            rad2 = np.radians(ang2_deg)
            eh2 = np.cos(rad2)
            ev2 = np.sin(rad2)
            
            # Actualizar textos de resultados
            self.lbl_res1.setText(f"Antena 1 (Tx): <b>Eh(X)={eh1:.2f}</b>, <b>Ev(Z)={ev1:.2f}</b>")
            self.lbl_res2.setText(f"Antena 2 (Rx): <b>Eh(X)={eh2:.2f}</b>, <b>Ev(Z)={ev2:.2f}</b>")
            
            # 4. Calcular Pérdida por Desajuste de Polarización (Polarization Mismatch Loss)
            # PLF = cos²(θ₁ - θ₂)
            plf = np.cos(np.radians(ang1_deg - ang2_deg))**2
            
            # Convertir a dB (manejar caso PLF=0 para evitar error log)
            if plf > 1e-6:
                loss_db = 10 * np.log10(plf)
                self.lbl_mismatch.setText(f"Pérdida por Desajuste: {loss_db:.2f} dB")
            else:
                self.lbl_mismatch.setText("Pérdida por Desajuste: Infinita (Cross-Pol)")
            
        except ValueError:
            # Manejo de error si el usuario ingresa texto no numérico
            self.lbl_res1.setText("Error: Ingrese ángulos válidos (números).")
            self.lbl_res2.setText("")
            self.lbl_mismatch.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentanaPrincipal()
    window.show()
    sys.exit(app.exec())