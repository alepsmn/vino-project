# apps/pos/api_client.py

import requests
from requests.adapters import HTTPAdapter, Retry
from decimal import Decimal

API_BASE_URL = "http://127.0.0.1:8000/api/v1"


class POSAPIClient:
    """
    Cliente robusto para comunicación con la API del backend.
    Maneja:
    - Login vía token
    - Reintentos automáticos
    - Sesión persistente
    - Métodos explícitos: login, get, post
    """

    def __init__(self, token=None):
        self.base_url = API_BASE_URL
        self.session = requests.Session()

        # Reintentos automáticos frente a fallos
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        if token:
            self.set_token(token)

    # -------------------------
    # AUTENTICACIÓN
    # -------------------------
    def set_token(self, token):
        self.session.headers.update({"Authorization": f"Token {token}"})

    def login(self, username, password):
        url = f"{self.base_url}/token/"
        r = self.session.post(url, data={"username": username, "password": password})

        if r.status_code != 200:
            return None

        token = r.json().get("token")
        if not token:
            return None

        self.set_token(token)
        return token

    # -------------------------
    # MÉTODOS GENÉRICOS
    # -------------------------
    def get(self, path, params=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.get(url, params=params)

    def post(self, path, data=None, json=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.post(url, data=data, json=json)

    # -------------------------
    # MÉTODOS EXPLÍCITOS PARA POS
    # -------------------------
    def obtener_stock(self):
        """
        Paginación completa de /stock/.
        Devuelve una lista de objetos stock completos.
        """
        resultados = []
        url = f"{self.base_url}/stock/"

        while url:
            r = self.session.get(url)
            if r.status_code != 200:
                break

            data = r.json()
            for item in data.get("results", []):
                resultados.append(item)

            url = data.get("next")

        return resultados

    def registrar_venta(self, detalles, metodo_pago="POS", descuento=0):
        """
        Enviar venta a la API unificada.
        El cálculo interno del total lo hace la API.
        """
        payload = {
            "detalles": detalles,
            "metodo_pago": metodo_pago,
            "descuento": float(Decimal(descuento)),
        }

        r = self.post("ventas/", json=payload)
        return r
