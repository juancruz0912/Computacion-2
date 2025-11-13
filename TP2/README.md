# 🌐 Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido de scraping web con procesamiento paralelo, rate limiting y análisis avanzados.

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-Arquitectura)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API Reference](#-api-reference)
- [Bonus Tracks Implementados](#-bonus-tracks-implementados)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Monitoreo](#-monitoreo)
- [Troubleshooting](#-troubleshooting)
- [Notas](#-notas)
- [Autor](#-autor)

---

## 🎯 Descripción

Sistema de scraping web distribuido que separa las responsabilidades de extracción (Servidor A) y procesamiento intensivo (Servidor B), utilizando comunicación TCP asíncrona y procesamiento paralelo con multiprocessing.

### Servidores

- **Servidor A (Scraping)**: Servidor HTTP asíncrono que realiza scraping básico de páginas web
- **Servidor B (Processing)**: Servidor TCP que procesa tareas pesadas usando pool de procesos

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│                    (curl, browser, etc)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR A (Scraping)                     │
│                   Port 8000 (HTTP/aiohttp)                   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Recibe requests HTTP                              │   │
│  │  • Rate Limiting (Redis)                             │   │
│  │  • Caché (Redis)                                     │   │
│  │  • Extrae HTML, links, imágenes, metadatos          │   │
│  │  • Delega procesamiento pesado al Servidor B        │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ TCP (Protocol binario)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SERVIDOR B (Processing)                     │
│                  Port 9000 (TCP/socketserver)                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pool de Procesos (multiprocessing.Pool)            │   │
│  │                                                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ Screenshot │  │Performance │  │  Images    │    │   │
│  │  │ (Selenium) │  │ (Selenium) │  │ (PIL/CV2)  │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  │                                                       │   │
│  │  ┌─────────────┐  ┌──────────┐                      │   │
│  │  │Technologies │  │   SEO    │                      │   │
│  │  │  Detector   │  │ Analyzer │                      │   │
│  │  └─────────────┘  └──────────┘                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │    Redis    │
                  │   Port 6379 │
                  └─────────────┘
```

---

## ✨ Características

### Scraping (Servidor A)
- ✅ Extracción de título, texto y estructura HTML
- ✅ Detección de links e imágenes
- ✅ Extracción de metadatos (SEO, Open Graph, Twitter Cards)
- ✅ Rate Limiting por dominio usando Redis
- ✅ Sistema de caché con TTL configurable
- ✅ Comunicación asíncrona con aiohttp

### Procesamiento (Servidor B)
- ✅ Screenshots con Selenium WebDriver
- ✅ Análisis de rendimiento (load time, recursos)
- ✅ Procesamiento de imágenes (descarga, thumbnails, dimensiones)
- ✅ Detección de tecnologías web (frameworks, CMS, librerías, analytics)
- ✅ Análisis completo de SEO con scoring
- ✅ Pool de procesos para paralelización
- ✅ Soporte para IPv4/IPv6

### Sistema
- ✅ Protocolo binario personalizado con JSON
- ✅ Manejo robusto de errores
- ✅ Logging detallado
- ✅ Tests automatizados

---

## 📦 Requisitos

### Software Base
- Python 3.8+
- Redis Server 7.0+
- Chrome/Chromium (para Selenium)
- ChromeDriver

### Dependencias Python
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
Pillow>=10.0.0
selenium>=4.15.0
redis>=7.0.0
```

---

## 🚀 Instalación

### 1. Clonar repositorio
```bash
git clone <repo>
cd TP2
```

### 2. Crear entorno virtual
```bash
python3 -m venv env
source env/bin/activate  # Linux/Mac
# env\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Iniciar Redis
redis-server
```

### 5. Instalar Chrome y ChromeDriver
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser chromium-chromedriver

# macOS
brew install --cask google-chrome
brew install chromedriver
```

---

## 💻 Uso

### Iniciar Servidores

#### Terminal 1: Redis (si no está en systemd)
```bash
redis-server
```

#### Terminal 2: Servidor B (Processing)
```bash
python server_processing.py -i localhost -p 9000
```

**Opciones:**
- `-i, --ip`: Dirección de escucha (default: localhost)
- `-p, --port`: Puerto TCP (default: 9000)
- `-n, --processes`: Número de procesos en el pool (default: CPU count)

#### Terminal 3: Servidor A (Scraping)
```bash
python server_scraping.py -i localhost -p 8000
```

**Opciones:**
- `-i, --ip`: Dirección de escucha (default: localhost)
- `-p, --port`: Puerto HTTP (default: 8000)
- `--processing-host`: IP del servidor B (default: localhost)
- `--processing-port`: Puerto del servidor B (default: 9000)
- `--redis-host`: IP de Redis (default: localhost)
- `--redis-port`: Puerto de Redis (default: 6379)
- `--no-cache`: Deshabilitar sistema de caché
- `--no-rate-limit`: Deshabilitar rate limiting
- `--max-requests`: Máximo requests/min por dominio (default: 10)
- `--cache-ttl`: TTL de caché en segundos (default: 3600)

### Ejemplos de Uso

#### 1. Scraping básico
```bash
curl "http://localhost:8000/scrape?url=https://example.com"
```

**Respuesta:**
```json
{
  "url": "https://example.com",
  "status": "success",
  "scraping_data": {
    "basic": {
      "title": "Example Domain",
      "text_preview": "...",
      "word_count": 21
    },
    "structure": {
      "headers": {"h1": 1, "h2": 0, ...},
      "elements_count": {...}
    },
    "links": [...],
    "images": [...],
    "metadata": {...}
  }
}
```

#### 2. Scraping completo (con procesamiento)
```bash
curl "http://localhost:8000/scrape?url=https://example.com&full=true"
```

**Respuesta incluye:**
- `scraping_data`: Datos básicos extraídos
- `processing_data`:
  - `screenshot`: Captura de pantalla
  - `performance`: Métricas de rendimiento
  - `images`: Imágenes procesadas
  - `technologies`: Tecnologías detectadas (frameworks, CMS, etc.)
  - `seo`: Análisis completo de SEO con score

#### 3. Health check
```bash
curl "http://localhost:8000/health"
```

#### 4. Estadísticas de caché
```bash
curl "http://localhost:8000/cache/stats"
```

**Respuesta:**
```json
{
  "cache_stats": {
    "hits": 15,
    "misses": 5,
    "writes": 5,
    "total_requests": 20,
    "hit_rate_percent": 75.0
  }
}
```

#### 5. Limpiar caché
```bash
curl -X POST "http://localhost:8000/cache/clear"
```

---

## 📚 API Reference

### Endpoints del Servidor A

#### `GET /health`
Health check del servidor.


**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T15:00:00.000000Z",
  "services": {
    "rate_limiter": "enabled",
    "cache": "enabled"
  },
  "cache_stats": {...}
}
```

#### `GET /scrape`
Realiza scraping de una URL.

**Parámetros:**
- `url` (required): URL a scrapear
- `full` (optional): `true` para procesamiento completo (default: `false`)

**Headers de respuesta:**
- `X-Cache`: `HIT` o `MISS`
- `X-Cache-TTL`: Segundos restantes de TTL (si es HIT)
- `X-RateLimit-Limit`: Límite de requests por ventana
- `X-RateLimit-Remaining`: Requests restantes

**Status codes:**
- `200`: Success
- `400`: Parámetros inválidos
- `429`: Rate limit excedido
- `500`: Error interno

#### `GET /cache/stats`
Obtiene estadísticas del sistema de caché.

#### `POST /cache/clear`
Limpia toda la caché.

---

## 🎁 Bonus Tracks Implementados

### ✅ Bonus Track 2: Rate Limiting y Caché con Redis

#### Rate Limiter
- **Implementación**: Ventana deslizante con Redis Sorted Sets
- **Granularidad**: Por dominio (evita bloquear todo el scraper)
- **Configurable**: Límite de requests y ventana de tiempo ajustables
- **Ubicación**: `common/rate_limiter.py`

**Características:**
```python
# Límite: 10 requests por minuto por dominio
# Ventana deslizante de 60 segundos
rate_limiter = RateLimiter(
    redis_host='localhost',
    redis_port=6379,
    max_requests=10,
    window_seconds=60
)

# Verificar si se puede procesar
allowed, info = rate_limiter.check_rate_limit(url)
```

**Response cuando se excede:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests to example.com",
  "rate_limit": {
    "limit": 10,
    "window_seconds": 60,
    "retry_after": 60
  }
}
```

#### Sistema de Caché
- **Implementación**: Redis con serialización JSON
- **TTL**: Configurable por entrada (default: 1 hora)
- **Keys hasheadas**: URLs largas se hashean con SHA-256
- **Caché separado**: Diferencia entre scraping básico y completo
- **Ubicación**: `common/cache.py`

**Características:**
```python
cache = RedisCache(
    redis_host='localhost',
    redis_port=6379,
    default_ttl=3600,  # 1 hora
    key_prefix='scraper'
)

# Guardar en caché
cache.set(url, data, full=True, ttl=3600)

# Obtener de caché
cached = cache.get(url, full=True)

# Estadísticas
stats = cache.get_stats()
# {
#   'hits': 150,
#   'misses': 50,
#   'writes': 50,
#   'hit_rate_percent': 75.0
# }
```

**Testing:**
```bash
# Test de Rate Limiter
python tests/test_rate_limiter.py

# Test de Caché
python tests/test_cache.py
```

---

### ✅ Bonus Track 3: Análisis Avanzados

#### 1. Detector de Tecnologías (`processor/technology_detector.py`)

Detecta automáticamente las tecnologías utilizadas en una página web.

**Categorías detectadas:**
- **Frameworks JS**: React, Vue.js, Angular, Next.js, Nuxt.js, Svelte, Ember.js
- **CMS**: WordPress, Drupal, Joomla, Shopify, Wix, Squarespace, Magento, PrestaShop
- **Librerías**: jQuery, Bootstrap, Tailwind CSS, Font Awesome, Lodash, Moment.js, Chart.js, Three.js
- **Analytics**: Google Analytics, Google Tag Manager, Facebook Pixel, Hotjar, Mixpanel, Segment
- **Servidores**: Nginx, Apache, Cloudflare, IIS, LiteSpeed, PHP, ASP.NET, Express.js

**Response:**
```json
{
  "technologies": {
    "frameworks": ["React", "Next.js"],
    "cms": ["WordPress"],
    "libraries": ["jQuery", "Bootstrap"],
    "analytics": ["Google Analytics"],
    "servers": ["Nginx", "PHP"],
    "meta": {
      "generator": "WordPress 6.4"
    },
    "summary": {
      "total_technologies": 6,
      "categories": {
        "frameworks": 2,
        "cms": 1,
        "libraries": 2,
        "analytics": 1,
        "servers": 2
      }
    }
  }
}
```

#### 2. Analizador de SEO (`processor/seo_analyzer.py`)

Análisis completo de SEO con scoring de 0-100 y grade A-F.

**Aspectos evaluados:**
- **Title Tag**: Existencia, longitud óptima (50-60 chars)
- **Meta Description**: Existencia, longitud óptima (150-160 chars)
- **Headers**: Jerarquía H1-H6, un único H1
- **Imágenes**: Alt tags presentes, cobertura
- **Links**: Balance interno/externo
- **Open Graph**: Tags para redes sociales
- **Structured Data**: JSON-LD, Schema.org
- **Canonical URL**: Prevención de contenido duplicado

**Response:**
```json
{
  "seo": {
    "score": 85,
    "grade": "B",
    "title": {
      "exists": true,
      "text": "Example Domain",
      "length": 14
    },
    "meta_description": {
      "exists": true,
      "text": "This domain is for use in illustrative examples...",
      "length": 145
    },
    "headers": {
      "h1_count": 1,
      "h1_texts": ["Example Domain"],
      "hierarchy": {
        "h1": 1,
        "h2": 3,
        "h3": 5
      }
    },
    "images": {
      "total_images": 10,
      "images_without_alt": 2,
      "alt_coverage_percent": 80.0
    },
    "links": {
      "total_links": 25,
      "internal_links": 18,
      "external_links": 7,
      "ratio": 0.72
    },
    "open_graph": {
      "exists": true,
      "tags": {
        "title": "Example",
        "description": "...",
        "image": "https://..."
      },
      "completeness_percent": 100.0
    },
    "structured_data": {
      "has_json_ld": true,
      "json_ld_count": 2,
      "types": ["Organization", "WebSite"]
    },
    "canonical": {
      "exists": true,
      "url": "https://example.com"
    },
    "issues": [
      "❌ 2 imágenes sin atributo alt"
    ],
    "warnings": [
      "⚠️  Title muy corto (14 chars). Recomendado: 50-60"
    ],
    "good_practices": [
      "✅ Un único H1 correctamente definido",
      "✅ Meta description con longitud óptima",
      "✅ Open Graph tags completos"
    ],
    "summary": {
      "total_issues": 1,
      "total_warnings": 1,
      "total_good_practices": 3
    }
  }
}
```

**Scoring:**
- `90-100`: Grade A (Excelente)
- `75-89`: Grade B (Bueno)
- `60-74`: Grade C (Aceptable)
- `45-59`: Grade D (Necesita mejoras)
- `0-44`: Grade F (Crítico)


---

## 📁 Estructura del Proyecto

```
TP2/
├── server_scraping.py          # Servidor A (HTTP/Scraping)
├── server_processing.py        # Servidor B (TCP/Processing)
├── requirements.txt
├── README.md
│
├── common/                     # Módulos compartidos
│   ├── __init__.py
│   ├── protocol.py            # Protocolo de comunicación
│   ├── rate_limiter.py        # ⭐ Rate limiting con Redis
│   └── cache.py               # ⭐ Sistema de caché con Redis
│
├── scraper/                    # Módulo de scraping
│   ├── __init__.py
│   └── html_parser.py         # Parser HTML con BeautifulSoup
│
├── processor/                  # Módulo de procesamiento
│   ├── __init__.py
│   ├── screenshot.py          # Generador de screenshots
│   ├── performance.py         # Analizador de rendimiento
│   ├── image_processor.py     # Procesador de imágenes
│   ├── technology_detector.py # ⭐ Detector de tecnologías
│   └── seo_analyzer.py        # ⭐ Analizador de SEO
│
└── tests/                      # Tests
    ├── test_protocol.py
    ├── test_server.py
    ├── test_rate_limiter.py   # ⭐ Tests de rate limiting
    └── test_cache.py          # ⭐ Tests de caché
```

---

## 🔧 Configuración Avanzada

### Rate Limiting Personalizado

```bash
# 5 requests por minuto
python server_scraping.py --max-requests 5

# Ventana de 30 segundos (ajustar en código)
```

### Caché Personalizado

```bash
# TTL de 30 minutos (1800 segundos)
python server_scraping.py --cache-ttl 1800

# Deshabilitar caché
python server_scraping.py --no-cache
```

### Pool de Procesos

```bash
# 8 procesos en el pool
python server_processing.py -n 8

# Usar todos los CPUs disponibles (default)
python server_processing.py
```

---

## 📊 Monitoreo

### Estadísticas en tiempo real

```bash
# Watch de estadísticas de caché
watch -n 1 'curl -s http://localhost:8000/cache/stats | python -m json.tool'

# Logs del servidor
tail -f server_scraping.log
tail -f server_processing.log
```

### Redis CLI

```bash
# Conectar a Redis
redis-cli

# Ver keys de rate limiting
KEYS rate:*

# Ver keys de caché
KEYS scraper:*

# Ver estadísticas
INFO stats
```

---

## 🐛 Troubleshooting

### Redis no conecta
```bash
# Verificar que Redis esté corriendo
redis-cli ping
# Debe responder: PONG

# Iniciar Redis
redis-server
```


### Caché no funciona
```bash
# Verificar conexión a Redis
curl http://localhost:8000/health

# Limpiar caché corrupta
curl -X POST http://localhost:8000/cache/clear
```

---

## 📝 Notas

- El rate limiting es por **dominio**, no por URL completa
- El caché diferencia entre scraping básico (`full=false`) y completo (`full=true`)
- Los análisis avanzados (tecnologías y SEO) **solo se ejecutan con `full=true`**
- Redis debe estar corriendo para rate limiting y caché
- El servidor B puede correr en máquina separada ajustando `--processing-host`

---

## 👥 Autor

- **Estudiante**: Juan Cruz Rupcic
- **Materia**: Computación II (Ingeniería Informática)
- **Fecha**: Noviembre 2025
---
