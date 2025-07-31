import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from component.data import get_data, refresh_data, preprocess_data
from sklearn.metrics import r2_score, mean_squared_error
import pickle
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

def mlp (X_train, X_test, y_train, y_test):
    #mlp = multilayer perceptron / neural network for regression.
    #to setup parameter, please refer to = https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html
    mlp_model = MLPRegressor(random_state=42)
    #mlp_model = MLPRegressor(hidden_layer_sizes=(100,100, ), max_iter=1000, random_state=42)
    #the model learning from training data
    mlp_model.fit(X_train, y_train)
    #get the prediction output
    y_pred = mlp_model.predict(X_test)
    y_pred = np.round(y_pred, 0)

    #get the root mean square error between prediction and real test data
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = mlp_model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred

def knn (X_train, X_test, y_train, y_test):
    #k nearest neighbor for regression.
    #to setup the parameter please refer to : https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html
    knn_model = KNeighborsRegressor()
    #the model is learning from training data
    knn_model.fit(X_train,  y_train)
    #get the prediction output
    y_pred = knn_model.predict(X_test)
    y_pred = np.round(y_pred, 0)
    #get the root mean square error between prediction and real test data
    rmse =np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = knn_model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred

def dt (X_train, X_test, y_train, y_test):
    model= DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred = np.round(y_pred, 0)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred

def svm (X_train, X_test, y_train, y_test):
    model=SVR()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred = np.round(y_pred, 0)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred

def rf (X_train, X_test, y_train, y_test):
    model=RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred = np.round(y_pred, 0)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred

def rl (X_train, X_test, y_train, y_test):
    model=LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred = np.round(y_pred, 0)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred

def rl (X_train, X_test, y_train, y_test):
    model=LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred = np.round(y_pred, 0)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = model.score(X_test, y_test)
    #get the pearson correlation
    corr, p_value = pearsonr(y_test, y_pred)
    #returning the output of RMSE, corr, and prediction result
    return rmse, r2, corr, y_pred


    #calling the function mlp.
    #returning rmse, pearson correlation, and prediction output
    # rmse_mlp, corr_mlp, y_pred_mlp = mlp(X_train, X_test, y_train, y_test)
    # #calling the function knn
    # #returning rmse, pearson correlation, and prediction output
    # rmse_knn, corr_knn, y_pred_knn = knn(X_train, X_test, y_train, y_test)
    # rmse_dt, corr_dt, y_pred_dt = dt(X_train, X_test, y_train, y_test)
    # #rmse_svm, corr_svm, y_pred_svm = svm(X_train, X_test, y_train, y_test)
    # rmse_rf, corr_rf, y_pred_rf = rf(X_train, X_test, y_train, y_test)
    # rmse_rl, corr_rl, y_pred_rl = rl(X_train, X_test, y_train, y_test)

