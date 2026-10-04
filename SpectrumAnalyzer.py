import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSlider,  
                            QGraphicsView, QGraphicsScene, QGraphicsDropShadowEffect, QFrame, QGraphicsEllipseItem)
from PyQt5.QtCore import (Qt, QTimer, QPointF, QLineF, QRectF, 
                         QThreadPool, QRunnable, QObject, pyqtSignal)
from PyQt5.QtGui import (QPainter, QPen, QColor, QLinearGradient, QPainterPath, QPolygonF)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import patches


# SEÑALES BRO
class WorkerSignals(QObject):
    result = pyqtSignal(dict)
    
# CLASE PARA PROCESAMIENTO EN SEGUNDO PLANO (THREADS)
class SpectrumWorker(QRunnable):
    def __init__(self, params):
        super().__init__()
        self.params = params
        self.signals = WorkerSignals()

    def run(self):
        try:
            # Cálculos con NumPy
            freq_points = np.linspace(0, 5000, 400)
            bw = self.params['bandwidth'] / 10
            
            # Señal principal
            main_signal = self.params['amplitude'] * np.exp(
                -np.square(freq_points - self.params['frequency']) / (3 * bw**2))
            
            # Armónicos (cálculo vectorizado)
            harmonics = np.array([0.5, 1.5, 2.0]) * self.params['frequency']
            secondary = (self.params['amplitude'] - 20) * np.sum(
                [np.exp(-np.square(freq_points - f) / (2 * (bw*2)**2)) for f in harmonics],
                axis=0
            )
            
            # Ruido y espectro final
            noise = np.random.normal(0, 0.6, len(freq_points))
            spectrum = main_signal + secondary + noise
            
            # Emitir resultados
            self.signals.result.emit({
                'freq_points': freq_points,
                'spectrum': spectrum,
                'peak_value': np.max(spectrum),
                'snr': np.max(spectrum) - np.mean(noise),
                'noise': np.mean(noise)
            })
        except Exception as e:
            print("Error en hilo secundario:", e)


