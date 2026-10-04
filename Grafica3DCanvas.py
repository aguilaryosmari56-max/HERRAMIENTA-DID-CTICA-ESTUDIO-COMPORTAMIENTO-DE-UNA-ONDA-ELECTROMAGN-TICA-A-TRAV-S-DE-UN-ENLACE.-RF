import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt

class Grafica3DCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Crear la figura y el layout 3D
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        
        # Configuración estética inicial
        self.ax.set_xlabel('Horizontal (X)')
        self.ax.set_ylabel('Eje Y (Propagación)')
        self.ax.set_zlabel('Vertical (Z)')
        self.fig.tight_layout()

    def actualizar_grafica(self, ant1_data, ant2_data):
        self.ax.clear()
        
        # Configurar límites y etiquetas nuevamente tras limpiar
        self.ax.set_xlabel('Horizontal (X)')
        self.ax.set_ylabel('Eje Y (Propagación)')
        self.ax.set_zlabel('Vertical (Z)')
        
        # Encontrar límites globales para que la gráfica no "salte"
        all_coords = np.concatenate(([ant1_data['pos']], [ant2_data['pos']]))
        max_val = np.max(np.abs(all_coords)) + 1.5
        self.ax.set_xlim(-max_val, max_val)
        self.ax.set_ylim(-max_val, max_val)
        self.ax.set_zlim(-max_val, max_val)
        
        # Líneas de referencia (ejes cartesianos)
        self.ax.plot([-max_val, max_val], [0, 0], [0, 0], color='black', linewidth=0.5, alpha=0.5)
        self.ax.plot([0, 0], [-max_val, max_val], [0, 0], color='black', linewidth=0.5, alpha=0.5)
        self.ax.plot([0, 0], [0, 0], [-max_val, max_val], color='black', linewidth=0.5, alpha=0.5)

        # Funcioón auxiliar para graficar una antena
        def graficar_vector_antena(data, color_base, nombre):
            pos = data['pos']
            vec_total = data['vec_total']
            vec_h = data['vec_h']
            vec_v = data['vec_v']
            
            # 1. Dibujar punto de posición de la antena
            self.ax.scatter3D(pos[0], pos[1], pos[2], color=color_base, s=50, label=f'Posición {nombre}')
            
            # 2. Dibujar Vector Total (La polarización real) con Quiver (flecha)
            # Quiver requiere (x,y,z, u,v,w) -> origen y dirección
            self.ax.quiver(pos[0], pos[1], pos[2], 
                           vec_total[0], vec_total[1], vec_total[2], 
                           color=color_base, linewidth=2, label=f'E Total {nombre}')
            
            # 3. Dibujar Componentes (Proyecciones) en líneas discontinuas
            # Componente Horizontal (X)
            self.ax.plot([pos[0], pos[0] + vec_h[0]], 
                         [pos[1], pos[1]], 
                         [pos[2], pos[2]], 
                         color='blue', linestyle='--', alpha=0.6, linewidth=1)
            
            # Componente Vertical (Z)
            self.ax.plot([pos[0], pos[0]], 
                         [pos[1], pos[1]], 
                         [pos[2], pos[2] + vec_v[2]], 
                         color='green', linestyle='--', alpha=0.6, linewidth=1)

        # Graficar ambas
        graficar_vector_antena(ant1_data, 'red', 'Antena 1 (Tx)')
        graficar_vector_antena(ant2_data, 'purple', 'Antena 2 (Rx)')
        
        self.ax.legend(loc='upper left', fontsize='small')
        self.draw()

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Polarización de 2 Antenas 3D")
        self.resize(1200, 700)
        self.initUI()
        
        # Realizar cálculo inicial
        self.calcular_y_graficar()

    def initUI(self):
        # Layout Principal: Horizontal (Controles | Gráfica)
        layout_principal = QHBoxLayout()
        self.setLayout(layout_principal)
        
        # --- PANEL IZQUIERDO: CONTROLES ---
        panel_controles = QVBoxLayout()
        layout_principal.addLayout(panel_controles, 1) # Proporción 1
        
        # Grupo Antena 1
        grupo1 = QGroupBox("Configuración Antena 1 (Tx)")
        grid1 = QGridLayout()
        grupo1.setLayout(grid1)
        
        self.ant1_x = QLineEdit("0"); grid1.addWidget(QLabel("Pos X:"), 0, 0); grid1.addWidget(self.ant1_x, 0, 1)
        self.ant1_y = QLineEdit("-2"); grid1.addWidget(QLabel("Pos Y:"), 1, 0); grid1.addWidget(self.ant1_y, 1, 1)
        self.ant1_z = QLineEdit("0"); grid1.addWidget(QLabel("Pos Z:"), 2, 0); grid1.addWidget(self.ant1_z, 2, 1)
        self.ant1_angulo = QLineEdit("90"); grid1.addWidget(QLabel("Ángulo θ (grados°):"), 3, 0); grid1.addWidget(self.ant1_angulo, 3, 1)
        # Notas: 90° es Vertical (Z puro), 0° es Horizontal (X puro)
        
        panel_controles.addWidget(grupo1)
        
        # Grupo Antena 2
        grupo2 = QGroupBox("Configuración Antena 2 (Rx)")
        grid2 = QGridLayout()
        grupo2.setLayout(grid2)
        
        self.ant2_x = QLineEdit("0"); grid2.addWidget(QLabel("Pos X:"), 0, 0); grid2.addWidget(self.ant2_x, 0, 1)
        self.ant2_y = QLineEdit("2"); grid2.addWidget(QLabel("Pos Y:"), 1, 0); grid2.addWidget(self.ant2_y, 1, 1)
        self.ant2_z = QLineEdit("0"); grid2.addWidget(QLabel("Pos Z:"), 2, 0); grid2.addWidget(self.ant2_z, 2, 1)
        self.ant2_angulo = QLineEdit("45"); grid2.addWidget(QLabel("Ángulo θ (grados°):"), 3, 0); grid2.addWidget(self.ant2_angulo, 3, 1)
        
        panel_controles.addWidget(grupo2)
        
        # Botón Calcular
        self.btn_calcular = QPushButton("Actualizar Simulación 3D")
        self.btn_calcular.setMinimumHeight(40)
        self.btn_calcular.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        self.btn_calcular.clicked.connect(self.calcular_y_graficar)
        panel_controles.addWidget(self.btn_calcular)
        
        # Panel de Resultados Numéricos
        grupo_res = QGroupBox("Componentes Calculados (Magnitud=1)")
        layout_res = QVBoxLayout()
        grupo_res.setLayout(layout_res)
        self.lbl_res1 = QLabel("Antena 1: Eh= - , Ev= -")
        self.lbl_res2 = QLabel("Antena 2: Eh= - , Ev= -")
        layout_res.addWidget(self.lbl_res1)
        layout_res.addWidget(self.lbl_res2)
        panel_controles.addWidget(grupo_res)

        panel_controles.addStretch() # Empujar todo hacia arriba

        # --- PANEL DERECHO: GRÁFICA 3D ---
        self.canvas_3d = Grafica3DCanvas(self, width=8, height=6)
        layout_principal.addWidget(self.canvas_3d, 3) # Proporción 3

    def obtener_datos_antena(self, le_x, le_y, le_z, le_angulo):
        try:
            # 1. Leer Inputs
            x = float(le_x.text())
            y = float(le_y.text())
            z = float(le_z.text())
            theta_deg = float(le_angulo.text())
            
            # 2. Lógica Matemática de Polarización
            # Asumimos propagación en el eje Y.
            # El campo eléctrico E vibra en el plano X-Z.
            # θ=0° -> Campo en X (Horizontal puro)
            # θ=90° -> Campo en Z (Vertical puro)
            
            theta_rad = np.radians(theta_deg)
            
            # Asumimos Magnitud del campo E = 1 para simplificar
            magnitud_e = 1.0
            
            # Componentes vectoriales
            eh_mag = magnitud_e * np.cos(theta_rad) # Proyección en X
            ev_mag = magnitud_e * np.sin(theta_rad) # Proyección en Z
            
            return {
                'pos': np.array([x, y, z]),
                'vec_total': np.array([eh_mag, 0, ev_mag]), # Vector E en el espacio
                'vec_h': np.array([eh_mag, 0, 0]),          # Solo componente X
                'vec_v': np.array([0, 0, ev_mag]),          # Solo componente Z
                'eh_mag': eh_mag,
                'ev_mag': ev_mag,
                'valido': True
            }
        except ValueError:
            return {'valido': False}

    def calcular_y_graficar(self):
        # Obtener datos de ambas antenas
        data1 = self.obtener_datos_antena(self.ant1_x, self.ant1_y, self.ant1_z, self.ant1_angulo)
        data2 = self.obtener_datos_antena(self.ant2_x, self.ant2_y, self.ant2_z, self.ant2_angulo)
        
        if not data1['valido'] or not data2['valido']:
            self.lbl_res1.setText("Error en los datos de entrada.")
            return

        # Actualizar Etiquetas Numéricas
        self.lbl_res1.setText(f"Antena 1 (Roja): Eh (X)={data1['eh_mag']:.2f}, Ev (Z)={data1['ev_mag']:.2f}")
        self.lbl_res2.setText(f"Antena 2 (Morada): Eh (X)={data2['eh_mag']:.2f}, Ev (Z)={data2['ev_mag']:.2f}")
        
        # Actualizar el Canvas 3D
        self.canvas_3d.actualizar_grafica(data1, data2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Estilo general para que no se vea tan nativo antiguo
    app.setStyle("Fusion")
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())