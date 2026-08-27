# Manual de Mantenimiento y Operación Técnica

Este documento describe las tareas de mantenimiento periódico, actualización de datos climáticos, auditoría y respaldo de **AAnalogos**.

---

## 1. Actualización Periódica de Datos Climáticos

Las agencias meteorológicas internacionales (NOAA PSL, CPC, NCEI, CSU) publican actualizaciones mensuales de sus índices durante los primeros 5 a 10 días de cada mes.

### Procedimiento de Actualización Automatizada
Ejecute el script de descarga y actualización:
```bash
python scripts/download_data.py
```
El script:
1. Conecta con las URLs oficiales configuradas en `config/data_sources.yaml`.
2. Verifica el código de respuesta HTTP (200 OK) y el tamaño del archivo.
3. Descarga a un archivo temporal y realiza un reemplazo atómico en `data/`.
4. Transforma y estructura los archivos a matrices estándar de 12 meses.

---

## 2. Auditoría Automatizada de Calidad de Datos

Tras cualquier actualización, ejecute la auditoría de consistencia:
```bash
python scripts/audit_sources.py
```
El reporte identificará:
* Si el nuevo mes fue incorporado correctamente.
* Si aparecieron valores sentinela no documentados.
* El rango de ventanas de 6 meses completamente válidas.

---

## 3. Gestión del Servicio en Linux (`systemd`)

| Acción | Comando |
| :--- | :--- |
| **Iniciar servicio** | `sudo systemctl start aanalogos` |
| **Detener servicio** | `sudo systemctl stop aanalogos` |
| **Reiniciar servicio** | `sudo systemctl restart aanalogos` |
| **Ver estado** | `sudo systemctl status aanalogos` |
| **Ver logs en vivo** | `journalctl -u aanalogos -f` |

---

## 4. Procedimiento de Respaldo (Backup)

Para respaldar el estado completo de la aplicación y sus datos históricos:
```bash
tar -czvf backup_aanalogos_$(date +%Y%m%d).tar.gz /opt/aanalogos/data /opt/aanalogos/config
```
