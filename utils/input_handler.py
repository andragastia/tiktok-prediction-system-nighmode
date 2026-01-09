import pandas as pd
import os

def save_new_data_to_csv(data_dict, file_path='data/dataset_tiktok.csv'):
    """
    Menyimpan data baru ke file CSV dataset tanpa menghapus data lama (Append Mode).
    """
    try:
        # 1. Cek apakah file ada untuk membaca header/kolom yang valid
        if not os.path.exists(file_path):
            return False, f"File dataset tidak ditemukan di: {file_path}"
        
        # Baca hanya header untuk memastikan urutan kolom sesuai
        df_existing_header = pd.read_csv(file_path, nrows=0)
        expected_cols = df_existing_header.columns.tolist()
        
        # 2. Siapkan baris data baru dengan urutan kolom yang benar
        row_data = {}
        for col in expected_cols:
            # Ambil data dari input user, jika tidak ada isi dengan None/Default
            row_data[col] = data_dict.get(col, None)
            
            # --- Default Value untuk kolom yang tidak diinput user ---
            if col == 'authorMeta.name' and row_data[col] is None:
                row_data[col] = 'Manual_Input_User' # Penanda data manual
            elif col == 'webVideoUrl' and row_data[col] is None:
                row_data[col] = 'https://tiktok.com/manual-entry'
            elif col == 'musicMeta.musicOriginal' and row_data[col] is None:
                row_data[col] = False
        
        # 3. Buat DataFrame 1 baris
        df_new = pd.DataFrame([row_data])
        
        # 4. Append ke CSV (mode='a') tanpa menulis header lagi
        df_new.to_csv(file_path, mode='a', header=False, index=False)
        
        return True, "Data berhasil disimpan ke database!"
    
    except Exception as e:
        return False, f"Terjadi kesalahan saat menyimpan: {str(e)}"