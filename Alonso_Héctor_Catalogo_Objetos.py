"""
UD2 - Bloque 4
Tarea individual: primeros pasos del catálogo orientado a objetos

Objetivos:
1. Crear las dataclasses Libro y Socio.
2. Listar libros utilizando class_row.
3. Buscar un libro por su identificador.

Base de datos: biblioteca
"""

import os
from dataclasses import dataclass
from decimal import Decimal

import psycopg
from psycopg.rows import class_row


# ==========================================================
# ACTIVIDAD 1. CREAR LAS DATACLASSES
# ==========================================================

# TODO 1 (completado):
# @dataclass genera el constructor y la representación del objeto.


@dataclass
class Libro:
    id_libro: int
    titulo: str
    autor: str
    precio: Decimal


# TODO 2 (completado):
# telefono admite cadena o None porque en PostgreSQL puede ser NULL.


@dataclass
class Socio:
    id_socio: int
    nombre: str
    apellidos: str
    telefono: str | None
    activo: bool


# ==========================================================
# CONFIGURACIÓN DE LA CONEXIÓN
# ==========================================================


def obtener_configuracion():
    """Recupera la configuración desde variables de entorno."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "connect_timeout": 5,
    }


# ==========================================================
# ACTIVIDAD 2. LISTAR LIBROS CON class_row
# ==========================================================


def listar_libros(conexion) -> list[Libro]:
    """
    Recupera los libros ordenados por título.

    Debe devolver una lista de objetos Libro, no tuplas
    ni diccionarios.
    """

    # TODO 3 (completado):
    # Cursor con row_factory=class_row(Libro), consulta y fetchall().

    consulta = """
        SELECT
            l.id_libro,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellidos) AS autor,
            l.precio
        FROM libros AS l
        JOIN autores AS a
            ON a.id_autor = l.id_autor
        ORDER BY l.titulo
    """

    with conexion.cursor(row_factory=class_row(Libro)) as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()


# ==========================================================
# ACTIVIDAD 3. BUSCAR UN LIBRO POR ID
# ==========================================================


def buscar_libro_por_id(
    conexion,
    id_libro: int,
) -> Libro | None:
    """
    Busca un libro mediante su identificador.

    Devuelve:
    - Un objeto Libro si existe.
    - None si no existe.
    """

    # TODO 4 (completado):
    # Consulta parametrizada con %s, tupla de un elemento (id_libro,)
    # y fetchone(), que devuelve Libro o None.

    consulta = """
        SELECT
            l.id_libro,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellidos) AS autor,
            l.precio
        FROM libros AS l
        JOIN autores AS a
            ON a.id_autor = l.id_autor
        WHERE l.id_libro = %s
    """

    with conexion.cursor(row_factory=class_row(Libro)) as cursor:
        cursor.execute(consulta, (id_libro,))
        return cursor.fetchone()


# ==========================================================
# FUNCIONES DE PRESENTACIÓN YA COMPLETADAS
# ==========================================================


def mostrar_libro(libro: Libro) -> None:
    """Muestra los datos de un objeto Libro."""
    print(
        f"{libro.id_libro} | "
        f"{libro.titulo} | "
        f"{libro.autor} | "
        f"{libro.precio:.2f} €"
    )


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================


def main():
    try:
        configuracion = obtener_configuracion()

        with psycopg.connect(**configuracion) as conexion:
            print("\n--- CATÁLOGO DE LIBROS ---")

            libros = listar_libros(conexion)

            if not libros:
                print("No hay libros registrados.")
            else:
                for libro in libros:
                    mostrar_libro(libro)

            print("\n--- BÚSQUEDA POR IDENTIFICADOR ---")

            # Puedes cambiar este identificador para realizar pruebas.
            id_buscado = 1

            libro_encontrado = buscar_libro_por_id(
                conexion,
                id_buscado,
            )

            if libro_encontrado is None:
                print(
                    "No existe ningún libro con el "
                    f"identificador {id_buscado}."
                )
            else:
                print("Libro encontrado:")
                mostrar_libro(libro_encontrado)

            print("\n--- COMPROBACIÓN DE None ---")

            libro_inexistente = buscar_libro_por_id(
                conexion,
                999999,
            )

            if libro_inexistente is None:
                print(
                    "La búsqueda de un identificador inexistente "
                    "ha devuelto None correctamente."
                )

    except KeyError as error:
        print(
            "Falta una variable de entorno:",
            error,
        )

    except ValueError:
        print(
            "DB_PORT debe contener un número entero."
        )

    except psycopg.OperationalError as error:
        print(
            "No se pudo establecer la conexión "
            "con PostgreSQL."
        )
        print(error)

    except psycopg.Error as error:
        print("Se produjo un error de base de datos.")
        print(error)


if __name__ == "__main__":
    main()


# ==========================================================
# PREGUNTAS DE REVISIÓN
# ==========================================================
#
# 1. ¿Qué ventaja aporta @dataclass?
#    Genera automáticamente el constructor __init__, la
#    representación __repr__ y la comparación __eq__ a partir
#    de los campos declarados, evitando escribir código
#    repetitivo y dejando la clase centrada en los datos.
#
# 2. ¿Qué función tiene class_row(Libro)?
#    Configura el cursor para que convierta cada fila del
#    resultado en una instancia de la clase Libro, asignando
#    cada columna al atributo homónimo, de modo que no hay que
#    trabajar con tuplas ni diccionarios.
#
# 3. ¿Por qué la consulta utiliza AS autor?
#    Porque la columna calculada CONCAT(a.nombre, ' ',
#    a.apellidos) no se llama autor; el alias hace que el nombre
#    de la columna coincida con el atributo autor de la
#    dataclass Libro, permitiendo que class_row pueda asignarle
#    el valor.
#
# 4. ¿Qué tipo de elementos contiene la lista devuelta por
#    listar_libros()?
#    Contiene objetos de la clase Libro; cada elemento tiene
#    acceso a atributos como libro.titulo, libro.autor, etc.
#
# 5. ¿Qué devuelve fetchone() si el identificador no existe?
#    Devuelve None, por lo que la función puede indicar que no
#    hay ningún libro con ese identificador sin lanzar un error.
#
# 6. ¿Por qué escribimos (id_libro,) con una coma?
#    Porque execute() espera una tupla de parámetros; sin la
#    coma, (id_libro) sería simplemente el valor del entero y
#    no una tupla, y la consulta parametrizada fallaría.
