import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# Configuración del estilo oscuro
#plt.style.use('ligth_background')

# --- Parámetros iniciales ---
Ex0_init = 1.0
Ey0_init = 1.0
fase_init = np.pi / 2
k = 2 * np.pi / 2
w = 2 * np.pi
z = np.linspace(0, 10, 500)

# Configuración de la figura y el layout
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d', facecolor='grey')
plt.subplots_adjust(left=0.1, bottom=0.25) # Espacio para los sliders

# Configuración de los Sliders (Manual)
ax_ex = plt.axes([0.2, 0.15, 0.6, 0.03], facecolor="#3B1C1C")
ax_ey = plt.axes([0.2, 0.10, 0.6, 0.03], facecolor="#352121")
ax_phi = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor="#332020")

s_ex = Slider(ax_ex, 'Amp Horizontal (Ex)', 0.0, 2.0, valinit=Ex0_init, color="#00032c")
s_ey = Slider(ax_ey, 'Amp Vertical (Ey)', 0.0, 2.0, valinit=Ey0_init, color="#011a02")
s_phi = Slider(ax_phi, 'Fase (rad)', -np.pi, np.pi, valinit=fase_init, color="#0084c2")

def update_plot(frame):
    
    # Obtener valores de los sliders
    Ex0 = s_ex.val
    Ey0 = s_ey.val
    fase = s_phi.val
    
    t = frame / 20.0
    ax.clear()
    
    # Ejes y rejilla
    ax.set_facecolor('white')
    ax.grid(False) # Quitar rejilla para un look más limpio
    
    # Cálculo de los campos
    Ex = Ex0 * np.cos(k * z - w * t)
    Ey = Ey0 * np.cos(k * z - w * t + fase)
    
    # Dibujar la onda resultante (Efecto neón)
    ax.plot(z, Ex, Ey, label='Campo Eléctrico (E)', color='#cc00ff', lw=2.5, zorder=10)
    
    # Proyecciones (Sombras proyectadas en los planos)
    ax.plot(z, Ex, zs=-2, zdir='z', color="#0d2d33", alpha=0.4, lw=1) # Componente X
    ax.plot(z, Ey, zs=2, zdir='y', color='#ff007f', alpha=0.4, lw=1)  # Componente Y

    # Estética
    ax.set_xlim(0, 10)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    ax.set_title(f'Simulación de Polarizacion Circular (t={t:.2f}s)', color='white', pad=20)
    ax.set_xlabel('Eje Z (Propagación)', color='gray')
    ax.set_ylabel('Eje X (Horizontal)', color="#11373f")
    ax.set_zlabel('Eje Y (Vertical)', color='#ff007f')
    
    # Eliminar los ticks del fondo para que se vea más minimalista
    ax.xaxis.pane.fill = True
    ax.yaxis.pane.fill = True
    ax.zaxis.pane.fill = True

# Animación
ani = FuncAnimation(fig, update_plot, frames=100, interval=50, cache_frame_data=False)
plt.show()