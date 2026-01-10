import pandas as pd
import os

def save_new_data_to_csv(new_data_dict, file_path='data/dataset_tiktok.csv'):
    try:
        # 1. Load data lama untuk mengambil struktur kolom (Schema)
        if os.path.exists(file_path):
            df_old = pd.read_csv(file_path)
            existing_columns = df_old.columns.tolist()
        else:
            return False, "File dataset tidak ditemukan!"

        # 2. Siapkan dictionary baru dengan SEMUA kolom yang ada di CSV lama
        #    Isi default dengan None/NaN dulu
        complete_data_row = {col: None for col in existing_columns}
        
        # 3. Timpa (Update) dengan data dari Input User
        #    Ini memastikan data user masuk, sisanya tetap None
        complete_data_row.update(new_data_dict)
        
        # 4. Handling Nilai Kosong (PENTING AGAR TIDAK DI-DROP DASHBOARD)
        #    Kita isi nilai NaN dengan default value agar lolos filter cleaning
        final_row = {}
        for col, val in complete_data_row.items():
            if val is None:
                # Logika Default Value:
                if 'Count' in col or 'duration' in col: 
                    final_row[col] = 0        # Kolom angka diisi 0
                elif 'original' in col:       # Kolom boolean
                    final_row[col] = False
                else:
                    final_row[col] = "-"      # Kolom teks diisi "-"
            else:
                final_row[col] = val

        # 5. Buat DataFrame baru dan simpan
        df_new = pd.DataFrame([final_row])
        
        # Gabungkan dan simpan
        df_updated = pd.concat([df_old, df_new], ignore_index=True)
        df_updated.to_csv(file_path, index=False)
        
        return True, "Data berhasil disimpan dan struktur kolom disesuaikan!"
        
    except Exception as e:
        return False, f"Gagal menyimpan: {str(e)}"