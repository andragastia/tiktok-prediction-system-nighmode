import pandas as pd
import os
import random
import string
import time # Tambahkan ini

def generate_unique_id():
    """
    Membuat ID unik kombinasi Timestamp + Random.
    Format: [TimestampDetik][3DigitAcak] -> Dijamin beda tiap input.
    """
    timestamp_part = str(int(time.time())) # Contoh: 1709123456
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"{timestamp_part}{random_part}"

def save_new_data_to_csv(new_data_dict, file_path='data/dataset_tiktok.csv'):
    try:
        if os.path.exists(file_path):
            df_old = pd.read_csv(file_path)
            existing_columns = df_old.columns.tolist()
        else:
            return False, "File dataset tidak ditemukan!"

        complete_data_row = {col: None for col in existing_columns}
        complete_data_row.update(new_data_dict)

        final_row = {}
        
        # --- GENERATE ID BARU ---
        # Kita panggil fungsi baru ini
        new_unique_id = generate_unique_id()
        
        for col, val in complete_data_row.items():
            if val is not None:
                final_row[col] = val
            else:
                # Logika Default Value
                col_lower = col.lower()
                if 'id' in col_lower: 
                    final_row[col] = new_unique_id  # Pastikan ID masuk sini
                elif 'name' in col_lower or 'author' in col_lower:
                    final_row[col] = "Admin_Tester" 
                elif 'text' in col_lower or 'desc' in col_lower:
                    # Tambahkan ID ke text agar tidak dianggap duplikat konten
                    final_row[col] = f"Konten Test Baru {new_unique_id}" 
                elif 'count' in col_lower or 'duration' in col_lower: 
                    final_row[col] = 0        
                elif 'original' in col_lower:       
                    final_row[col] = False
                else:
                    final_row[col] = "-"

        df_new = pd.DataFrame([final_row])
        df_updated = pd.concat([df_old, df_new], ignore_index=True)
        df_updated.to_csv(file_path, index=False)
        
        return True, "Data tersimpan! ID Unik: " + new_unique_id
        
    except Exception as e:
        return False, f"Gagal menyimpan: {str(e)}"