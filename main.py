from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Literal
import sqlite3

app = FastAPI()

# Configuración de la base de datos SQLite
DATABASE = 'riesgos_forjahierro.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_reportante TEXT NOT NULL,
        area_taller TEXT NOT NULL,
        nivel_riesgo INTEGER NOT NULL,
        requiere_parada_planta BOOLEAN NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

class ReporteIncidente(BaseModel):
    nombre_reportante: str
    area_taller: str
    nivel_riesgo: int = Field(..., ge=1, le=5, description="Nivel de riesgo entre 1 y 5")
    requiere_parada_planta: bool

@app.get("/interfaz", response_class=HTMLResponse)
def interfaz():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Incidente - ForjaHierro</title>
        <style>
            body {
                background: linear-gradient(120deg, #23272b 70%, #ff5722 200%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #f2f2f2;
                margin: 0;
                padding: 0;
                min-height: 100vh;
            }
            .container {
                background: #353940f2;
                max-width: 430px;
                margin: 40px auto 0 auto;
                padding: 2em 2.5em 2.5em 2.5em;
                border-radius: 10px;
                box-shadow: 0 8px 35px 6px #101217ce;
                border-top: 7px solid #ff5722;
            }
            h1 {
                color: #ff5722;
                text-align: center;
                margin-bottom: 1.1em;
                letter-spacing: 2px;
                text-shadow: 0 2px 15px #000b;
            }
            label {
                display: block;
                margin: 0.7em 0 0.2em 0;
                font-weight: 500;
                color: #f7f7f7;
            }
            input[type="text"], select {
                width: 100%;
                padding: 0.6em 0.7em;
                margin-bottom: 0.8em;
                border: none;
                border-radius: 6px;
                background: #292b2e;
                color: #f2f2f2;
                font-size: 1.04em;
                box-shadow: 0 1px 4px #00000033;
            }
            input[type="checkbox"] {
                accent-color: #ff5722;
                transform: scale(1.2);
                margin-right: 0.4em;
                vertical-align: middle;
            }
            .form-group {
                margin-bottom: 1.3em;
            }
            button {
                background-color: #ea1a22;
                color: #fff;
                border: none;
                padding: 0.8em 0;
                width: 100%;
                border-radius: 6px;
                font-size: 1.15em;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.18s;
                letter-spacing: 1px;
                margin-top: 10px;
                box-shadow: 0 3px 17px #10121799;
            }
            button:hover {
                background-color: #ff5722;
            }
            #resultado {
                margin-top: 2em;
                font-size: 1.15em;
                background: #23272b;
                border: 3px solid #ea1a22;
                border-radius: 12px;
                min-height: 60px;
                padding: 1.2em;
                color: #fff;
                box-shadow: 0 1px 14px #ea1a2257;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            #resultado[data-status="ok"] {
                border: 3px solid #43a047;
                color: #fff;
                background: #363b36;
            }
            ::placeholder { color: #bdbdbd; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Reporte de Incidente</h1>
            <form id="formIncidente" autocomplete="off">
                <div class="form-group">
                    <label for="nombre">Nombre del reportante:</label>
                    <input type="text" id="nombre" name="nombre" placeholder="Ingrese su nombre" required />
                </div>
                <div class="form-group">
                    <label for="area">Área del taller:</label>
                    <input type="text" id="area" name="area" placeholder="Área del incidente" required />
                </div>
                <div class="form-group">
                    <label for="nivel">Nivel de riesgo:</label>
                    <select id="nivel" name="nivel" required>
                        <option value="" disabled selected>Seleccione nivel</option>
                        <option value="1">1 - Bajo</option>
                        <option value="2">2</option>
                        <option value="3">3 - Medio</option>
                        <option value="4">4</option>
                        <option value="5">5 - Alto</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="checkbox" id="parada" name="parada">
                    <label for="parada" style="display: inline;">Requiere parada de planta</label>
                </div>
                <button type="submit">Enviar Reporte</button>
            </form>
            <div id="resultado"></div>
        </div>
        <script>
            document.getElementById('formIncidente').addEventListener('submit', async function(e){
                e.preventDefault();
                const resultado = document.getElementById('resultado');
                resultado.textContent = '';
                resultado.removeAttribute('data-status');

                const nombre = document.getElementById('nombre').value.trim();
                const area = document.getElementById('area').value.trim();
                const nivel = parseInt(document.getElementById('nivel').value, 10);
                const parada = document.getElementById('parada').checked;

                if (!nombre || !area || isNaN(nivel)) {
                    resultado.textContent = 'Por favor, complete todos los campos obligatorios.';
                    resultado.setAttribute('data-status', 'error');
                    return;
                }

                const datos = {
                    nombre_reportante: nombre,
                    area_taller: area,
                    nivel_riesgo: nivel,
                    requiere_parada_planta: parada
                };

                resultado.innerHTML = '<span style="color:#bbb;">Enviando reporte...</span>';
                try {
                    const resp = await fetch('/api/registrar-incidente', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(datos)
                    });

                    if (!resp.ok) {
                        resultado.textContent = 'Error al registrar el incidente';
                        resultado.setAttribute('data-status', 'error');
                        return;
                    }
                    const data = await resp.json();

                    if (data.alerta) {
                        resultado.textContent = data.alerta;
                        resultado.setAttribute('data-status', 'alerta');
                        resultado.style.borderColor = "#ea1a22";
                        resultado.style.background = "#ff5722";
                        resultado.style.color = "#fff";
                    } else if (data.mensaje) {
                        resultado.textContent = data.mensaje;
                        resultado.setAttribute('data-status', 'ok');
                        resultado.style.borderColor = "#43a047";
                        resultado.style.background = "#363b36";
                        resultado.style.color = "#fff";
                    } else {
                        resultado.textContent = 'Respuesta desconocida del servidor.';
                    }
                } catch (err) {
                    resultado.textContent = 'Error de red. Intente nuevamente.';
                    resultado.setAttribute('data-status', 'error');
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/registrar-incidente")
def registrar_incidente(reporte: ReporteIncidente):
    # Guardar en la base de datos
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO incidentes (nombre_reportante, area_taller, nivel_riesgo, requiere_parada_planta)
        VALUES (?, ?, ?, ?)
    """, (
        reporte.nombre_reportante,
        reporte.area_taller,
        reporte.nivel_riesgo,
        int(reporte.requiere_parada_planta),  # sqlite no tiene boolean, se usa 0/1
    ))
    conn.commit()
    conn.close()

    if reporte.nivel_riesgo in (4, 5) or reporte.requiere_parada_planta:
        return {"alerta": "ALERTA ROJA: Detener operaciones y notificar gerencia"}
    else:
        return {"mensaje": "Incidente registrado, revisión ordinaria"}
 