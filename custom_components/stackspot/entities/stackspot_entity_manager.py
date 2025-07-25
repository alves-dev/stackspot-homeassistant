import logging
from typing import Optional, Dict

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


class StackSpotEntityManager:
    _instance: Optional["StackSpotEntityManager"] = None
    _entities: Dict[str, Dict[str, Entity]] = {}

    def __new__(cls):
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(StackSpotEntityManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

    @classmethod
    def instance(cls) -> "StackSpotEntityManager":
        """Retorna a única instância do gerenciador de entidades."""
        return cls()

    def add_entity(self, entry_id: str, key: str, entity: Entity) -> None:
        """
        Adiciona uma entidade ao gerenciador, vinculando-a a uma ConfigEntry e uma chave.
        """
        self._add_entry_container(entry_id)
        self._entities[entry_id][key] = entity
        _LOGGER.debug(f"Entity '{key}' added for entry_id: {entry_id}")

    def get_entity_by(self, entry_id: str, key: str) -> Optional[Entity]:
        """
        Recupera uma entidade a partir da config_id (entry_id) e da key.
        """
        if entry_id in self._entities and key in self._entities[entry_id]:
            return self._entities[entry_id][key]
        _LOGGER.warning(f"Entity '{key}' not found for entry_id: {entry_id}")
        return None

    def remove_entry(self, entry_id: str) -> None:
        """
        Remove todas as entidades associadas a uma ConfigEntry específica.
        Chamado durante async_unload_entry.
        """
        if entry_id in self._entities:
            del self._entities[entry_id]
            _LOGGER.debug(f"All entities for entry_id: {entry_id} removed.")
        else:
            _LOGGER.debug(f"No entities found to remove for entry_id: {entry_id}.")

    def _add_entry_container(self, entry_id: str) -> None:
        """
        Adiciona um container para uma nova ConfigEntry, se ainda não existir.
        Chamado quando uma ConfigEntry (principal ou sub-entrada) é configurada.
        """
        if entry_id not in self._entities:
            self._entities[entry_id] = {}
            _LOGGER.debug(f"Container added for entry_id: {entry_id}")
