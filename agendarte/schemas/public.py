# -*- coding: utf-8 -*-
from __future__ import annotations
from enum import Enum
from sqlalchemy import func
from tai_sql import *
from tai_sql.generators import *

datasource(
    provider=env('MAIN_DATABASE_URL'),
    schema='public',
    syntax='v2',
    operative_fields=True,      # created_at / updated_at / created_by / updated_by
)

generate(
    PythonClientGenerator(output_dir='database'),
    ERDiagramGenerator(output_dir='diagrams', 
                       format='html',
                       theme='corporate',
                       include_columns=True),
)



class Estado(Enum):
    """Estado de publicación de un post."""
    REALIZADO = 'realizado'
    PENDIENTE = 'pendiente'

class Tipo_Evento(Enum):
    """Tipo de evento."""
    SHOW = 'show'
    ENSAYO = 'ensayo'
    GRABACION = 'grabacion'
    OTROS = 'otros'

class Usuario(Table):
    """Usuarios del sistema."""
    __tablename__ = 'usuario'

    id: col[int] = column(primary_key=True, autoincrement=True)
    nombre: col[str] = column(description='Nombre visible')
    apellido: col[str] = column(description='Apellido visible')
    email: col[str] = column(unique=True)
    created_at: col[datetime] = column(server_now=True)

    proyectos: onetomany[Proyecto]
    eventos: onetomany[Evento]
    repertorios: onetomany[Repertorio]


class Proyecto(Table):
    """Proyectos del usuario."""
    __tablename__ = 'proyecto'

    id: col[int] = column(primary_key=True, autoincrement=True)
    id_usuario: col[int] = column(description='Usuario propietario del proyecto')
    nombre: col[str] = column(description='Nombre del proyecto', unique=True)
    tipo: col[str | None] = column(description='Tipo de proyecto')
    descripcion: col[str | None] = column(description='Descripción del proyecto')
    created_at: col[datetime] = column(server_now=True)

    usuario: manytoone[Usuario] = relation(
        fields=['id_usuario'], references=['id'],
        backref='proyectos', onDelete='cascade')
    eventos: onetomany[Evento]
    repertorios: onetomany[Repertorio]

    
class Evento(Table):
    """Eventos del musico"""
    __tablename__ = 'evento'

    id: col[int] = column(primary_key=True, autoincrement=True)
    usuario_id: col[int] = column(description='Usuario que crea el evento')
    id_proyecto: col[int | None] = column(description='Proyecto al que pertenece el evento')
    nombre: col[str] = column(description='Nombre del evento', unique=True)
    ubicacion: col[str | None] = column(description='Ubicacion del evento')
    tipo: col[Tipo_Evento] = column(description='Tipo de evento')
    fecha: col[datetime] = column(description='Fecha del evento')
    hora: col[time] = column(description='Hora del evento')
    estado: col[Estado] = column(description='Estado del evento', default=Estado.PENDIENTE)
    notas: col[str | None] = column(description='Notas adicionales del evento')
    created_at: col[datetime] = column(server_now=True)

    proyecto: manytoone[Proyecto] = relation(
        fields=['id_proyecto'], references=['id'],
        backref='eventos', onDelete='cascade')

    usuario: manytoone[Usuario] = relation(
        fields=['usuario_id'], references=['id'],
        backref='eventos', onDelete='cascade')

    gastos: onetomany[Gasto]
    ingresos: onetomany[Ingreso]

    

class Repertorio(Table):
    """Repertorios del usuario"""
    __tablename__ = 'repertorio'
    id: col[int] = column(primary_key=True, autoincrement=True)
    usuario_id: col[int] = column(description='Usuario que crea el evento')
    id_proyecto: col[int | None] = column(description='Proyecto al que pertenece el repertorio')
    nombre: col[str] = column(description='Nombre del repertorio', unique=True)
    canciones: onetomany[Cancion]
    descripcion: col[str | None] = column(description='Descripción del repertorio')
    created_at: col[datetime] = column(server_now=True)


    usuario: manytoone[Usuario] = relation(
        fields=['usuario_id'], references=['id'],
        backref='repertorios', onDelete='cascade')
    proyecto: manytoone[Proyecto] = relation(
        fields=['id_proyecto'], references=['id'],
        backref='repertorios', onDelete='cascade')

    
class Cancion(Table):
    """Canciones del usuario"""
    __tablename__ = 'cancion'

    id: col[int] = column(primary_key=True, autoincrement=True)
    id_repertorio: col[int | None] = column(description='Repertorio al que pertenece la canción')
    nombre: col[str] = column(description='Nombre de la canción', unique=True)
    created_at: col[datetime] = column(server_now=True)

    repertorio: manytoone[Repertorio] = relation(
        fields=['id_repertorio'], references=['id'],
        backref='canciones', onDelete='cascade')


class Gasto(Table):
    """Gastos del usuario"""
    __tablename__ = 'gasto'

    id: col[int] = column(primary_key=True, autoincrement=True)
    id_evento: col[int | None] = column(description='Evento al que pertenece el gasto')
    nombre: col[str] = column(description='Nombre del gasto', unique=True)
    importe: col[numeric] = column(precision=10, scale=2, description='Monto del gasto')
    pagado: col[bool] = column(description='Indica si el gasto ha sido pagado o no', default=False)
    concepto: col[str | None] = column(description='Concepto del gasto')
    created_at: col[datetime] = column(server_now=True)


    evento: manytoone[Evento] = relation(
        fields=['id_evento'], references=['id'],
        backref='gastos', onDelete='cascade')

   
class Ingreso(Table):
    """Ingresos del usuario"""
    __tablename__ = 'ingreso'

    id: col[int] = column(primary_key=True, autoincrement=True)
    id_evento: col[int | None] = column(description='Evento al que pertenece el ingreso')
    nombre: col[str] = column(description='Nombre del ingreso', unique=True)
    importe: col[numeric] = column(precision=10, scale=2, description='Monto del ingreso')
    recibido: col[bool] = column(description='Indica si el ingreso ha sido recibido o no', default=False)
    concepto: col[str | None] = column(description='Concepto del ingreso')
    created_at: col[datetime] = column(server_now=True)

    evento: manytoone[Evento] = relation(
        fields=['id_evento'], references=['id'],
        backref='ingresos', onDelete='cascade')

    