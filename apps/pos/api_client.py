import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"  # cambia a tu dominio en producción


class POSAPIClient:
    def __init__(self, token=None):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Token {token}"})

    def login(self, username, password):
        url = f"{self.base_url}/token/"
        response = self.session.post(url, data={"username": username, "password": password})

        # Línea de depuración — imprime código de estado y texto de respuesta
        print("DEBUG API LOGIN:", response.status_code, response.text)

        if response.status_code == 200:
            token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Token {token}"})
            return token
        return None


    def get_vinos(self):
        url = f"{self.base_url}/vinos/"
        response = self.session.get(url)
        return response.json() if response.status_code == 200 else []

    def registrar_venta(self, detalles):
        """
        detalles = [
            {"vino": 1, "cantidad": 2, "precio_unitario": 12.50, "subtotal": 25.00},
            ...
        ]
        """
        url = f"{self.base_url}/ventas/"
        data = {"detalles": detalles, "total": sum(d["subtotal"] for d in detalles), "pagado": True}
        response = self.session.post(url, json=data)
        return response.json() if response.status_code in (200, 201) else response.text
