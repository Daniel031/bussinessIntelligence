from app import db, Donante, Articulo, Sucursal, Fecha, Donacion
from faker import Faker
from random import randint

fake = Faker()

db.create_all()

# Verificar si ya existen registros en la base de datos
if Donante.query.count() == 0:
    # Generar 5000 registros aleatorios
    meses_listado = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for _ in range(3000):
        # Generar datos aleatorios para cada tabla
        nombre_donante = fake.name()
        fecha_nacimiento = fake.date_of_birth()
        nombre_articulo = fake.word()
        categoria_articulo = fake.word()
        nombre_sucursal = fake.company()
        dia_fecha = randint(1, 31)
        mes_fecha = randint(1, 12)
        anio_fecha = randint(2019, 2023)
        cant_articulo = randint(1, 7)
        total_monto = randint(0, 1000)
        cant_donantes = randint(1, 5)

        dia_fecha =   meses_listado[mes_fecha - 1] if (dia_fecha % meses_listado[mes_fecha - 1]) == 0 else (dia_fecha % meses_listado[mes_fecha - 1])

        # Crear registros en la base de datos
        donante = Donante(fecha_nacimiento=fecha_nacimiento)
        db.session.add(donante)
        
        articulo = Articulo(nombre=nombre_articulo, categoria=categoria_articulo)
        db.session.add(articulo)

        sucursal = Sucursal(nombre=nombre_sucursal)
        db.session.add(sucursal)

        fecha = Fecha(dia=dia_fecha, mes=mes_fecha, anio=anio_fecha)
        db.session.add(fecha)

        donacion = Donacion(cant_articulo=cant_articulo, total_monto=total_monto, cant_donantes=cant_donantes, donante=donante, sucursal=sucursal, fecha=fecha, articulo=articulo)
        db.session.add(donacion)

    # Guardar los cambios en la base de datos
    db.session.commit()
else:
    print("Los registros ya existen en la base de datos, no se requiere carga adicional.")
