"""
Sistema de caché usando Redis con TTL automático
"""
import redis
import json
import hashlib
import logging
from typing import Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Sistema de caché usando Redis
    
    Features:
    - TTL automático por entrada
    - Serialización JSON
    - Keys hasheadas para URLs largas
    - Estadísticas de cache hits/misses
    """
    
    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        default_ttl: int = 3600,  # 1 hora
        key_prefix: str = 'scraper'
    ):
        """
        Args:
            redis_host: Host de Redis
            redis_port: Puerto de Redis
            default_ttl: TTL por defecto en segundos
            key_prefix: Prefijo para las keys en Redis
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        
        # Estadísticas
        self.stats_key = f"{key_prefix}:stats"
        
        # Verificar conexión
        try:
            self.redis_client.ping()
            logger.info(f"✅ Caché conectado a Redis ({redis_host}:{redis_port})")
        except redis.ConnectionError:
            logger.error(f"❌ No se pudo conectar a Redis ({redis_host}:{redis_port})")
            raise
    
    def _generate_key(self, url: str, full: bool = False) -> str:
        """
        Genera una clave única para la URL
        
        Args:
            url: URL a cachear
            full: Si es scraping completo (con procesamiento)
        
        Returns:
            Clave de Redis
        """
        # Hash MD5 de la URL (para URLs largas)
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Tipo de scraping
        scrape_type = 'full' if full else 'basic'
        
        return f"{self.key_prefix}:cache:{scrape_type}:{url_hash}"
    
    def get(self, url: str, full: bool = False) -> Optional[dict]:
        """
        Obtiene datos cacheados para una URL
        
        Args:
            url: URL a buscar
            full: Si es scraping completo
        
        Returns:
            Datos cacheados o None si no existe
        """
        key = self._generate_key(url, full)
        
        try:
            data = self.redis_client.get(key)
            
            if data:
                # Cache HIT
                self._increment_stat('hits')
                
                result = json.loads(data)
                
                # Agregar metadata de caché
                result['cache'] = {
                    'hit': True,
                    'cached_at': result.get('timestamp'),
                    'ttl_seconds': self.redis_client.ttl(key)
                }
                
                logger.info(f"✅ Cache HIT para {url} (TTL: {result['cache']['ttl_seconds']}s)")
                
                return result
            else:
                # Cache MISS
                self._increment_stat('misses')
                logger.debug(f"❌ Cache MISS para {url}")
                return None
        
        except json.JSONDecodeError:
            logger.error(f"⚠️  Error decodificando JSON para {url}")
            self.delete(url, full)
            return None
        
        except Exception as e:
            logger.error(f"⚠️  Error obteniendo caché para {url}: {e}")
            return None
    
    def set(
        self,
        url: str,
        data: dict,
        full: bool = False,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Guarda datos en caché para una URL
        
        Args:
            url: URL a cachear
            data: Datos a guardar
            full: Si es scraping completo
            ttl: TTL custom en segundos (None = default)
        
        Returns:
            True si se guardó exitosamente
        """
        key = self._generate_key(url, full)
        ttl = ttl or self.default_ttl
        
        try:
            # Agregar timestamp si no existe
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            # Serializar a JSON
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Guardar con TTL
            success = self.redis_client.setex(
                key,
                ttl,
                json_data
            )
            
            if success:
                logger.info(f"💾 Datos cacheados para {url} (TTL: {ttl}s)")
                self._increment_stat('writes')
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"⚠️  Error guardando caché para {url}: {e}")
            return False
    
    def delete(self, url: str, full: bool = False) -> bool:
        """
        Elimina entrada de caché para una URL
        
        Args:
            url: URL a eliminar
            full: Si es scraping completo
        
        Returns:
            True si se eliminó exitosamente
        """
        key = self._generate_key(url, full)
        
        deleted = self.redis_client.delete(key)
        
        if deleted:
            logger.info(f"🗑️  Caché eliminado para {url}")
        
        return bool(deleted)
    
    def exists(self, url: str, full: bool = False) -> bool:
        """
        Verifica si existe caché para una URL
        
        Args:
            url: URL a verificar
            full: Si es scraping completo
        
        Returns:
            True si existe en caché
        """
        key = self._generate_key(url, full)
        return bool(self.redis_client.exists(key))
    
    def get_ttl(self, url: str, full: bool = False) -> int:
        """
        Obtiene el TTL restante para una URL cacheada
        
        Args:
            url: URL a consultar
            full: Si es scraping completo
        
        Returns:
            TTL en segundos, -1 si no existe, -2 si no tiene TTL
        """
        key = self._generate_key(url, full)
        return self.redis_client.ttl(key)
    
    def _increment_stat(self, stat_type: str):
        """Incrementa contador de estadísticas"""
        try:
            self.redis_client.hincrby(self.stats_key, stat_type, 1)
        except:
            pass
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de caché
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            stats = self.redis_client.hgetall(self.stats_key)
            
            hits = int(stats.get('hits', 0))
            misses = int(stats.get('misses', 0))
            writes = int(stats.get('writes', 0))
            total = hits + misses
            
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                'hits': hits,
                'misses': misses,
                'writes': writes,
                'total_requests': total,
                'hit_rate_percent': round(hit_rate, 2)
            }
        
        except Exception as e:
            logger.error(f"⚠️  Error obteniendo estadísticas: {e}")
            return {}
    
    def clear_all(self) -> int:
        """
        Elimina todas las entradas de caché
        
        Returns:
            Número de keys eliminadas
        """
        pattern = f"{self.key_prefix}:cache:*"
        keys = self.redis_client.keys(pattern)
        
        if keys:
            deleted = self.redis_client.delete(*keys)
            logger.warning(f"🗑️  Caché limpiado: {deleted} entradas eliminadas")
            return deleted
        
        return 0
    
    def close(self):
        """Cierra la conexión a Redis"""
        self.redis_client.close()
        logger.info("🔌 Conexión a Redis cerrada")


# Instancia global (se inicializa en el servidor)
cache = None


def init_cache(
    redis_host: str = 'localhost',
    redis_port: int = 6379,
    default_ttl: int = 3600
) -> RedisCache:
    """
    Inicializa el sistema de caché global
    
    Args:
        redis_host: Host de Redis
        redis_port: Puerto de Redis
        default_ttl: TTL por defecto en segundos
    
    Returns:
        Instancia de RedisCache
    """
    global cache
    
    cache = RedisCache(
        redis_host=redis_host,
        redis_port=redis_port,
        default_ttl=default_ttl
    )
    
    return cache


def get_cache() -> RedisCache:
    """
    Obtiene el sistema de caché global
    
    Returns:
        Instancia de RedisCache
    
    Raises:
        RuntimeError: Si el caché no fue inicializado
    """
    if cache is None:
        raise RuntimeError(
            "Caché no inicializado. "
            "Llama a init_cache() primero"
        )
    
    return cache