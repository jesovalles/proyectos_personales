import numpy as np
import pandas as pd
import pickle
import streamlit as st

# Cargar el modelo guardado
loaded_model = pickle.load(open('C:\\Users\\Alejandro\\Proyectos\\Personal Projects\\Despliegue de modelo\\Despliegue de modelo usando Streamlit - Exporte CSV\\modelo_entrenado.sav', 'rb'))

# Función para predecir
def diabetes_prediction(input_data):
    predictions = loaded_model.predict(input_data)
    return predictions

# Aplicación web
def main():
    st.title('Predicción de Diabetes Web App')
    
    # Cargar el dataset
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        
        # Mostrar el dataset cargado
        st.write(data)
        
        # Obtener las columnas del dataset
        columns = data.columns.tolist()
        
        # Verificar si todas las columnas necesarias están presentes
        required_columns = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        if all(col in columns for col in required_columns):
            
            # Eliminar las filas con valores faltantes
            data_for_prediction = data.dropna(subset=required_columns)
            
            # Realizar la predicción
            predictions = diabetes_prediction(data_for_prediction[required_columns])
            
            # Agregar las predicciones al dataframe original
            data['DiabetesPrediction'] = predictions
            
            # Eliminar la columna 'Outcome'
            if 'Outcome' in data.columns:
                data.drop(columns=['Outcome'], inplace=True)
            
            # Mostrar el dataset con las predicciones
            st.write("Dataset con predicciones:", data)
            
            # Exportar el dataset resultante a un archivo CSV
            csv_file = data.to_csv(index=False)
            st.download_button(label="Descargar CSV", data=csv_file, file_name="dataset_con_predicciones.csv", mime="text/csv")
            
        else:
            st.error("El archivo CSV debe contener las siguientes columnas: {}".format(', '.join(required_columns)))
        
# Ejecución de la función
if __name__ == '__main__':
    main()


    
    
    
    
    
    
    
    
    
  
    
  