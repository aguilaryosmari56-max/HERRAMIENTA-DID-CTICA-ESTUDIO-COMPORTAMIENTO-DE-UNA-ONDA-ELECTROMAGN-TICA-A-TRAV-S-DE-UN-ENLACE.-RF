import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuración de estilo visual
plt.style.use('dark_background')

def calcular_polarizacion():
    print("--- Configuración de la Onda Electromagnética ---")
    try:
        ex0 = float(input("Ingrese Amplitud Horizontal (Ex0) [ej: 1.0]: "))
        ey0 = float(input("Ingrese Amplitud Vertical (Ey0) [ej: 1.0]: "))
        print("La fase se ingresa en grados (0 para lineal, 90 para circular/elíptica)")
        fase_deg = float(input("Ingrese desfase (grados) [ej: 90]: "))
        fase_rad = np.radians(fase_deg)
    except ValueError:
        print("Entrada no válida. Usando valores por defecto (Circular).")
        ex0, ey0, fase_rad = 1.0, 1.0, np.pi/2

    return ex0, ey0, fase_rad

# 1. Captura de datos manual
Ex0, Ey0, fase = calcular_polarizacion()

# 2. Parámetros de la simulación
z = np.linspace(0, 10, 1000)
k = 2 * np.pi / 4  # Número de onda
w = 2 * np.pi      # Frecuencia angular

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

def animate(i):
    ax.clear()
    t = i / 20.0
    
    # Ecuaciones de Maxwell para los componentes del campo E
    Ex = Ex0 * np.cos(k * z - w * t)
    Ey = Ey0 * np.cos(k * z - w * t + fase)
    
    # Dibujado de componentes con colores neón
    # Componente Horizontal (Azul Cian)
    ax.plot(z, Ex, zs=-2, zdir='z', color='#00f2ff', alpha=0.3, label='Componente Ex')
    # Componente Vertical (Rosa Neón)
    ax.plot(z, Ey, zs=2, zdir='y', color='#ff0077', alpha=0.3, label='Componente Ey')
    
    # Vector Resultante (Púrpura/Blanco)
    ax.plot(z, Ex, Ey, color='#bcff00', lw=2, label='Vector Campo E')
    
    # Dibujar el "frente de onda" en la posición final para ver la forma de la polarización
    ax.scatter([10], [Ex[-1]], [Ey[-1]], color='white', s=50)

    # Configuración de ejes y estética
    ax.set_xlim(0, 10)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    ax.set_title(f"Polarización: Ex0={Ex0} | Ey0={Ey0} | Fase={np.degrees(fase):.1f}°", color='white')
    ax.set_xlabel('Eje Z (Propagación)', color='gray')
    ax.set_ylabel('Eje X (Horizontal)', color='#00f2ff')
    ax.set_zlabel('Eje Y (Vertical)', color='#ff0077')
    
    # Ocultar paneles para mayor limpieza visual
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)
    ax.grid(color='gray', linestyle='--', alpha=0.1)

# Crear la animación
ani = FuncAnimation(fig, animate, frames=100, interval=30, blit=False)

print("\nGenerando animación... Cierre la ventana de la gráfica para terminar.")
plt.show()