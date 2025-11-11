# 🌐 Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido de alto rendimiento para scraping, análisis y procesamiento de páginas web utilizando Python con arquitectura cliente-servidor.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso Rápido](#-uso-rápido)
- [Documentación Detallada](#-documentación-detallada)
- [Solución de Problemas](#Solución-de-problemas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Autor](#-autor)

---

## 🎯 Descripción

Este proyecto implementa un sistema distribuido que permite:

- **Scraping asíncrono** de páginas web sin bloquear operaciones
- **Captura de screenshots** reales usando Selenium/Chromium
- **Análisis de rendimiento** web (tiempos de carga, métricas de navegación)
- **Procesamiento de imágenes** con generación de thumbnails
- **Comunicación eficiente** entre servidores mediante protocolo TCP custom
- **Procesamiento paralelo** usando multiprocessing

### Casos de Uso

- Monitoreo de sitios web
- Análisis de rendimiento de aplicaciones web
- Generación de reportes de accesibilidad
- Captura automatizada de screenshots
- Extracción de datos estructurados

---

## ✨ Características

### Servidor A (Scraping Asíncrono)
- ✅ HTTP Server con `asyncio` y `aiohttp`
- ✅ Scraping no bloqueante con `BeautifulSoup`
- ✅ Extracción de metadatos (Open Graph, Twitter Cards, SEO)
- ✅ Cliente TCP asíncrono para comunicación con Servidor B
- ✅ Rate limiting y timeouts configurables

### Servidor B (Procesamiento Distribuido)
- ✅ Pool de procesos con `multiprocessing`
- ✅ Screenshots reales con `Selenium` + `Chromium`
- ✅ Análisis de rendimiento web (Performance API)
- ✅ Procesamiento de imágenes asíncrono
- ✅ Manejo de múltiples tareas concurrentes

### Protocolo de Comunicación
- ✅ Serialización JSON optimizada
- ✅ Validación de mensajes
- ✅ Manejo robusto de errores
- ✅ Soporte para diferentes tipos de tareas

---

### Flujo de Ejecución

```
1. Cliente → HTTP GET → Servidor A
2. Servidor A → Scraping asíncrono (aiohttp + BeautifulSoup)
3. Servidor A → TCP request → Servidor B
4. Servidor B → Distribuye tareas en pool de procesos:
   ├─ Worker 1: Screenshot (Selenium)
   ├─ Worker 2: Performance Analysis
   └─ Worker 3: Image Processing
5. Servidor B → TCP response → Servidor A
6. Servidor A → HTTP JSON response → Cliente
```

---

## 📦 Requisitos

### Software Requerido

```bash
# Python
Python 3.8+

# Chromium/Chrome (para screenshots)
chromium-browser >= 90.0
chromium-chromedriver >= 90.0
```

### Dependencias Python

Ver [`requirements.txt`](requirements.txt):
```
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
Pillow>=10.0.0
aiofiles>=23.0.0
selenium>=4.15.0
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone <repository_url>
cd TP2
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv env

# Activar entorno virtual
# Linux/macOS:
source env/bin/activate

# Windows:
env\Scripts\activate
```

### 3. Instalar Dependencias Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instalar Chromium/ChromeDriver

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

#### macOS (con Homebrew):
```bash
brew install chromium
brew install chromedriver
```

#### Verificar instalación:
```bash
chromium-browser --version
chromedriver --version
```

---

## ⚡ Uso Rápido

### Inicio Manual

#### Terminal 1: Servidor B (Procesamiento)
```bash
python server_processing.py -i localhost -p 9000 -n 4
```

**Parámetros:**
- `-i, --ip`: Dirección IP de escucha (default: localhost)
- `-p, --port`: Puerto de escucha (default: 9000)
- `-n, --processes`: Número de workers en el pool (default: núcleos CPU)

#### Terminal 2: Servidor A (Scraping)
```bash
python server_scraping.py -i localhost -p 8000
```

**Parámetros:**
- `-i, --ip`: Dirección IP de escucha (default: localhost)
- `-p, --port`: Puerto HTTP (default: 8000)
- `--processing-host`: IP del Servidor B (default: localhost)
- `--processing-port`: Puerto del Servidor B (default: 9000)

#### Terminal 3: Cliente

```bash
# Scraping básico (sin procesamiento)
python client.py --url https://example.com

# Scraping + Procesamiento completo
python client.py --url https://example.com --full

# Con servidor custom
python client.py --url https://example.com --server http://localhost:8000 --full
```

**Parámetros del Cliente:**
- `--url`: URL a analizar (requerido)
- `--full`: Habilitar procesamiento completo (opcional)
- `--server`: URL del Servidor A (default: http://localhost:8000)
- `--output`: Guardar resultado en archivo JSON (opcional)

---

## 📖 Documentación Detallada

### Endpoints del Servidor A

#### `GET /scrape`

Scraping de una URL.

**Parámetros:**
- `url` (string, requerido): URL a scrapear
- `full` (boolean, opcional): Si `true`, incluye procesamiento completo

**Ejemplo:**
```bash
curl "http://localhost:8000/scrape?url=https://example.com&full=true"
```

**Respuesta:**
```json
{
  "url": "https://example.com",
  "timestamp": "2025-11-11T20:00:00Z",
  "status": "success",
  "scraping_data": {
    "basic": {
      "title": "Example Domain",
      "text_preview": "...",
      "word_count": 25
    },
    "structure": {...},
    "links": [...],
    "images": [...],
    "metadata": {...}
  },
  "processing_data": {
    "screenshot": {...},
    "performance": {...},
    "images": {...}
  }
}
```

#### `GET /health`

Health check del servidor.

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-11T20:00:00Z"
}
```

### Protocolo de Comunicación

El protocolo entre servidores usa TCP con mensajes length-prefixed JSON:

```
[4 bytes: length][JSON payload]
```

**Tipos de mensajes:**
- `REQUEST`: Solicitud de procesamiento
- `RESPONSE`: Respuesta exitosa
- `ERROR`: Error en procesamiento

**Tipos de tareas:**
- `SCREENSHOT`: Captura de screenshot
- `PERFORMANCE`: Análisis de rendimiento
- `IMAGES`: Procesamiento de imágenes
- `ALL`: Todas las tareas en paralelo

Ver [`docs/PROTOCOL.md`](docs/PROTOCOL.md) para detalles.

---


## Solución de problemas

### Error: "ChromeDriver not found"

```bash
# Verificar instalación
which chromedriver

# Si no está instalado
sudo apt-get install chromium-chromedriver

# Crear symlink si es necesario
sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
```

### Error: "Connection refused" al conectar con Servidor B

```bash
# Verificar que el Servidor B esté corriendo
ps aux | grep server_processing.py

# Verificar puerto
netstat -tuln | grep 9000

# Reiniciar Servidor B
python server_processing.py -i localhost -p 9000
```

### Error: "Address already in use"

```bash
# Encontrar proceso usando el puerto
sudo lsof -i :8000
sudo lsof -i :9000

# Matar proceso
kill -9 <PID>

# O usar otro puerto
python server_scraping.py -i localhost -p 8001
```

---

## 📂 Estructura del Proyecto

```
TP2/
├── server_scraping.py          # Servidor A (HTTP + Scraping)
├── server_processing.py        # Servidor B (TCP + Processing)
├── client.py                   # Cliente CLI
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── Enunciado.md                # COnsignas a cumplir del proyecto
│
├── common/                     # Módulos compartidos
│   ├── __init__.py
│   └── protocol.py            # Protocolo de comunicación
│
├── scraper/                    # Módulo de scraping
│   ├── __init__.py
│   ├── web_scraper.py         # Scraper HTTP asíncrono
│   └── html_parser.py         # Parser HTML
│
├── processor/                  # Módulo de procesamiento
│   ├── __init__.py
│   ├── screenshot.py          # Generador de screenshots
│   ├── performance.py         # Analizador de rendimiento
│   └── image_processor.py     # Procesador de imágenes
│
└── tests/                      # Tests
    ├── __init__.py
    ├── test_protocol.py
    ├── test_integration.py
    └── test_processors.py
```

---


## 👥 Autor

- **Estudiante**: Juan Cruz Rupcic
- **Materia**: Computación II (Ingeniería Informática)
- **Fecha**: Noviembre 2025
- **Materia**: Computación II
- **Fecha**: Noviembre 2025
---
