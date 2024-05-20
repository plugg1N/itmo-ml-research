import pandas as pd
import streamlit as st
import pickle

import warnings
warnings.simplefilter("ignore")

from catboost import CatBoostClassifier
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler



st.set_page_config(layout="wide")

col1, col2 = st.columns(2)


# Map for converting encoded labels into real ones
compounds = ['0 (CFU/ml)', '10² (CFU/ml)', '10³ (CFU/ml)', '10⁴ (CFU/ml)', '10⁵ (CFU/ml)', '10⁶ (CFU/ml)', '10⁷ (CFU/ml)', '10⁸ (CFU/ml)', '10⁹ (CFU/ml)']
map_to = list(map(str, list(range(9))))
comp_map = dict(zip(map_to, compounds))


with col1:
    st.title('Определение концентрации')
    uploaded_file = st.file_uploader("Выберите CSV файл:", type="csv")

    loaded_model = CatBoostClassifier().load_model('models/clf_rs.cbm')
    with open('scalers/rs_scaler.pkl', 'rb') as file: scaler = pickle.load(file)

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write('Содержимое CSV файла:')
        st.write(data.sample(3))

        data = scaler.transform(data)

        preds = [comp_map[str(int(i))] for i in loaded_model.predict(data)]
        download_data = pd.DataFrame(data={'predictions':preds}).to_csv(index=False).encode('utf-8')
        
        st.title('Полученные предсказания')
        st.dataframe(pd.DataFrame(data={'predictions':preds}).head(3))

        st.download_button(label='Скачать предсказания модели (CSV)',
                        data=download_data,
                        file_name='inference.csv')
        

with col2:
    if uploaded_file is not None:
        st.header('Распределение предсказаний')

        sns.set_theme(style='ticks', rc={'text.color': 'white', 'axes.facecolor':'#0e1117', 'figure.facecolor':'#0e1117'})
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.tick_params(axis = 'x', colors = 'white')
        ax.tick_params(axis = 'y', colors = 'white')

        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        


        sns.histplot(pd.DataFrame(data={'predictions':preds})['predictions'])
        st.pyplot(fig)