def visualisasi_model(existing_djm):

    year_columns = [col for col in existing_djm.columns if str(col).isdigit()]
    tahun = st.selectbox('Pilih Tahun', year_columns[:-1])
    tahun_selanjutnya = str(int(tahun) + 1)

    # Menampilkan data berdasarkan tahun yang dipilih
    df_tahun = existing_djm[['Prodi', int(tahun), int(tahun_selanjutnya)]].copy()
    df_tahun.columns = ['Program Studi', 'Jumlah Mahasiswa Baru Saat Ini', 'Jumlah Mahasiswa Baru Setelahnya']

    # Menghapus baris dengan NaN pada 'Jumlah Mahasiswa Setelahnya'
    df_tahun = df_tahun.dropna(subset=['Jumlah Mahasiswa Baru Setelahnya'])


    # Membuat scatter plot berdasarkan tahun yang dipilih
    X = df_tahun['Jumlah Mahasiswa Baru Saat Ini'].values.reshape(-1, 1)  # Jumlah Mahasiswa Saat Ini
    y = df_tahun['Jumlah Mahasiswa Baru Setelahnya'].values  # Jumlah Mahasiswa Setelahnya

    # Membuat model regresi linear
    model = pickle.load(open("next_year_students_prediction.sav", "rb"))
    model.fit(X, y)
    y_pred = model.predict(X)

    # Menghitung nilai R²
    r2 = r2_score(y, y_pred)
    r2 = round (r2, 2)
    st.write(f'Nilai R² untuk prediksi tahun selanjutnya adalah: ', r2)  # Menampilkan R²

    # Menghitung nilai RMSE
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    rmse = round(rmse, 2)
    st.write(f'Root Mean Squared Error (RMSE): {rmse}')  # Menampilkan RMSE


    # Menambahkan kolom prediksi ke df_tahun
    df_tahun['Prediksi Jumlah Mahasiswa Baru Setelahnya'] = np.round(y_pred)

    average_row = pd.DataFrame({
        'Program Studi': ['Average'],
        'Jumlah Mahasiswa Baru Saat Ini': [df_tahun['Jumlah Mahasiswa Baru Saat Ini'].mean(skipna=True)],
        'Jumlah Mahasiswa Baru Setelahnya': [df_tahun['Jumlah Mahasiswa Baru Setelahnya'].mean(skipna=True)],
        'Prediksi Jumlah Mahasiswa Baru Setelahnya': [df_tahun['Prediksi Jumlah Mahasiswa Baru Setelahnya'].mean(skipna=True)]
    })
    # Menambahkan baris rata-rata ke dataframe
    df_tahun = pd.concat([df_tahun, average_row], ignore_index=True)


    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, color='blue', label='Data Sebenarnya')
    # Menambahkan garis regresi merah
    plt.plot(X, y_pred, color='red', linewidth=2, label='Data Prediksi')
    # Menambahkan label, judul tanpa legend dan grid
    plt.title(f"Scatter Plot Linear Regression\nTahun: {tahun}", fontsize=18)
    plt.xlabel('Jumlah Mahasiswa Baru Saat Ini', fontsize=12)
    plt.ylabel('Jumlah Mahasiswa Baru Setelahnya', fontsize=12)
    plt.grid(False)
    plt.legend()
    # Menampilkan grafik di Streamlit
    st.pyplot(plt)


    # Matriks Korelasi
    st.write("Matriks Korelasi")
    # Menghitung korelasi menggunakan data 'Jumlah Mahasiswa Saat Ini' dan 'Jumlah Mahasiswa Setelahnya'
    correlation_df = df_tahun[['Jumlah Mahasiswa Baru Saat Ini', 'Jumlah Mahasiswa Baru Setelahnya']]
    # Menghitung korelasi
    corr = correlation_df.corr()
    # Menampilkan matriks korelasi menggunakan heatmap dari Seaborn
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="Blues", vmin=0, vmax=1, linewidths=0.5)
    # Menampilkan grafik matriks korelasi di Streamlit
    st.pyplot(plt)

    # Menampilkan tabel detail data
    st.write('Tabel Detail Data')
    st.dataframe(df_tahun)



    st.markdown("### Tabel R² dan RMSE Setiap Tahun")

    # metrics_list = []

    # for i in range(len(year_columns) - 1):
    #     tahun_i = year_columns[i]
    #     tahun_i_plus_1 = year_columns[i + 1]

    #     df_pair = existing_djm[[int(tahun_i), int(tahun_i_plus_1)]].dropna()
    #     if df_pair.empty:
    #         continue

    #     X_pair = df_pair[int(tahun_i)].values.reshape(-1, 1)
    #     y_pair = df_pair[int(tahun_i_plus_1)].values

    #     # Gunakan model yang sama
    #     model.fit(X_pair, y_pair)
    #     y_pred_pair = model.predict(X_pair)

    #     r2_pair = r2_score(y_pair, y_pred_pair)
    #     rmse_pair = np.sqrt(mean_squared_error(y_pair, y_pred_pair))

    #     metrics_list.append({
    #         'Tahun': f"{tahun_i} → {tahun_i_plus_1}",
    #         'R²': round(r2_pair, 2),
    #         'RMSE': round(rmse_pair, 2)
    #     })

    # df_metrics = pd.DataFrame(metrics_list)
    # st.dataframe(df_metrics)

    # Membagi data menjadi data latih dan data uji
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # Calling the functions for different models
    rmse_mlp, r2_mlp, corr_mlp, y_pred_mlp = mlp(X_train, X_test, y_train, y_test)
    rmse_knn, r2_knn, corr_knn, y_pred_knn = knn(X_train, X_test, y_train, y_test)
    rmse_dt, r2_dt, corr_dt, y_pred_dt = dt(X_train, X_test, y_train, y_test)
    rmse_rf, r2_rf, corr_rf, y_pred_rf = rf(X_train, X_test, y_train, y_test)
    rmse_rl, r2_rl, corr_rl, y_pred_rl = rl(X_train, X_test, y_train, y_test)

    st.write("### R² dan RMSE untuk Setiap Model")
    st.markdown("#### MLP")
    st.write(f"R²: {r2_mlp:.2f}, RMSE   : {rmse_mlp:.2f}")
    st.markdown("#### KNN")
    st.write(f"R²: {r2_knn:.2f}, RMSE   : {rmse_knn:.2f}")
    st.markdown("#### Decision Tree")    
    st.write(f"R²: {r2_dt:.2f}, RMSE   : {rmse_dt:.2f}")
    st.markdown("#### Random Forest")
    st.write(f"R²: {r2_rf:.2f}, RMSE   : {rmse_rf:.2f}")
    st.markdown("#### Linear Regression")
    st.write(f"R²: {r2_rl:.2f}, RMSE   : {rmse_rl:.2f}")
    st.markdown("### Evaluasi Model Lain")
    st.write("Berikut adalah evaluasi model lain (MLP, KNN, Decision Tree, Random Forest) untuk memprediksi jumlah mahasiswa baru berdasarkan data tahun sebelumnya.")
    st.markdown("### Evaluasi Model Lain (MLP, KNN, Decision Tree, Random Forest)")


    # ===============================
    # Evaluasi Model Lain (MLP, KNN, DT, RF)
    # ===============================
    # model_dict = {
    #     'Linear Regression': LinearRegression(),
    #     'MLP': MLPRegressor(max_iter=1000, random_state=42),
    #     'KNN': KNeighborsRegressor(n_neighbors=5),
    #     'Decision Tree': DecisionTreeRegressor(random_state=42),
    #     'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42)
    # }

    # summary_metrics = []  # untuk rekap akhir semua model

    # for model_name, model_obj in model_dict.items():
    #     metrics_list = []

    #     for i in range(len(year_columns) - 1):
    #         tahun_i = year_columns[i]
    #         tahun_next = year_columns[i + 1]

    #         df_pair = existing_djm[[int(tahun_i), int(tahun_next)]].dropna()
    #         if df_pair.empty:
    #             continue

    #         X_pair = df_pair[int(tahun_i)].values.reshape(-1, 1)
    #         y_pair = df_pair[int(tahun_next)].values

    #         try:
    #             model_obj.fit(X_pair, y_pair)
    #             y_pred_pair = model_obj.predict(X_pair)
    #             r2_val = r2_score(y_pair, y_pred_pair)
    #             rmse_val = np.sqrt(mean_squared_error(y_pair, y_pred_pair))
    #             metrics_list.append({
    #                 'Tahun': f"{tahun_i} → {tahun_next}",
    #                 'R²': round(r2_val, 2),
    #                 'RMSE': round(rmse_val, 2)
    #             })
    #         except:
    #             metrics_list.append({
    #                 'Tahun': f"{tahun_i} → {tahun_next}",
    #                 'R²': None,
    #                 'RMSE': None
    #             })

    #     df_metrics = pd.DataFrame(metrics_list)

    #     # Hitung rata-rata R² dan RMSE (skip NaN)
    #     avg_r2 = df_metrics['R²'].dropna().mean()
    #     avg_rmse = df_metrics['RMSE'].dropna().mean()

    #     # Tambahkan ke ringkasan
    #     summary_metrics.append({
    #         'Model': model_name,
    #         'Rata-rata R²': round(avg_r2, 2) if not np.isnan(avg_r2) else None,
    #         'Rata-rata RMSE': round(avg_rmse, 2) if not np.isnan(avg_rmse) else None
    #     })

    #     # Tampilkan tabel per model
    #     st.markdown(f"#### Model: {model_name}")
    #     st.dataframe(df_metrics)

    #     # Tampilkan rata-rata per model
    #     st.markdown(f"**Rata-rata R²:** {round(avg_r2, 2) if not np.isnan(avg_r2) else '-'}  |  **Rata-rata RMSE:** {round(avg_rmse, 2) if not np.isnan(avg_rmse) else '-'}")

    # # Tampilkan ringkasan rata-rata semua model
    # st.markdown("### Ringkasan Rata-rata R² dan RMSE Semua Model")
    # df_summary = pd.DataFrame(summary_metrics)
    # st.dataframe(df_summary)