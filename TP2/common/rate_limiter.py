"""
Rate Limiter usando Redis con algoritmo de ventana deslizante
"""
import redis
import time
import logging
from urllib.parse import urlparse
from typing import Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter por dominio usando Redis
    
    Algoritmo: Sliding Window
    - Almacena timestamps de requests en una sorted set
    - Remueve timestamps antiguos
    - Cuenta requests en la ventana de tiempo
    """
    
    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        max_requests: int = 10,
        window_seconds: int = 60
    ):
        """
        Args:
            redis_host: Host de Redis
            redis_port: Puerto de Redis
            max_requests: Máximo de requests por ventana
            window_seconds: Tamaño de la ventana en segundos
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Verificar conexión
        try:
            self.redis_client.ping()
            logger.info(f"✅ Rate Limiter conectado a Redis ({redis_host}:{redis_port})")
        except redis.ConnectionError:
            logger.error(f"❌ No se pudo conectar a Redis ({redis_host}:{redis_port})")
            raise
    
    def _get_domain(self, url: str) -> str:
        """Extrae el dominio de una URL"""
        parsed = urlparse(url)
        return parsed.netloc or parsed.path
    
    def _get_key(self, domain: str) -> str:
        """Genera la clave de Redis para el dominio"""
        return f"rate_limit:{domain}"
    
    def check_rate_limit(self, url: str) -> Tuple[bool, dict]:
        """
        Verifica si la URL puede ser procesada según el rate limit
        
        Args:
            url: URL a verificar
        
        Returns:
            Tuple de (allowed: bool, info: dict)
        """
        domain = self._get_domain(url)
        key = self._get_key(domain)
        now = time.time()
        window_start = now - self.window_seconds
        
        # Pipeline para operaciones atómicas
        pipe = self.redis_client.pipeline()
        
        # 1. Remover timestamps antiguos (fuera de la ventana)
        pipe.zremrangebyscore(key, 0, window_start)
        
        # 2. Contar requests en la ventana actual
        pipe.zcard(key)
        
        # Ejecutar pipeline hasta aquí
        results = pipe.execute()
        request_count = results[1]  # Resultado del ZCARD
        
        # ✅ VERIFICAR LÍMITE ANTES DE AGREGAR
        allowed = request_count < self.max_requests
        
        # ✅ SOLO AGREGAR SI ESTÁ PERMITIDO
        if allowed:
            pipe = self.redis_client.pipeline()
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window_seconds)
            pipe.execute()
        
        info = {
            'domain': domain,
            'requests_in_window': request_count,
            'max_requests': self.max_requests,
            'window_seconds': self.window_seconds,
            'allowed': allowed,
            'remaining': max(0, self.max_requests - request_count)
        }
        
        if not allowed:
            logger.warning(
                f"⚠️  Rate limit excedido para {domain}: "
                f"{request_count}/{self.max_requests} requests en {self.window_seconds}s"
            )
        else:
            logger.debug(
                f"✅ Rate limit OK para {domain}: "
                f"{request_count + 1}/{self.max_requests} requests"
            )
        
        return allowed, info
    
    def reset_domain(self, url: str) -> bool:
        """
        Resetea el rate limit para un dominio (útil para testing)
        
        Args:
            url: URL del dominio a resetear
        
        Returns:
            True si se reseteó exitosamente
        """
        domain = self._get_domain(url)
        key = self._get_key(domain)
        
        deleted = self.redis_client.delete(key)
        
        if deleted:
            logger.info(f"🔄 Rate limit reseteado para {domain}")
        
        return bool(deleted)
    
    def get_stats(self, url: str) -> dict:
        """
        Obtiene estadísticas del rate limit para un dominio
        
        Args:
            url: URL del dominio
        
        Returns:
            Diccionario con estadísticas
        """
        domain = self._get_domain(url)
        key = self._get_key(domain)
        now = time.time()
        window_start = now - self.window_seconds
        
        # Limpiar timestamps antiguos
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Obtener todos los timestamps en la ventana
        timestamps = self.redis_client.zrange(key, 0, -1, withscores=True)
        
        request_count = len(timestamps)
        allowed = request_count < self.max_requests
        
        return {
            'domain': domain,
            'request_count': request_count,
            'max_requests': self.max_requests,
            'window_seconds': self.window_seconds,
            'allowed': allowed,
            'remaining': max(0, self.max_requests - request_count),
            'oldest_request': timestamps[0][1] if timestamps else None,
            'newest_request': timestamps[-1][1] if timestamps else None
        }
    
    def close(self):
        """Cierra la conexión a Redis"""
        self.redis_client.close()
        logger.info("🔌 Conexión a Redis cerrada")


# Instancia global (se inicializa en el servidor)
rate_limiter = None


def init_rate_limiter(
    redis_host: str = 'localhost',
    redis_port: int = 6379,
    max_requests: int = 10,
    window_seconds: int = 60
) -> RateLimiter:
    """
    Inicializa el rate limiter global
    
    Args:
        redis_host: Host de Redis
        redis_port: Puerto de Redis
        max_requests: Máximo de requests por ventana
        window_seconds: Tamaño de la ventana en segundos
    
    Returns:
        Instancia de RateLimiter
    """
    global rate_limiter
    
    rate_limiter = RateLimiter(
        redis_host=redis_host,
        redis_port=redis_port,
        max_requests=max_requests,
        window_seconds=window_seconds
    )
    
    return rate_limiter


def get_rate_limiter() -> RateLimiter:
    """
    Obtiene el rate limiter global
    
    Returns:
        Instancia de RateLimiter
    
    Raises:
        RuntimeError: Si el rate limiter no fue inicializado
    """
    if rate_limiter is None:
        raise RuntimeError(
            "Rate limiter no inicializado. "
            "Llama a init_rate_limiter() primero"
        )
    
    return rate_limiter