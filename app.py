from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from pandas import Timestamp
from sklearn.linear_model import LinearRegression
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/donaciones'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)

class Donante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_nacimiento = db.Column(db.Date, nullable=False)

class Articulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(255), nullable=False)

class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

class Fecha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)

class Donacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cant_articulo = db.Column(db.Integer, nullable=False)
    total_monto = db.Column(db.Float, nullable=False)
    cant_donantes = db.Column(db.Integer, nullable=False)
    donante_id = db.Column(db.Integer, db.ForeignKey('donante.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    fecha_id = db.Column(db.Integer, db.ForeignKey('fecha.id'), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey('articulo.id'), nullable=False)
    donante = db.relationship('Donante', backref='donaciones')
    sucursal = db.relationship('Sucursal', backref='donaciones')
    fecha = db.relationship('Fecha', backref='donaciones')
    articulo = db.relationship('Articulo', backref='donaciones')

class Monto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    donacion_id = db.Column(db.Integer, db.ForeignKey('donacion.id'), nullable=False)
    donacion = db.relationship('Donacion', backref='montos')

@app.route('/api/donaciones', methods=['GET'])
def get_donaciones():
    # Consultar todas las donaciones y sus fechas
    donaciones = db.session.query(Donacion, Fecha).join(Fecha, Donacion.fecha_id == Fecha.id).all()
    
    # Crear una lista de diccionarios con los datos necesarios
    datos = [{'fecha': f'{fecha.anio}-{fecha.mes:02d}-{fecha.dia:02d}', 'cant_articulo': donacion.cant_articulo} for donacion, fecha in donaciones]

    # Convertir la lista de diccionarios a un DataFrame de pandas
    df = pd.DataFrame(datos)
 
    # Convertir la columna de fechas a un objeto datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Establecer la columna de fechas como el índice del DataFrame
    df.set_index('fecha', inplace=True)
    
    # Agrupar por fecha y sumar la cantidad de artículos donados
    series_temporal = df.resample('D').sum()
    series_temporal = series_temporal.reset_index()
    to_json_series = series_temporal.to_dict(orient='records')
    response = make_response(jsonify(to_json_series))
    response.headers['Content-Type'] = 'application/json'

    return response, 200, {'Access-Control-Allow-Origin':'*'}

@app.route('/api/donaciones/<int:year>', methods=['GET'])
def get_donaciones_por_ano(year):
    # Consultar todas las donaciones y sus fechas para el año especificado
    donaciones = db.session.query(Donacion, Fecha).join(Fecha, Donacion.fecha_id == Fecha.id).filter(Fecha.anio == year).all()
    
    # Crear una lista de diccionarios con los datos necesarios
    datos = [{'fecha': f'{fecha.anio}-{fecha.mes:02d}-{fecha.dia:02d}', 'cant_articulo': donacion.cant_articulo} for donacion, fecha in donaciones]

    # Convertir la lista de diccionarios a un DataFrame de pandas
    df = pd.DataFrame(datos)
 
    # Convertir la columna de fechas a un objeto datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Establecer la columna de fechas como el índice del DataFrame
    df.set_index('fecha', inplace=True)
    
    # Agrupar por mes y sumar la cantidad de artículos donados
    series_temporal = df.resample('M').sum()
    series_temporal = series_temporal.reset_index()
    to_json_series = series_temporal.to_dict(orient='records')
    response = make_response(jsonify(to_json_series))
    response.headers['Content-Type'] = 'application/json'

    return response, 200, {'Access-Control-Allow-Origin':'*'}

@app.route('/api/anos_disponibles', methods=['GET'])
def get_anos_disponibles():
    # Consultar todos los años únicos en la tabla Fecha
    anos = db.session.query(Fecha.anio).distinct().order_by(Fecha.anio).all()
    
    # Convertir el resultado a una lista de años
    anos_disponibles = [anio.anio for anio in anos]
    
    response = make_response(jsonify(anos_disponibles))
    response.headers['Content-Type'] = 'application/json'

    return response, 200, {'Access-Control-Allow-Origin': '*'}

@app.route('/api/prediccion/<int:year>', methods=['GET'])
def get_prediccion(year):
    # Consultar todas las donaciones y sus fechas para el año especificado
    donaciones = db.session.query(Donacion, Fecha).join(Fecha, Donacion.fecha_id == Fecha.id).filter(Fecha.anio == year).all()
    
    # Crear una lista de diccionarios con los datos necesarios
    datos = [{'fecha': f'{fecha.anio}-{fecha.mes:02d}-{fecha.dia:02d}', 'cant_articulo': donacion.cant_articulo} for donacion, fecha in donaciones]

    # Convertir la lista de diccionarios a un DataFrame de pandas
    df = pd.DataFrame(datos)
 
    # Convertir la columna de fechas a un objeto datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Establecer la columna de fechas como el índice del DataFrame
    df.set_index('fecha', inplace=True)
    
    # Agrupar por mes y sumar la cantidad de artículos donados
    series_temporal = df.resample('M').sum()
    
    # Crear una columna con el número de meses desde el inicio
    series_temporal['mes'] = np.arange(len(series_temporal))

    # Modelar con regresión lineal
    X = series_temporal[['mes']]
    y = series_temporal['cant_articulo']
    modelo = LinearRegression()
    modelo.fit(X, y)

    # Predecir los próximos 6 meses (en lugar de 3)
    meses_futuros = np.array([[len(series_temporal) + i] for i in range(6)])
    predicciones = modelo.predict(meses_futuros)

    # Crear un DataFrame para los meses futuros
    fechas_futuras = pd.date_range(start=series_temporal.index[-1] + pd.DateOffset(months=1), periods=6, freq='M')
    predicciones_df = pd.DataFrame({'fecha': fechas_futuras, 'cant_articulo': predicciones})

    # Convertir a JSON
    predicciones_json = predicciones_df.to_dict(orient='records')
    response = make_response(jsonify(predicciones_json))
    response.headers['Content-Type'] = 'application/json'

    return response, 200, {'Access-Control-Allow-Origin': '*'}

@app.route('/api/prediccion-a/<int:year>', methods=['GET'])
def get_prediccion_a(year):
    # Consultar todas las donaciones y sus fechas para el año especificado
    donaciones = db.session.query(Donacion, Fecha).join(Fecha, Donacion.fecha_id == Fecha.id).filter(Fecha.anio == year).all()
    
    # Crear una lista de diccionarios con los datos necesarios
    datos = [{'fecha': f'{fecha.anio}-{fecha.mes:02d}-{fecha.dia:02d}', 'cant_articulo': donacion.cant_articulo} for donacion, fecha in donaciones]

    # Convertir la lista de diccionarios a un DataFrame de pandas
    df = pd.DataFrame(datos)
 
    # Convertir la columna de fechas a un objeto datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Establecer la columna de fechas como el índice del DataFrame
    df.set_index('fecha', inplace=True)
    
    # Agrupar por mes y sumar la cantidad de artículos donados
    series_temporal = df.resample('M').sum()

    # Modelar con ARIMA
    modelo = ARIMA(series_temporal['cant_articulo'], order=(5, 1, 0))
    modelo_fit = modelo.fit()

    # Predecir los próximos 12 meses
    predicciones = modelo_fit.forecast(steps=12)
    fechas_futuras = pd.date_range(start=series_temporal.index[-1] + pd.DateOffset(months=1), periods=12, freq='M')
    predicciones_df = pd.DataFrame({'fecha': fechas_futuras, 'cant_articulo': predicciones})

    # Convertir a JSON
    predicciones_json = predicciones_df.to_dict(orient='records')
    response = make_response(jsonify(predicciones_json))
    response.headers['Content-Type'] = 'application/json'

    return response, 200, {'Access-Control-Allow-Origin': '*'}

if __name__ == '__main__':
    app.run(debug=True)