# INTERFAZ PRINCIPAL CON GESTIÓN DE THREADS TREMENDO
class SpectrumAnalyzerSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.waterfall_data = np.zeros((50, 400))
        self.spectrum_canvas = None
        self.waterfall_canvas = None
        self.metrics_canvas = None
        
        self.setup_ui()
        self.setup_threading()
        
    def setup_ui(self):
        # Configuración de ventana
        self.setWindowTitle("SPECTRUM ANALYZER")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 800)
        
        # Paleta de colores oscuros
        self.dark_gray = QColor(45, 45, 45)
        self.medium_gray = QColor(60, 60, 60)
        self.light_gray = QColor(100, 100, 100)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Componentes de la UI
        self.setup_title_bar()
        self.setup_antennas()
        self.setup_plots()
        self.setup_controls()
        
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.antenna_view)
        main_layout.addWidget(self.plot_container)
        main_layout.addWidget(self.control_panel)
    
    def setup_threading(self):
        # Configuración del sistema de hilos
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(2)  
        
        # Estado inicial
        self.simulation_active = True
        self.frequency = 1000
        self.amplitude = -50
        self.bandwidth = 100
        self.waterfall_data = np.zeros((50, 400))
        self.waterfall_counter = 0
        
        # Timer principal (30 FPS)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.schedule_calculation)
        self.update_timer.start(33)  # 30 actualizaciones/segundo


    def setup_title_bar(self):
        # Barra de título personalizada
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(35)
        self.title_bar.setStyleSheet(f"""
            background-color: {self.medium_gray.name()};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            padding-left: 15px;
        """)
        
        layout = QHBoxLayout(self.title_bar)
        layout.setContentsMargins(0, 0, 10, 0)
        
        self.title_label = QLabel("SPECTRUM ANALYZER")
        self.title_label.setStyleSheet("color: white; font: bold 14px;")
        
        # Botones de control de ventana
        btn_style = f"""
            QPushButton {{
                color: white;
                background-color: transparent;
                border: 1px solid {self.light_gray.name()};
                border-radius: 4px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }}
            QPushButton:hover {{ background-color: {self.medium_gray.name()}; }}
        """
        self.min_btn = QPushButton("─")
        self.max_btn = QPushButton("□")
        self.close_btn = QPushButton("✕")
        
        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setStyleSheet(btn_style)
        
        self.close_btn.setStyleSheet(btn_style + "QPushButton:hover { background-color: #ff4444; }")
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)
        
        # Conexiones de botones
        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.close)
    
    def setup_antennas(self):
        self.antenna_view = AntennaGraphicsView()
        self.antenna_view.setFixedHeight(250)
    
    def setup_plots(self):
        self.plot_container = QWidget()
        layout = QHBoxLayout(self.plot_container)
        
        self.spectrum_plot = self.create_spectrum_plot()
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.waterfall_plot = self.create_waterfall_plot()
        self.metrics_plot = self.create_metrics_plot()
        
        right_layout.addWidget(self.waterfall_plot)
        right_layout.addWidget(self.metrics_plot)
        
        layout.addWidget(self.spectrum_plot, 70)
        layout.addWidget(right_panel, 30)
    
    def create_spectrum_plot(self):
        fig = Figure(facecolor=self.dark_gray.name())
        canvas = FigureCanvas(fig)
        self.spectrum_canvas = canvas
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #2E2E2E;
                border-radius: 12px;
            }
        """)
        
        # Añadir sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(3, 3)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(canvas)
        
        ax = fig.add_subplot(111)
        ax.set_title("Espectro de Frecuencia", 
                    color='white', 
                    pad=18,
                    fontsize=12,
                    fontweight='bold',
                    y=1.02)
        ax.set_xlabel("Frecuencia (MHz)", 
                     color='white', 
                     fontsize=10,
                     labelpad=8)
        ax.set_ylabel("Amplitud (dBm)", 
                     color='white', 
                     fontsize=10,
                     labelpad=10)
        ax.tick_params(colors='white')
        ax.set_facecolor(self.medium_gray.name())
        ax.grid(True, color='#666666')
        fig.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.15)
        
        self.spectrum_line, = ax.plot([], [], '#00FFAA', linewidth=1.2)
        self.peak_marker = ax.plot([], [], 'yo', markersize=6, alpha=0.8)[0]
        
        return container
    
    def create_waterfall_plot(self):
        fig = Figure(facecolor=self.dark_gray.name())
        canvas = FigureCanvas(fig)
        self.waterfall_canvas = canvas
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #2E2E2E;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(6, 6)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)  # Margen superior
        layout.addWidget(canvas)
        
        ax = fig.add_subplot(111)
        
        # Título y etiquetas
        ax.set_title("WATERFALL", 
                    color='white', 
                    pad=10,  
                    fontsize=11,
                    fontweight='bold',
                    y=0.94)  

        ax.set_xlabel("Frecuencia (MHz)", 
                     color='white', 
                     fontsize=9,
                     labelpad=3)
        
        ax.set_ylabel("Tiempo (s)", 
                     color='white', 
                     fontsize=9,
                     labelpad=4)
        
        # Ajustar márgenes
        fig.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.20)
        
        ax.tick_params(axis='both', 
                      colors='white', 
                      labelsize=8,
                      length=4,
                      width=1)
        
        self.waterfall_img = ax.imshow(
            self.waterfall_data,
            aspect='auto',
            cmap='inferno',  
            interpolation='hanning'
        )
        
        return container
    
    def create_metrics_plot(self):
        fig = Figure(facecolor=self.dark_gray.name())
        canvas = FigureCanvas(fig)
        self.metrics_canvas = canvas
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: #2E2E2E;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(3, 3)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(canvas)
        
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Fondo para las métricas
        rect = patches.Rectangle((0.02, 0.1), 0.96, 0.8,
                                linewidth=1, 
                                edgecolor='#00FFAA',
                                facecolor='#404040',
                                alpha=0.5,
                                transform=ax.transAxes)
        ax.add_patch(rect)
        
        # Texto
        self.metrics_text = ax.text(
            0.5, 0.5,
            "",
            fontsize=10,
            color='#00FFAA',
            fontfamily='monospace',
            ha='center',
            va='center',
            transform=ax.transAxes,
            bbox=dict(facecolor='#303030', 
                     edgecolor='#00FFAA', 
                     boxstyle='round,pad=0.5',
                     alpha=0.7)
        )
        
        # Título de métricas
        ax.text(0.5, 0.93, "MÉTRICAS\n",
               color='white',
               fontsize=11,
               ha='center',
               va='center',
               transform=ax.transAxes,
               fontweight='bold')
        
        return container
    
    def setup_controls(self):
        # Panel de controles
        self.control_panel = QWidget()
        self.control_panel.setStyleSheet("""
            background-color: #2E2E2E;
            border-radius: 8px;
            padding: 12px;
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(3, 3)
        self.control_panel.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self.control_panel)
        layout.setSpacing(20)
        
        # Sliders
        controls = [
            ("Frecuencia", "MHz", 100, 5000, self.set_frequency),
            ("Amplitud", "dBm", -100, 0, self.set_amplitude),
            ("Ancho Banda", "kHz", 1, 3000, self.set_bandwidth)
        ]
        
        for label, unit, min_val, max_val, callback in controls:
            container = QWidget()
            v_layout = QVBoxLayout(container)
            
            lbl = QLabel(f"{label} ({unit})")
            lbl.setStyleSheet("color: white; font: bold 12px;")
            
            value_lbl = QLabel(str((min_val + max_val) // 2))
            value_lbl.setStyleSheet("color: white; font: 14px;")
            value_lbl.setAlignment(Qt.AlignCenter)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue((min_val + max_val) // 2)
            slider.valueChanged.connect(callback)
            slider.valueChanged.connect(lambda v, lbl=value_lbl: lbl.setText(str(v)))
            
            slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    height: 8px;
                    background: {self.light_gray.name()};
                    border-radius: 4px;
                }}
                QSlider::handle:horizontal {{
                    width: 16px;
                    height: 16px;
                    background: #00FFAA;
                    border-radius: 8px;
                    margin: -4px 0;
                }}
                QSlider::sub-page:horizontal {{
                    background: #00AA77;
                    border-radius: 4px;
                }}
            """)
            
            v_layout.addWidget(lbl)
            v_layout.addWidget(value_lbl)
            v_layout.addWidget(slider)
            layout.addWidget(container)
        
        # Botones de control
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(8)
        
        btn_style = f"""
            QPushButton {{
                background-color: {self.light_gray.name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font: bold 12px;
            }}
            QPushButton:hover {{ background-color: #00AA77; }}
        """
        
        self.start_btn = QPushButton("Iniciar")
        self.stop_btn = QPushButton("Detener")
        self.reset_btn = QPushButton("Reiniciar")
        
        for btn in [self.start_btn, self.stop_btn, self.reset_btn]:
            btn.setStyleSheet(btn_style)
            btn.setFixedHeight(40)
            btn_layout.addWidget(btn)
        
        layout.addWidget(btn_container)
        
        # Conexiones de botones
        self.start_btn.clicked.connect(self.start_simulation)
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.reset_btn.clicked.connect(self.reset_simulation)
    
    def schedule_calculation(self):
        """Programar cálculo en hilo secundario"""
        if self.simulation_active:
            worker = SpectrumWorker({
                'frequency': self.frequency,
                'amplitude': self.amplitude,
                'bandwidth': self.bandwidth
            })
            worker.signals.result.connect(self.update_ui)
            self.threadpool.start(worker)
    
    def update_ui(self, data):
        """Actualizar UI con datos del hilo secundario"""
        # 1. Actualizar espectro
        self.spectrum_line.set_data(data['freq_points'], data['spectrum'])
        self.spectrum_canvas.figure.axes[0].relim()
        self.spectrum_canvas.figure.axes[0].autoscale_view()
        
        # 2. Actualizar waterfall
        self.waterfall_data = np.roll(self.waterfall_data, 1, axis=0)
        self.waterfall_data[0, :] = np.interp(
            np.linspace(0, len(data['spectrum'])-1, len(self.waterfall_data[0])),
            np.arange(len(data['spectrum'])),
            data['spectrum']
        )
        self.waterfall_img.set_data(self.waterfall_data)
        self.waterfall_img.autoscale()
        self.waterfall_canvas.draw_idle()
        
        # 3. Actualizar métricas
        metrics_content = (
            f"FRECUENCIA: {self.frequency:>7} MHz\n"
            f"AMPLITUD:  {data['peak_value']:>7.1f} dBm\n"
            f"ANCHO BW:  {self.bandwidth:>7} kHz\n"
            f"RELAC SNR: {data['snr']:>7.1f} dB\n"
            f"RUIDO AVG: {data['noise']:>7.1f} dB"
        )
        self.metrics_text.set_text(metrics_content)
        self.metrics_canvas.draw_idle()
        
        # 4. Redibujar espectro
        self.spectrum_canvas.draw_idle()
    
    def set_frequency(self, value):
        self.frequency = value
    
    def set_amplitude(self, value):
        self.amplitude = value
    
    def set_bandwidth(self, value):
        self.bandwidth = value
    
    def start_simulation(self):
        self.simulation_active = True
        self.update_timer.start(33)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_simulation(self):
        self.simulation_active = False
        self.update_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def reset_simulation(self):
        self.stop_simulation()
        self.frequency = 1000
        self.amplitude = -50
        self.bandwidth = 100
        self.waterfall_data = np.zeros((50, 400))
        self.start_simulation()
    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        
        # Fondo degradado
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.dark_gray)
        gradient.setColorAt(1, self.medium_gray)
        painter.fillPath(path, gradient)
        
        # Borde
        painter.setPen(QPen(self.light_gray, 2))
        painter.drawPath(path)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < self.title_bar.height():
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_pos') and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

# CLASE PARA ANIMACIÓN DE ANTENAS :(
class AntennaGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent; border: none;")
        
        # Configuración del escenario
        self.width = 800  # Ancho del área de visualización
        self.height = 250  # Alto del área de visualización
        self.scene.setSceneRect(0, 0, self.width, self.height)
        
        # Elementos de fondo
        self.create_background()
        
        # Configuración de antenas
        self.antenna_height = 120
        self.antenna_width = 30
        self.left_antenna_pos = QPointF(100, 150)
        self.right_antenna_pos = QPointF(700, 150)
        self.connection_lines = []
        self.wave_points = []
        self.animation_index = 0
        
        self.create_antennas()
        self.create_wave_path()
        
        # Timer de animación
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS
    
    def create_background(self):
        
        
        # Montañas en el horizonte
        mountain_path = QPainterPath()
        mountain_path.moveTo(0, 180)
        mountain_path.cubicTo(150, 80, 300, 200, 450, 120)
        mountain_path.cubicTo(600, 180, 750, 100, self.width, 160)
        mountain_path.lineTo(self.width, self.height)
        mountain_path.lineTo(0, self.height)
        mountain_path.closeSubpath()
        self.scene.addPath(mountain_path, 
                          QPen(Qt.NoPen), 
                          QColor(50, 80, 40))
        
        # Suelo verde
        ground_gradient = QLinearGradient(0, 180, 0, self.height)
        ground_gradient.setColorAt(0, QColor(60, 120, 60))
        ground_gradient.setColorAt(1, QColor(30, 80, 30))
        self.scene.addRect(0, 180, self.width, self.height - 180,
                          QPen(Qt.NoPen), ground_gradient)
        
        
    
    def create_antennas(self):
        # Antena izquierda (3D con perspectiva)
        left_base = self.scene.addRect(
            self.left_antenna_pos.x() - 20, self.left_antenna_pos.y(),
            40, 15, QPen(Qt.NoPen), QColor(120, 120, 120))
        
        left_mast = self.scene.addPolygon(
            QPolygonF([
                QPointF(self.left_antenna_pos.x() - 3, self.left_antenna_pos.y()),
                QPointF(self.left_antenna_pos.x() + 3, self.left_antenna_pos.y()),
                QPointF(self.left_antenna_pos.x() + 1, self.left_antenna_pos.y() - self.antenna_height),
                QPointF(self.left_antenna_pos.x() - 1, self.left_antenna_pos.y() - self.antenna_height)
            ]), QPen(Qt.NoPen), QColor(100, 100, 100))
        
        # Antena derecha (3D con perspectiva)
        right_base = self.scene.addRect(
            self.right_antenna_pos.x() - 20, self.right_antenna_pos.y(),
            40, 15, QPen(Qt.NoPen), QColor(120, 120, 120))
        
        right_mast = self.scene.addPolygon(
            QPolygonF([
                QPointF(self.right_antenna_pos.x() - 3, self.right_antenna_pos.y()),
                QPointF(self.right_antenna_pos.x() + 3, self.right_antenna_pos.y()),
                QPointF(self.right_antenna_pos.x() + 1, self.right_antenna_pos.y() - self.antenna_height),
                QPointF(self.right_antenna_pos.x() - 1, self.right_antenna_pos.y() - self.antenna_height)
            ]), QPen(Qt.NoPen), QColor(100, 100, 100))
        
        # Elementos de antena (discos)
        for i in range(5):
            y_offset = self.left_antenna_pos.y() - (i * 25)
            radius = 5 + i * 2
            self.scene.addEllipse(
                self.left_antenna_pos.x() - radius, y_offset - radius,
                radius * 2, radius * 2,
                QPen(QColor(150, 150, 150), 1), QColor(180, 180, 180))
            
            self.scene.addEllipse(
                self.right_antenna_pos.x() - radius, y_offset - radius,
                radius * 2, radius * 2,
                QPen(QColor(150, 150, 150), 1), QColor(180, 180, 180))
        
        # Topes de antena
        self.scene.addEllipse(
            self.left_antenna_pos.x() - 6, self.left_antenna_pos.y() - self.antenna_height - 6,
            12, 12, QPen(Qt.NoPen), QColor(200, 200, 200))
        
        self.scene.addEllipse(
            self.right_antenna_pos.x() - 6, self.right_antenna_pos.y() - self.antenna_height - 6,
            12, 12, QPen(Qt.NoPen), QColor(200, 200, 200))
    
    def create_wave_path(self):
        # Crear camino de onda sinusoidal
        start_point = QPointF(self.left_antenna_pos.x(), 
                             self.left_antenna_pos.y() - self.antenna_height)
        end_point = QPointF(self.right_antenna_pos.x(),
                           self.right_antenna_pos.y() - self.antenna_height)
        
        # Generar puntos de onda
        num_points = 50
        for i in range(num_points + 1):
            t = i / num_points
            x = start_point.x() + t * (end_point.x() - start_point.x())
            y = start_point.y() + 30 * np.sin(t * 8 * np.pi)  # Onda sinusoidal
            
            # Añadir perspectiva (más bajo en los extremos)
            y += 40 * (1 - (t - 0.5)**2 / 0.25)
            
            self.wave_points.append(QPointF(x, y))
        
        # Crear líneas de conexión
        for i in range(len(self.wave_points) - 1):
            line = self.scene.addLine(QLineF(self.wave_points[i], self.wave_points[i+1]),
                                    QPen(QColor(100, 100, 100), 1.5))
            self.connection_lines.append(line)
    
    def update_animation(self):
        # Actualizar color de las líneas para efecto de onda
        for i, line in enumerate(self.connection_lines):
            distance = (i - self.animation_index) % len(self.connection_lines)
            
            # Efecto de onda con color que se propaga
            if distance < 10:
                intensity = 255 - (distance * 25)
                alpha = min(255, intensity * 2)
                color = QColor(0, intensity, 255, alpha)
                line.setPen(QPen(color, 2))
            else:
                line.setPen(QPen(QColor(100, 100, 100, 50), 1))
        
        # Mover el punto de animación
        self.animation_index = (self.animation_index + 1) % len(self.connection_lines)
        
        # Efecto de parpadeo en los topes de antena (CORREGIDO)
        blink = np.sin(self.animation_index * 0.2) * 55 + 200  # blink es float64
        for item in self.scene.items():
            if isinstance(item, QGraphicsEllipseItem) and item.rect().width() == 12:
                item.setBrush(QColor(int(blink), int(blink), int(blink)))  # Convertir a int

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpectrumAnalyzerSimulator()
    window.show()
    sys.exit(app.exec_())