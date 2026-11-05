# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
import os
import re
from urllib.parse import (
    unquote,
    urlparse,
    parse_qs
)
from typing import (
    Optional,
    Generator,
    AsyncGenerator
)
from contextlib import (
    contextmanager,
    asynccontextmanager
)
from sqlalchemy import (
    create_engine,
    Engine,
    URL
)
from sqlalchemy.orm import (
    sessionmaker,
    Session
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from tai_alphi import Alphi

# Logger
logger = Alphi.get_logger_by_name("tai-sql")


class _BaseSessionManager:
    """Funcionalidad compartida para gestores de sesiones."""

    _docker_env: Optional[bool] = None

    @property
    def docker_env(self) -> bool:
        """Indica si la aplicación se está ejecutando dentro de un contenedor Docker."""
        if self._docker_env is None:
            self._docker_env = False
            if os.path.exists("/.dockerenv"):
                self._docker_env = True
            else:
                try:
                    with open("/proc/1/cgroup", "r") as f:
                        cgroup = f.read()
                        if "docker" in cgroup or "containerd" in cgroup:
                            self._docker_env = True
                except FileNotFoundError:
                    pass
        return self._docker_env

    def parse_localhost(self, host: Optional[str]) -> Optional[str]:
        """Ajusta el host si se está ejecutando en Docker."""
        if self.docker_env and host in ['localhost', '127.0.0.1']:
            return 'host.docker.internal'
        return host

    def _build_url(self, connection_string: str, async_mode: bool = False) -> URL:
        """
        Crea una URL desde un string de conexión.
        
        Args:
            connection_string: String de conexión completo
            async_mode: Si True, transforma el driver a su versión asíncrona
        """
        try:
            connection_string = connection_string.strip()
            if '://' not in connection_string:
                raise ValueError("String de conexión debe tener formato: driver://user:pass@host:port/db")
            
            parse = urlparse(connection_string)
            if not parse.scheme:
                raise ValueError("Driver no especificado en el string de conexión")
            if not parse.hostname:
                raise ValueError("Host no especificado en el string de conexión")
            
            driver = parse.scheme
            # El motor es la parte de delante del `+`; la de detrás es el DBAPI.
            # `postgresql` y `postgresql+psycopg2` son el mismo motor, y en modo async el
            # DBAPI **hay que** sustituirlo: un motor asíncrono sobre psycopg2 falla con
            # "asyncio extension requires an async driver".
            backend = driver.split('+')[0]
            if async_mode:
                async_drivers = {
                    'postgresql': 'postgresql+asyncpg',
                    'mysql': 'mysql+aiomysql',
                    'mssql': 'mssql+aioodbc',
                }
                driver = async_drivers.get(backend, driver)
            
            database = parse.path[1:] if parse.path and len(parse.path) > 1 else None
            port = parse.port
            if port is None:
                default_ports = {
                    'postgresql': 5432, 'mysql': 3306,
                    'sqlite': None, 'mssql': 1433, 'oracle': 1521
                }
                port = default_ports.get(backend, None)
            
            query_params = {}
            if parse.query:
                try:
                    query_params = parse_qs(parse.query)
                    query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
                except Exception:
                    query_params = {}
            
            try:
                return URL.create(
                    drivername=driver,
                    username=parse.username,
                    password=parse.password,
                    host=self.parse_localhost(parse.hostname),
                    port=port,
                    database=database,
                    query=query_params
                )
            except Exception:
                return self._build_url_escaped(connection_string, async_mode)
            
        except Exception:
            return self._build_url_escaped(connection_string, async_mode)

    def _build_url_escaped(self, connection_string: str, async_mode: bool = False) -> URL:
        """Versión alternativa que maneja manualmente el escaping de caracteres especiales."""
        try:
            # La contraseña es **greedy hasta la última `@`**: es justo para lo que existe este
            # parser. Con `[^@]+` no podía contener una `@`, así que sobre
            # `usuario:c!av3@#$@localhost` el host salía `#$@localhost` — y este camino
            # solo se recorre cuando `urlparse` ya falló, que es lo que pasa con una
            # contraseña con caracteres especiales.
            pattern = r'^([^:]+)://([^:]+):(.+)@([^:/]+)(?::(\d+))?(?:/(.*))?$'
            match = re.match(pattern, connection_string.strip())
            if not match:
                raise ValueError(
                    "Formato de connection string no válido.\n"
                    "Esperado: driver://username:password@host:port/database"
                )
            
            driver, username, password, host, port, database_and_query = match.groups()
            
            if async_mode:
                async_drivers = {
                    'postgresql': 'postgresql+asyncpg',
                    'mysql': 'mysql+aiomysql',
                    'mssql': 'mssql+aioodbc',
                }
                driver = async_drivers.get(driver.split('+')[0], driver)
            
            database = None
            query_params = {}
            if database_and_query:
                if '?' in database_and_query:
                    database, query_string = database_and_query.split('?', 1)
                    for param in query_string.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            query_params[unquote(key)] = unquote(value)
                else:
                    database = database_and_query
            
            if port:
                try:
                    port = int(port)
                except ValueError:
                    raise ValueError(f"Puerto inválido: {port}")
            else:
                default_ports = {
                    'postgresql': 5432, 'mysql': 3306,
                    'sqlite': None, 'mssql': 1433, 'oracle': 1521
                }
                port = default_ports.get(driver.split('+')[0], None)
            
            return URL.create(
                drivername=driver,
                username=unquote(username) if username else None,
                password=unquote(password) if password else None,
                host=self.parse_localhost(unquote(host)) if host else None,
                port=port,
                database=unquote(database) if database else None,
                query=query_params
            )
        except Exception as e:
            raise ValueError(f"Error en parsing manual: {e}")


class SyncSessionManager(_BaseSessionManager):
    """
    Gestor de sesiones síncronas para SQLAlchemy.

    Configuración del Engine:
        - Pool size: 5 conexiones
        - Max overflow: 5 conexiones adicionales
        - Pool timeout: 30 segundos
        - Pool recycle: 3600 segundos
        - Pre-ping True para detectar conexiones perdidas
    """
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None

    @property
    def engine(self) -> Engine:
        if not self._engine:
            connection_string = os.getenv('MAIN_DATABASE_URL')
            if not connection_string:
                raise ValueError('Variable de entorno "MAIN_DATABASE_URL" no encontrada')
            url = self._build_url(connection_string, async_mode=False)
            engine_kwargs = {
                'echo': False,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'pool_size': 5,
                'max_overflow': 5,
                'pool_timeout': 30
            }
            self._engine = create_engine(url, **engine_kwargs)
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        if not self._session_factory:
            self._session_factory = sessionmaker(
                bind=self.engine, autoflush=False, autocommit=False
            )
        return self._session_factory
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager para obtener una sesión síncrona."""
        session: Session = self.session_factory()
        try:
            if not session.in_transaction():
                session.begin()
            yield session
            if session.in_transaction():
                session.commit()
                for msg in session.info.pop('_log_buffer', []):
                    logger.info(msg)
        except Exception as e:
            if session.in_transaction():
                session.rollback()
            raise e
        finally:
            session.close()


class AsyncSessionManager(_BaseSessionManager):
    """
    Gestor de sesiones asíncronas para SQLAlchemy.

    Configuración del Engine:
        - Pool size: 5 conexiones
        - Max overflow: 5 conexiones adicionales
        - Pool timeout: 30 segundos
        - Pool recycle: 3600 segundos
        - Pre-ping True para detectar conexiones perdidas
    """

    _async_driver_mapping = {
        'postgresql': 'postgresql+asyncpg',
        'mysql': 'mysql+aiomysql',
        'mssql': 'mssql+aioodbc',
    }
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            connection_string = os.getenv('MAIN_DATABASE_URL')
            if not connection_string:
                raise ValueError('Variable de entorno "MAIN_DATABASE_URL" no encontrada')
            url = self._build_url(connection_string, async_mode=True)
            engine_kwargs = {
                'echo': False,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'pool_size': 5,
                'max_overflow': 5,
                'pool_timeout': 30,
            }
            self._engine = create_async_engine(url, **engine_kwargs)
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker:
        if not self._session_factory:
            self._session_factory = async_sessionmaker(
                bind=self.engine, autoflush=False, autocommit=False
            )
        return self._session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None, None]:
        """Context manager para obtener una sesión asíncrona."""
        session: AsyncSession = self.session_factory()
        try:
            if not session.in_transaction():
                await session.begin()
            yield session
            if session.in_transaction():
                await session.commit()
                for msg in session.info.pop('_log_buffer', []):
                    logger.info(msg)
        except Exception as e:
            if session.in_transaction():
                await session.rollback()
            raise e
        finally:
            await session.close()


# Instancias a nivel de módulo (usadas por los DAOs via import)
sync_session_manager = SyncSessionManager()
async_session_manager = AsyncSessionManager()