# agendarte

Proyecto generado con [tai-sql](https://github.com/triplealpha-innovation/tai-sql).

## Setup

```bash
cd agendarte
poetry install
```

## Crear o recuperar un usuario desde el cliente

Arranca tai-api e instala las dependencias con `poetry install`. Después ejecuta
el script desde este directorio:

```bash
python cliente.py
```

El cliente usa los endpoints HTTP de tai-api y solo requiere la biblioteca estándar
de Python. Puedes configurar la URL (incluido un posible prefijo) y el token Bearer:

```bash
export TAI_API_URL="http://127.0.0.1:8000"
export TAI_API_TOKEN="..."
python cliente.py
```

Si `TAI_API_TOKEN` no está definido, el script lo solicita sin mostrarlo. Déjalo
vacío cuando ejecutes tai-api con `tai-api dev` y la autorización desactivada.
El script pregunta si quieres crear un usuario (`c`) o buscarlo por email (`r`).
