"""Parseo de DATABASE_URL y del almacenamiento S3.

Un DATABASE_URL sin su query string no es el mismo DATABASE_URL: Neon entrega
sslmode=require y channel_binding=require, y perderlos degrada la conexion.
"""

from config.settings import parse_database_url, s3_config

URL_NEON = (
    "postgresql://neondb_owner:secreto@ep-jolly-lake-bec4ymn0-pooler.c-9.us-east-2.aws."
    "neon.tech/neondb?sslmode=require&channel_binding=require"
)


def test_conserva_sslmode_y_channel_binding():
    configuracion = parse_database_url(URL_NEON)

    assert configuracion["OPTIONS"] == {
        "sslmode": "require",
        "channel_binding": "require",
    }


def test_extrae_host_puerto_usuario_y_base():
    configuracion = parse_database_url(URL_NEON)

    assert configuracion["HOST"] == "ep-jolly-lake-bec4ymn0-pooler.c-9.us-east-2.aws.neon.tech"
    assert configuracion["NAME"] == "neondb"
    assert configuracion["USER"] == "neondb_owner"
    assert configuracion["PASSWORD"] == "secreto"
    assert configuracion["ENGINE"] == "django.db.backends.postgresql"


def test_sin_query_no_inventa_options():
    configuracion = parse_database_url("postgres://u:p@localhost:5432/base")
    assert "OPTIONS" not in configuracion


def test_respeta_el_puerto_explicito():
    assert parse_database_url("postgres://u:p@host:6543/base")["PORT"] == "6543"


def test_almacenamiento_r2():
    configuracion = s3_config(
        {
            "R2_ACCOUNT_ID": "abc123",
            "R2_BUCKET": "obelisco-media",
            "R2_ACCESS_KEY_ID": "clave",
            "R2_SECRET_ACCESS_KEY": "secreto",
        }
    )

    assert configuracion["AWS_S3_ENDPOINT_URL"] == "https://abc123.r2.cloudflarestorage.com"
    assert configuracion["AWS_S3_REGION_NAME"] == "auto"


def test_almacenamiento_s3_compatible_generico():
    configuracion = s3_config(
        {
            "AWS_ENDPOINT_URL_S3": "https://br-muddy-snow.storage.us-east-2.aws.neon.tech",
            "AWS_STORAGE_BUCKET_NAME": "obelisco",
            "AWS_ACCESS_KEY_ID": "nak_live_x",
            "AWS_SECRET_ACCESS_KEY": "nsk_live_y",
            "AWS_REGION": "us-east-2",
        }
    )

    assert configuracion["AWS_S3_ENDPOINT_URL"].startswith("https://br-muddy-snow")
    assert configuracion["AWS_STORAGE_BUCKET_NAME"] == "obelisco"
    assert configuracion["AWS_S3_REGION_NAME"] == "us-east-2"


def test_sin_configuracion_completa_no_hay_almacenamiento():
    assert s3_config({}) is None
    assert s3_config({"AWS_ENDPOINT_URL_S3": "https://x", "AWS_STORAGE_BUCKET_NAME": "b"}) is None
