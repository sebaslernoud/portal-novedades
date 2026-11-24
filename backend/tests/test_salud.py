"""GET /api/salud contra la base configurada en DATABASE_URL (la de Docker, ya migrada)."""


def test_salud_informa_base_y_migracion(cliente):
    respuesta = cliente.get("/api/salud")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok", "base_de_datos": "ok", "migracion": "0001"}
