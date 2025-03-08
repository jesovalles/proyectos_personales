# importando librerias
import numpy as np
import pickle
import streamlit as st

# cargando el modelo guardado
loaded_model = pickle.load(open('C:\\Users\\Alejandro\\Proyectos\\Personal Projects\\Despliegue de modelo\\Despliegue usando Streamlit\\modelo_entrenado.sav', 'rb'))

# creando una funcion para predecir
def diabetes_prediction(input_data):
    
    # cambiar input_data a un numpy array
    input_data_as_numpy_array = np.asarray(input_data)

    # reformando el array para que contenga 1 fila y un numero de columnas determinado
    input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)

    # realizando la prediccion
    prediction = loaded_model.predict(input_data_reshaped)
    print(f'El resultado es {prediction[0]}')

    if (prediction[0] == 0):
        return 'La persona no es diabetica'
    else:
        return 'La persona es diabetica'

# creando aplicacion web
def main():
    
    # creando un titulo
    st.title('Predicción de Diabetes Web App')
    
    # solicitando los datos al usuario para la prediccion
    Pregnancies = st.text_input('Número de embarazos')
    Glucose = st.text_input('Nivel de glucosa')
    BloodPressure = st.text_input('Presión arterial')
    SkinThickness = st.text_input('Grosor de la piel')
    Insulin = st.text_input('Nivel de insulina')
    BMI = st.text_input('Indice de masa corporal - BMI')
    DiabetesPedigreeFunction = st.text_input('Valor de la función pedigrí de diabetes')
    Age = st.text_input('Edad')
    
    # codigo para la prediccion
    diagnosis = ''
    
    # creando un boton para ejecutar la prediccion
    if st.button('Resultado de la prueba'):
        diagnosis = diabetes_prediction([Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age])

    # mensaje de exito de la ejecucion de la funcion
    st.success(diagnosis)

# ejecucion de la funcion
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
  
    
  