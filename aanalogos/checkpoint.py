"""
Módulo de gestión de sesión multi-usuario, persistencia de checkpoints (LocalStorage)
y mecanismo Anti-Sleep (Keep-Alive) para AAnalogos.
"""

import json
import base64
import urllib.parse
from typing import Dict, Any, Optional, List
from .config import UMBRALES_OSCILACIONES, LONGITUD_VENTANA_OPERACIONAL


CLAVE_STORAGE_DEFECTO = "aanalogos_user_checkpoint_v1"
INDICES_DEFECTO = ["RONI", "TNA", "ONIv6"]


def obtener_configuracion_defecto() -> Dict[str, Any]:
    """Retorna la configuración inicial estándar del sistema."""
    return {
        "indices": list(INDICES_DEFECTO),
        "modo_analisis": "Operacional",
        "longitud_ventana": LONGITUD_VENTANA_OPERACIONAL,
        "year_objetivo": 2015,
        "mes_objetivo": 10,
        "tipo_reanalisis": "Retrospectivo Completo (Todos los años históricos)",
        "umbrales_usuario": {k: list(v) for k, v in UMBRALES_OSCILACIONES.items()},
        "seccion": "3. Análisis de años análogos",
    }


def validar_y_sanitizar_checkpoint(
    datos: Any,
    indices_validos: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Valida y sanea un diccionario de checkpoint, asegurando tipos y límites correctos.
    Si algún campo es inválido o falta, asigna su valor por defecto de forma segura.
    """
    cfg_default = obtener_configuracion_defecto()
    if not isinstance(datos, dict):
        return cfg_default

    if indices_validos is None:
        indices_validos = list(UMBRALES_OSCILACIONES.keys())

    resultado = {}

    # 1. Índices seleccionados
    indices_raw = datos.get("indices")
    if isinstance(indices_raw, list):
        indices_limpios = [str(k) for k in indices_raw if str(k) in indices_validos]
        resultado["indices"] = indices_limpios if indices_limpios else list(INDICES_DEFECTO)
    else:
        resultado["indices"] = list(INDICES_DEFECTO)

    # 2. Modo de análisis
    modo = datos.get("modo_analisis")
    if modo in ["Operacional", "Reanálisis Histórico"]:
        resultado["modo_analisis"] = modo
    else:
        resultado["modo_analisis"] = "Operacional"

    # 3. Longitud de ventana
    try:
        vent = int(datos.get("longitud_ventana", LONGITUD_VENTANA_OPERACIONAL))
        resultado["longitud_ventana"] = vent if vent in [6, 12] else LONGITUD_VENTANA_OPERACIONAL
    except (ValueError, TypeError):
        resultado["longitud_ventana"] = LONGITUD_VENTANA_OPERACIONAL

    # 4. Año objetivo
    try:
        y_obj = int(datos.get("year_objetivo", 2015))
        resultado["year_objetivo"] = y_obj if 1950 <= y_obj <= 2100 else 2015
    except (ValueError, TypeError):
        resultado["year_objetivo"] = 2015

    # 5. Mes objetivo
    try:
        m_obj = int(datos.get("mes_objetivo", 10))
        resultado["mes_objetivo"] = m_obj if 1 <= m_obj <= 12 else 10
    except (ValueError, TypeError):
        resultado["mes_objetivo"] = 10

    # 6. Tipo de reanálisis
    tipo_r = datos.get("tipo_reanalisis")
    if isinstance(tipo_r, str) and "Backtesting" in tipo_r:
        resultado["tipo_reanalisis"] = "Backtesting / Simulación Tiempo Real (Corte en $Y_{\\text{obj}}$)"
    else:
        resultado["tipo_reanalisis"] = "Retrospectivo Completo (Todos los años históricos)"

    # 7. Umbrales personalizados
    umbrales_raw = datos.get("umbrales_usuario")
    umbrales_limpios = {}
    for cod, (r_def, mad_def) in UMBRALES_OSCILACIONES.items():
        if isinstance(umbrales_raw, dict) and cod in umbrales_raw:
            val_pair = umbrales_raw[cod]
            if isinstance(val_pair, (list, tuple)) and len(val_pair) >= 2:
                try:
                    r_val = float(val_pair[0])
                    mad_val = float(val_pair[1])
                    if -1.0 <= r_val <= 1.0 and 0.0 <= mad_val <= 10.0:
                        umbrales_limpios[cod] = (r_val, mad_val)
                    else:
                        umbrales_limpios[cod] = (r_def, mad_def)
                except (ValueError, TypeError):
                    umbrales_limpios[cod] = (r_def, mad_def)
            else:
                umbrales_limpios[cod] = (r_def, mad_def)
        else:
            umbrales_limpios[cod] = (r_def, mad_def)
    resultado["umbrales_usuario"] = umbrales_limpios

    # 8. Sección de navegación
    sec = datos.get("seccion")
    secciones_validas = [
        "1. Estado de datos disponibles",
        "2. Configuración de umbrales",
        "3. Análisis de años análogos",
        "4. Explorador de índices",
        "5. Metodología",
        "Documentación y créditos",
    ]
    resultado["seccion"] = sec if sec in secciones_validas else "3. Análisis de años análogos"

    return resultado


def codificar_checkpoint(config_dict: Dict[str, Any]) -> str:
    """Serializa la configuración a una cadena JSON compacta codificada en Base64 seguro para URL."""
    datos_exportables = dict(config_dict)
    if "umbrales_usuario" in datos_exportables:
        datos_exportables["umbrales_usuario"] = {
            k: [float(v[0]), float(v[1])] for k, v in datos_exportables["umbrales_usuario"].items()
        }
    json_bytes = json.dumps(datos_exportables, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(json_bytes).decode("ascii")


def decodificar_checkpoint(
    cadena_codificada: str,
    indices_validos: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Decodifica y valida una cadena de checkpoint desde URL o almacenamiento."""
    if not cadena_codificada or not isinstance(cadena_codificada, str):
        return obtener_configuracion_defecto()

    try:
        padded = cadena_codificada + "=" * (-len(cadena_codificada) % 4)
        json_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
        datos = json.loads(json_bytes.decode("utf-8"))
        return validar_y_sanitizar_checkpoint(datos, indices_validos=indices_validos)
    except Exception:
        try:
            datos = json.loads(urllib.parse.unquote(cadena_codificada))
            return validar_y_sanitizar_checkpoint(datos, indices_validos=indices_validos)
        except Exception:
            return obtener_configuracion_defecto()


def generar_componente_cliente(
    estado_actual: Dict[str, Any],
    clave_storage: str = CLAVE_STORAGE_DEFECTO
) -> str:
    """
    Genera el script HTML/JS invisible que:
    1. Ejecuta un Web Worker en segundo plano (Keep-Alive / Anti-Sleep) para evitar desconexiones.
    2. Guarda de forma asíncrona el checkpoint del usuario en el LocalStorage de su navegador.
    3. Si la página se abre sin parámetros de estado en la URL, restaura automáticamente el último checkpoint desde LocalStorage.
    """
    estado_serializado = codificar_checkpoint(estado_actual)

    template = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0; padding:0; overflow:hidden;">
    <script>
    (function() {
        const STORAGE_KEY = "__STORAGE_KEY__";
        const CURRENT_STATE = "__CURRENT_STATE__";

        // 1. Guardar estado actual en LocalStorage del navegador del cliente
        try {
            if (window.parent && window.parent.localStorage) {
                window.parent.localStorage.setItem(STORAGE_KEY, CURRENT_STATE);
            }
        } catch(e) {
            console.warn("AAnalogos: LocalStorage no accesible", e);
        }

        // 2. Restauración automática al iniciar sin parámetros
        try {
            if (window.parent && window.parent.location) {
                const searchParams = new URLSearchParams(window.parent.location.search);
                const hasStateInUrl = searchParams.has("state");
                const hasDocInUrl = searchParams.has("doc");
                
                // Si la URL está limpia (sin ?state= ni ?doc=), comprobar si existe checkpoint previo
                if (!hasStateInUrl && !hasDocInUrl) {
                    const savedState = window.parent.localStorage.getItem(STORAGE_KEY);
                    if (savedState && savedState !== CURRENT_STATE && savedState.length > 10) {
                        searchParams.set("state", savedState);
                        const newUrl = window.parent.location.pathname + "?" + searchParams.toString();
                        window.parent.location.replace(newUrl);
                    }
                }
            }
        } catch(e) {
            console.warn("AAnalogos: Error en auto-restauración", e);
        }

        // 3. Mecanismo Anti-Sleep (Keep-Alive mediante Web Worker + Fetch Heartbeat)
        try {
            if (!window._aanalogos_keep_alive_active) {
                window._aanalogos_keep_alive_active = true;

                // Crear un Web Worker desacoplado mediante Blob para que el navegador no lo congele en background
                const workerScript = `
                    let intervalId = null;
                    self.onmessage = function(e) {
                        if (e.data === 'start') {
                            if (!intervalId) {
                                intervalId = setInterval(function() {
                                    self.postMessage('heartbeat');
                                }, 35000); // 35 segundos
                            }
                        } else if (e.data === 'stop') {
                            if (intervalId) {
                                clearInterval(intervalId);
                                intervalId = null;
                            }
                        }
                    };
                `;
                const blob = new Blob([workerScript], { type: 'application/javascript' });
                const worker = new Worker(URL.createObjectURL(blob));

                const sendPing = function() {
                    try {
                        fetch(window.location.origin + '/_stcore/health', {
                            method: 'GET',
                            cache: 'no-store',
                            headers: { 'X-Aanalogos-KeepAlive': '1' }
                        }).catch(function() {
                            fetch(window.location.origin + '/', { method: 'HEAD', cache: 'no-store' }).catch(function() {});
                        });
                    } catch(err) {}
                };

                worker.onmessage = function(e) {
                    if (e.data === 'heartbeat') {
                        sendPing();
                    }
                };

                worker.postMessage('start');

                if (window.parent && window.parent.document) {
                    window.parent.document.addEventListener('visibilitychange', function() {
                        if (window.parent.document.visibilityState === 'visible') {
                            sendPing();
                        }
                    });
                }
            }
        } catch(e) {
            console.warn("AAnalogos: Keep-Alive worker no pudo iniciarse", e);
        }
    })();
    </script>
    </body>
    </html>
    """
    return template.replace("__STORAGE_KEY__", clave_storage).replace("__CURRENT_STATE__", estado_serializado)

