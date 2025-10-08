# Vinoteca POS

Sistema Django con API REST y punto de venta sincronizado.
- Backend: Django + DRF + PostgreSQL
- Apps: inventario, ventas, api, usuarios, core, pos
- Autenticación: Token DRF (empleados)
- Sincronización de stock automática

## Ejecución local
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
