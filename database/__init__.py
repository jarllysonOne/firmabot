import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Aviso:
    nome: str
    mensagem: str
    tipo: str = "aviso"
    participantes: list = None
    
    def __post_init__(self):
        if self.participantes is None:
            self.participantes = []


@dataclass
class Evento:
    nome: str
    mensagem: str
    data: Optional[str] = None
    hora: Optional[str] = None
    ativo: bool = True
    participantes: list = None
    confirmados: list = None
    recusados: list = None
    lembrete_minutos: int = 15
    tipo: str = "normal"
    recorrencia: Optional[str] = None
    limite_participantes: Optional[int] = None
    lista_espera: list = None
    arquivado: bool = False
    
    def __post_init__(self):
        if self.participantes is None:
            self.participantes = []
        if self.confirmados is None:
            self.confirmados = []
        if self.recusados is None:
            self.recusados = []
        if self.lista_espera is None:
            self.lista_espera = []


class Database:
    _instance = None
    _avisos: Dict[str, Aviso] = {}
    _eventos: Dict[str, Evento] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _get_data_path(self, name: str) -> str:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "data", f"{name}.json")

    def _load(self):
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"), exist_ok=True)

        for tipo, colecao in [("avisos", self._avisos), ("eventos", self._eventos)]:
            path = self._get_data_path(tipo)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if tipo == "avisos":
                            colecao[k] = Aviso(**v)
                        else:
                            colecao[k] = Evento(**v)

    def _save(self, tipo: str):
        path = self._get_data_path(tipo)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._get_collection(tipo), f, ensure_ascii=False, indent=2, default=str)

    def _get_collection(self, tipo: str) -> Dict[str, Any]:
        if tipo == "avisos":
            return {k: asdict(v) for k, v in self._avisos.items()}
        return {k: asdict(v) for k, v in self._eventos.items()}

    def add_aviso(self, nome: str, mensagem: str, participantes: list = None) -> bool:
        if nome in self._avisos:
            return False
        self._avisos[nome] = Aviso(nome=nome, mensagem=mensagem, participantes=participantes or [])
        self._save("avisos")
        return True

    def get_aviso(self, nome: str) -> Optional[Aviso]:
        return self._avisos.get(nome)

    def list_avisos(self) -> Dict[str, Aviso]:
        return self._avisos.copy()

    def delete_aviso(self, nome: str) -> bool:
        if nome in self._avisos:
            del self._avisos[nome]
            self._save("avisos")
            return True
        return False

    def add_evento(self, nome: str, mensagem: str, data: str = None, hora: str = None, participantes: list = None, lembrete_minutos: int = 15) -> bool:
        if nome in self._eventos:
            return False
        self._eventos[nome] = Evento(nome=nome, mensagem=mensagem, data=data, hora=hora, participantes=participantes or [], lembrete_minutos=lembrete_minutos)
        self._save("eventos")
        return True

    def get_evento(self, nome: str) -> Optional[Evento]:
        return self._eventos.get(nome)

    def list_eventos(self) -> Dict[str, Evento]:
        return self._eventos.copy()

    def update_evento(self, nome: str, **kwargs) -> bool:
        if nome in self._eventos:
            evento = self._eventos[nome]
            for key, value in kwargs.items():
                if hasattr(evento, key):
                    setattr(evento, key, value)
            self._save("eventos")
            return True
        return False

    def delete_evento(self, nome: str) -> bool:
        if nome in self._eventos:
            del self._eventos[nome]
            self._save("eventos")
            return True
        return False

    def get_eventos_ativos(self) -> Dict[str, Evento]:
        return {k: v for k, v in self._eventos.items() if v.ativo}

    def confirmar_participacao(self, nome: str, user_id: str) -> bool:
        if nome in self._eventos:
            evento = self._eventos[nome]
            if user_id not in evento.confirmados:
                evento.confirmados.append(user_id)
                if user_id in evento.recusados:
                    evento.recusados.remove(user_id)
            self._save("eventos")
            return True
        return False

    def recusar_participacao(self, nome: str, user_id: str) -> bool:
        if nome in self._eventos:
            evento = self._eventos[nome]
            if user_id not in evento.recusados:
                evento.recusados.append(user_id)
                if user_id in evento.confirmados:
                    evento.confirmados.remove(user_id)
            self._save("eventos")
            return True
        return False


db = Database()