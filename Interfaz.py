import tkinter as tk
from tkinter import filedialog, messagebox
import Validacion

ruta_pdf = None  

def seleccionar_pdf():
    global ruta_pdf
    ruta_pdf = filedialog.askopenfilename(
        title="Selecciona el archivo PDF de listado y certificados",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if ruta_pdf:
        nombre_archivo = ruta_pdf.split('/')[-1]
        label_pdf.config(
            text=f"✅ {nombre_archivo}", 
            fg="#27ae60", 
            font=("Arial", 10, "bold")
        )
        frame_inputs.pack(pady=10)  
        boton_validar.pack(pady=8)   
def guardar_resultados(resultado):
    """Función para guardar los resultados en un archivo txt"""
    try:
        archivo = filedialog.asksaveasfilename(
            title="Guardar resultados de validación",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(resultado)
            messagebox.showinfo(
                "✅ Guardado Exitoso", 
                f"Los resultados se guardaron correctamente en:\n{archivo}"
            )
    except Exception as e:
        messagebox.showerror(
            "❌ Error al Guardar", 
            f"No se pudieron guardar los resultados:\n{str(e)}"
        )

def validar_pdf():
    try:
        inicio = entry_inicio.get()
        fin = entry_fin.get()

        if not inicio.isdigit() or not fin.isdigit():
            messagebox.showerror("❌ Error", "Las páginas deben ser números enteros.")
            return

        pagina_inicio = int(inicio)
        pagina_fin = int(fin)

        if pagina_inicio < 1 or pagina_fin < pagina_inicio:
            messagebox.showerror("❌ Error", "Rango de páginas inválido.")
            return

        resultado = Validacion.procesar_pdf(ruta_pdf, pagina_inicio - 1, pagina_fin)

        # Ventana de resultados mejorada
        resultado_ventana = tk.Toplevel()
        resultado_ventana.title("📊 Resultados de Validación")
        resultado_ventana.geometry("850x600")  # Aumenté altura para el botón
        resultado_ventana.configure(bg='#f8f9fa')
        
        # Título de la ventana de resultados
        titulo_resultado = tk.Label(
            resultado_ventana, 
            text="📋 Resultados de la Validación",
            font=("Arial", 16, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50',
            pady=15
        )
        titulo_resultado.pack()

        # Frame para el texto con scrollbar
        frame_texto = tk.Frame(resultado_ventana, bg='#f8f9fa')
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        texto = tk.Text(
            frame_texto, 
            wrap=tk.WORD, 
            font=("Consolas", 11),
            bg='white',
            fg='#2c3e50',
            relief=tk.SOLID,
            bd=1,
            padx=10,
            pady=10
        )
        
        scrollbar = tk.Scrollbar(frame_texto, command=texto.yview)
        texto.config(yscrollcommand=scrollbar.set)
        
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        texto.insert(tk.END, resultado)
        texto.config(state=tk.DISABLED)  # Solo lectura

        # Frame para el botón de descarga
        frame_boton = tk.Frame(resultado_ventana, bg='#f8f9fa')
        frame_boton.pack(pady=15)

        # Botón bonito para descargar
        boton_descargar = tk.Button(
            frame_boton,
            text="💾 Descargar Resultados",
            command=lambda: guardar_resultados(resultado),
            font=("Arial", 12, "bold"),
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        boton_descargar.pack()

    except Exception as e:
        messagebox.showerror("❌ Error", f"Ocurrió un error:\n{e}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("🔍 Validador de Certificados")
ventana.geometry("500x380")  # Ajusté la altura
ventana.configure(bg='#f8f9fa')
ventana.resizable(False, False)

# Título principal con emoji
label_titulo = tk.Label(
    ventana, 
    text="🔍 Validador de Certificados PDF",
    font=("Arial", 16, "bold"),
    bg='#f8f9fa',
    fg='#2c3e50',
    pady=20
)
label_titulo.pack()

# Subtítulo
label_subtitulo = tk.Label(
    ventana,
    text="Selecciona un archivo PDF para validar certificados",
    font=("Arial", 11),
    bg='#f8f9fa',
    fg='#7f8c8d'
)
label_subtitulo.pack(pady=(0, 20))

# Botón para seleccionar PDF con estilo mejorado
boton_pdf = tk.Button(
    ventana, 
    text="📁 Seleccionar PDF",
    command=seleccionar_pdf,
    font=("Arial", 12, "bold"),
    bg='#3498db',
    fg='white',
    relief=tk.FLAT,
    padx=30,
    pady=10,
    cursor='hand2'
)
boton_pdf.pack(pady=10)

# Label para mostrar PDF seleccionado
label_pdf = tk.Label(
    ventana, 
    text="", 
    font=("Arial", 10),
    bg='#f8f9fa',
    fg='#7f8c8d'
)
label_pdf.pack(pady=5)

# Frame para inputs con mejor diseño (inicialmente oculto)
frame_inputs = tk.Frame(ventana, bg='#f8f9fa', pady=5)  # Reducido padding

# Estilo para labels
label_style = {"font": ("Arial", 11), "bg": '#f8f9fa', "fg": '#2c3e50'}

tk.Label(frame_inputs, text="📄 Página inicio:", **label_style).grid(
    row=0, column=0, padx=10, pady=6, sticky="e"  # Reducido pady de 8 a 6
)
entry_inicio = tk.Entry(
    frame_inputs, 
    width=8, 
    font=("Arial", 11),
    justify='center',
    relief=tk.SOLID,
    bd=1
)
entry_inicio.grid(row=0, column=1, padx=10, pady=6)

tk.Label(frame_inputs, text="📄 Página fin:", **label_style).grid(
    row=1, column=0, padx=10, pady=6, sticky="e"
)
entry_fin = tk.Entry(
    frame_inputs, 
    width=8, 
    font=("Arial", 11),
    justify='center',
    relief=tk.SOLID,
    bd=1
)
entry_fin.grid(row=1, column=1, padx=10, pady=6)

# Botón de validación con estilo mejorado (inicialmente oculto)
boton_validar = tk.Button(
    ventana, 
    text="✅ Comenzar Validación",
    command=validar_pdf,
    font=("Arial", 12, "bold"),
    bg='#27ae60',
    fg='white',
    relief=tk.FLAT,
    padx=30,
    pady=10,
    cursor='hand2'
)

ventana.mainloop()