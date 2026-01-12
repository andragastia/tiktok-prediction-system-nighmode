import pandas as pd
import os
import time
import random
import string

def save_new_data_to_csv(new_data_dict):
    """
    Menyimpan data baru ke CSV dengan penanganan kolom otomatis & cerdas.
    """
    # Cari path file relatif terhadap file script ini
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(os.path.dirname(current_dir), 'data', 'dataset_tiktok.csv')
    
    try:
        if not os.path.exists(file_path):
            return False, "File database tidak ditemukan!"

        # 1. Baca data lama
        df_old = pd.read_csv(file_path)
        
        # 2. Buat DataFrame dari input baru
        df_new = pd.DataFrame([new_data_dict])
        
        # 3. GABUNGKAN (CONCAT) - Ini inti Pandas
        # Pandas akan otomatis membuat kolom NaN jika di input tidak ada
        df_final = pd.concat([df_old, df_new], ignore_index=True)
        
        # 4. ISI NILAI KOSONG (SMART FILLNA - Menggantikan logika if-else panjang)
        # Kita isi nilai NaN pada baris terakhir (data baru) saja agar aman
        last_idx = df_final.index[-1]
        
        # Default untuk angka -> 0
        num_cols = df_final.select_dtypes(include=['number']).columns
        df_final.loc[last_idx, num_cols] = df_final.loc[last_idx, num_cols].fillna(0)
        
        # Default untuk teks -> "-"
        obj_cols = df_final.select_dtypes(include=['object']).columns
        df_final.loc[last_idx, obj_cols] = df_final.loc[last_idx, obj_cols].fillna("-")
        
        # Default Bool -> False
        bool_cols = df_final.select_dtypes(include=['bool']).columns
        df_final.loc[last_idx, bool_cols] = df_final.loc[last_idx, bool_cols].fillna(False)

        # 5. SIMPAN
        df_final.to_csv(file_path, index=False)
        
        return True, "Data berhasil ditambahkan!"
        
    except Exception as e:
        return False, f"Error sistem: {str(e)}"