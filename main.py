from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import matplotlib.pyplot as plt
import numpy as np
import io
import base64


# 1. Crear la instancia de la app
app = FastAPI()

# 2. Configurar archivos estáticos (CSS, JS, Img)
# Esto le dice a FastAPI que la carpeta "/static" contiene archivos públicos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. Configurar motor de plantillas (HTML)
templates = Jinja2Templates(directory="templates")

# --- RUTAS ---

# Ruta Inicio (GET)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # En FastAPI SIEMPRE debes pasar "request": request al template
    return templates.TemplateResponse("index.html", {
        "request": request,
        "titulo": "Inicio con FastAPI"
    })

# Ruta Contacto (GET)
# 1. MODELO DE DATOS (Para recibir los valores de los sliders)
class SimParams(BaseModel):
    T0: float
    K: float
    tau: float
    u: float
    t_final: float = 20.0
    num_points: int = 100

# 2. RUTA QUE ENTREGA LA PÁGINA (GET)
@app.get("/simulation", response_class=HTMLResponse)
async def simulation(request: Request):
    # Solo entregamos el HTML vacío, la gráfica se cargará después con JS
    return templates.TemplateResponse("simulation.html", {
        "request": request,
        "pagina_actual": "simulacion"
    })

# 3. RUTA API QUE CALCULA LOS DATOS (POST) - ¡ESTO ES LO NUEVO!
@app.post("/api/calculate")
async def calculate_simulation(params: SimParams):
    """
    Recibe los parámetros del slider, calcula los arrays de Numpy 
    y devuelve JSON puro (sin imágenes).
    """
    # Vector de Tiempo
    t = np.linspace(0, params.t_final, params.num_points)
    
    # Solución por Laplace (Tu fórmula matemática)
    # T(t) = K*u*(1 - exp(-t/tau)) + T0*exp(-t/tau)
    T = params.K * params.u * (1 - np.exp(-t / params.tau)) + params.T0 * np.exp(-t / params.tau)

    # Devolvemos los datos como listas simples de Python
    return JSONResponse(content={
        "labels": t.tolist(), # Eje X
        "data": T.tolist()    # Eje Y
    })

@app.get("/exposure", response_class=HTMLResponse)
async def exposure(request: Request):
    return templates.TemplateResponse("exposure.html", {
        "request": request,
        "pagina_actual": "exposure"
    })


# Ruta para procesar datos del formulario (POST)
#@app.post("/procesar-datos", response_class=HTMLResponse)
#async def procesar_datos(request: Request, nombre: str = Form(...), edad: int = Form(...)):
#    """
#    Los parámetros 'nombre' y 'edad' deben coincidir con el 'name'
#    de tus inputs en el HTML.
#    """
#    mensaje = f"Hola {nombre}, tienes {edad} años. Procesado por FastAPI."
#    
#    print(mensaje) # Verás esto en la consola del servidor
#
#    return templates.TemplateResponse("index.html", {
#        "request": request,
#        "titulo": "Resultado",
#       "resultado": mensaje
#    })