
import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFrame, QGroupBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QDoubleValidator, QIcon

# Integración de Matplotlib con PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

# --- Constantes Físicas ---
C = 299792458  # Velocidad de la luz (m/s)
ETA_0 = 120 * np.pi  # Impedancia intrínseca del vacío (aprox 377 ohms)

class MplCanvas(FigureCanvas):
    """Lienzo de Matplotlib para renderizado 3D animado."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Estilo oscuro para laboratorio visual
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#121212')
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        
        # Configuración inicial del eje 3D
        self.set_dark_theme()
        
        # Datos de la onda (iniciales)
        self.num_points = 200
        self.z = np.linspace(0, 10, self.num_points) # Eje de propagación
        self.time = 0
        self.ex_amp = 1.0 # Amplitud Horizontal inicial
        self.ey_amp = 0.5 # Amplitud Vertical inicial
        self.omega = 2 * np.pi * 1e6 # Frecuencia angular inicial (1 MHz)
        self.k = self.omega / C # Número de onda

    def set_dark_theme(self):
        """Configura los ejes con un tema oscuro."""
        self.ax.set_facecolor('#121212')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.zaxis.label.set_color('white')
        
        # Ocultar paneles de fondo para un look más limpio
        self.ax.xaxis.pane.set_visible(False)
        self.ax.yaxis.pane.set_visible(False)
        self.ax.zaxis.pane.set_visible(False)
        self.ax.grid(color='#444444', linestyle='--', alpha=0.5)

    def update_wave_data(self, ex, ey, freq_hz):
        """Actualiza los parámetros físicos de la onda."""
        self.ex_amp = ex
        self.ey_amp = ey
        self.omega = 2 * np.pi * freq_hz
        self.k = self.omega / C
        
        # Ajustar el eje Z dinámicamente según la longitud de onda (muestrar 3 lambdas)
        wavelength = C / freq_hz
        self.z = np.linspace(0, wavelength * 3, self.num_points)

    def render_frame(self):
        """Dibuja el frame actual de la animación."""
        self.ax.clear()
        self.set_dark_theme()
        
        # Cálculo de los componentes vectoriales del Campo Eléctrico (E)
        # E(z,t) = E0 * cos(kz - wt)
        phase = self.k * self.z - self.omega * self.time
        Ex = self.ex_amp * np.cos(phase)
        Ey = self.ey_amp * np.cos(phase)
        Ez = np.zeros_like(self.z) # Onda transversal
        
        # --- Dibujado ---
        
        # 1. Proyección Horizontal (Ex) - Cian
        self.ax.plot(self.z, Ex, zs=self.ax.get_zlim()[0], zdir='z', 
                     color='#00f2ff', alpha=0.2, linestyle='--', label='Proyección Horizontal (Ex)')
        
        # 2. Proyección Vertical (Ey) - Rosa
        self.ax.plot(self.z, Ey, zs=self.ax.get_ylim()[1], zdir='y', 
                     color='#ff0077', alpha=0.2, linestyle='--', label='Proyección Vertical (Ey)')

        # 3. Vector Campo E Resultante - Verde Neón
        self.ax.plot(self.z, Ex, Ey, color='#bcff00', lw=2.5, label='Campo Eléctrico E (Resultante)')

        # Configuración de límites y etiquetas
        max_amp = max(self.ex_amp, self.ey_amp, 0.1) * 1.2
        self.ax.set_xlim(self.z[0], self.z[-1])
        self.ax.set_ylim(-max_amp, max_amp)
        self.ax.set_zlim(-max_amp, max_amp)
        
        self.ax.set_xlabel('Distancia Z (m)')
        self.ax.set_ylabel('Amplitud Ex (V/m)')
        self.ax.set_zlabel('Amplitud Ey (V/m)')
        self.ax.set_title(f'Animación de Campo EM (t={self.time:.2e} s)', color='white')

        self.draw()

class AntennaSimApp(QMainWindow):
    """Ventana principal de la aplicación."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AntennaSim Pro - Polarización y Campo EM")
        self.setMinimumSize(1200, 800)
        
        # Estilo CSS Global (Dark Mode moderno)
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QGroupBox { 
                color: #bcff00; font-weight: bold; font-family: 'Segoe UI'; 
                border: 2px solid #333; border-radius: 8px; margin-top: 1ex; padding: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }
            QLabel { color: white; font-family: 'Segoe UI'; font-size: 13px; }
            QLineEdit { 
                background-color: #1e1e1e; color: white; border: 1px solid #444; 
                border-radius: 4px; padding: 6px; font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #bcff00; }
            QPushButton { 
                background-color: #bcff00; color: black; font-weight: bold; 
                font-family: 'Segoe UI'; font-size: 14px; border-radius: 6px; padding: 12px; margin-top: 15px;
            }
            QPushButton:hover { background-color: #d4ff55; }
            QPushButton:pressed { background-color: #9ecc00; }
            #ResultsFrame { background-color: #1a1a1a; border-radius: 8px; padding: 15px; border: 1px solid #333;}
            #ResultLabel { color: #00f2ff; font-weight: bold; font-size: 15px; }
            #ResultValue { color: white; font-family: 'Consolas'; font-size: 15px; }
        """)

        # Layout Principal (Horizontal: Controles | Gráfica)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Panel de Controles (Izquierda) ---
        control_panel = QFrame()
        control_panel.setFixedWidth(350)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 0, 10, 0)

        # 1. Grupo de Entrada de Datos
        input_group = QGroupBox("Parámetros del Sistema")
        form_layout = QFormLayout(input_group)
        form_layout.setSpacing(10)

        # Validador para asegurar entradas numéricas
        self.num_validator = QDoubleValidator(0.0, 1e18, 10)
        self.num_validator.setNotation(QDoubleValidator.Notation.ScientificNotation)

        self.in_gain = self.create_input(form_layout, "Ganancia Antena (dB):", "12.0")
        self.in_volt = self.create_input(form_layout, "Voltaje Alimentación (Vrms):", "120.0")
        self.in_freq = self.create_input(form_layout, "Frecuencia (Hz):", "2.4e9") # 2.4 GHz
        self.in_dist = self.create_input(form_layout, "Distancia Medición (m):", "100.0")
        self.in_z0   = self.create_input(form_layout, "Impedancia Entrada Antena (Ω):", "50.0")

        control_layout.addWidget(input_group)

        # 2. Botón Calcular
        self.btn_calc = QPushButton("CALCULAR Y ACTUALIZAR")
        self.btn_calc.clicked.connect(self.perform_calculations)
        control_layout.addWidget(self.btn_calc)

        # 3. Grupo de Resultados
        results_group = QGroupBox("Resultados de Polarización")
        results_layout = QVBoxLayout(results_group)
        
        self.results_frame = QFrame()
        self.results_frame.setObjectName("ResultsFrame")
        self.res_form = QFormLayout(self.results_frame)
        
        self.out_ex = self.create_result_display(self.res_form, "Campo E Horiz. (Ex0):")
        self.out_ey = self.create_result_display(self.res_form, "Campo E Vert. (Ey0):")
        self.out_etot = self.create_result_display(self.res_form, "Campo E Total RMS:")
        
        results_layout.addWidget(self.results_frame)
        control_layout.addWidget(results_group)
        control_layout.addStretch() # Empujar todo hacia arriba

        # --- Panel de Gráfica 3D (Derecha) ---
        self.canvas = MplCanvas(self, width=7, height=6, dpi=100)
        
        # Integrar layouts
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.canvas, stretch=1)

        # --- Timer para la Animación ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance_animation)
        self.animation_speed = 30 # ms por frame (aprox 33 FPS)
        self.is_animated = False

        # Cargar datos iniciales
        self.perform_calculations()

    # --- Funciones Auxiliares de GUI ---
    def create_input(self, layout, label_text, default_text):
        """Crea una fila de entrada de formulario."""
        le = QLineEdit(default_text)
        le.setValidator(self.num_validator)
        layout.addRow(label_text, le)
        return le

    def create_result_display(self, layout, label_text):
        """Crea una fila de visualización de resultados."""
        lbl_val = QLabel("---")
        lbl_val.setObjectName("ResultValue")
        lbl_lab = QLabel(label_text)
        lbl_lab.setObjectName("ResultLabel")
        layout.addRow(lbl_lab, lbl_val)
        return lbl_val

    # --- Lógica de Cálculo y Animación ---
    def perform_calculations(self):
        """Recoge datos, calcula campos y actualiza la gráfica."""
        try:
            # 1. Recolección de datos
            gain_db = float(self.in_gain.text())
            volt_rms = float(self.in_volt.text())
            freq_hz = float(self.in_freq.text())
            dist_m = float(self.in_dist.text())
            z_ant = float(self.in_z0.text())

            if dist_m <= 0 or freq_hz <= 0:
                raise ValueError("Frecuencia y Distancia deben ser positivas.")

            # 2. Cálculos Físicos
            
            # A. Potencia Transmitida (Pt = V^2 / Z)
            p_trans = (volt_rms**2) / z_ant
            
            # B. Ganancia lineal (G = 10^(GdB/10))
            gain_lin = 10**(gain_db / 10.0)
            
            # C. Potencia Radiada Isotrópica Equivalente (PIRE = Pt * Gt)
            eirp = p_trans * gain_lin
            
            # D. Densidad de Potencia a la distancia R (S = PIRE / (4*pi*R^2))
            power_density = eirp / (4 * np.pi * (dist_m**2))
            
            # E. Magnitud del Campo Eléctrico Total RMS (E = sqrt(S * ETA_0))
            e_tot_rms = np.sqrt(power_density * ETA_0)
            
            # --- Modelado de Polarización para Antena Direccional ---
            # Asumiremos un modelo estándar donde la antena direccional tiene
            # una polarización principal (ej. Vertical) muy fuerte y una cruzada (Horizontal) débil.
            # En ingeniería se usa la Discriminación de Polarización Cruzada (XPD) en dB.
            
            xpd_db = 20.0 # Valor típico de XPD para una buena antena direccional (20dB de diferencia)
            xpd_lin = 10**(xpd_db / 20.0) # Relación de amplitudes Ey/Ex
            
            # Ey0 es la componente principal, Ex0 la cruzada.
            # E_tot_rms^2 = Ey_rms^2 + Ex_rms^2
            # E_tot_rms^2 = (Ex_rms * XPD)^2 + Ex_rms^2 = Ex_rms^2 * (XPD^2 + 1)
            
            ex_rms = e_tot_rms / np.sqrt(xpd_lin**2 + 1)
            ey_rms = ex_rms * xpd_lin
            
            # Convertir RMS a Amplitud de pico para la animación (Ao = Arms * sqrt(2))
            ex_peak = ex_rms * np.sqrt(2)
            ey_peak = ey_rms * np.sqrt(2)

            # 3. Actualizar Visualización de Resultados
            self.out_ex.setText(f"{ex_peak:.3e} V/m (Pico)")
            self.out_ey.setText(f"{ey_peak:.3e} V/m (Pico)")
            self.out_etot.setText(f"{e_tot_rms:.3e} V/m (RMS)")

            # 4. Actualizar la Gráfica y reiniciar animación
            self.canvas.update_wave_data(ex_peak, ey_peak, freq_hz)
            self.canvas.time = 0
            
            if not self.is_animated:
                self.timer.start(self.animation_speed)
                self.is_animated = True
            
            # Forzar renderizado del primer frame
            self.canvas.render_frame()

        except ValueError as e:
            QMessageBox.warning(self, "Error de Entrada", f"Entrada inválida: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error inesperado: {str(e)}")

    def advance_animation(self):
        """Avanza el tiempo y renderiza el siguiente frame."""
        # Avanzar el tiempo basándose en la frecuencia para que sea visible
        # Un buen paso es 1/20 del período
        period = 1.0 / (self.canvas.omega / (2 * np.pi))
        time_step = period / 20.0
        
        self.canvas.time += time_step
        self.canvas.render_frame()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar paleta para asegurar Dark Mode en el sistema si es necesario
    app.setStyle("Fusion")
    
    window = AntennaSimApp()
    window.show()
    sys.exit(app.exec())