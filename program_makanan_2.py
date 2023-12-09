# PROGRAM KHUSUS UNTUK TEST CASE 1

import itertools
import json
from multiprocessing import Pool
import timeit

# Load data dari dataset makanan
with open("data_makanan_4.json", 'r') as file:
    data = json.load(file)

data_makanan = list(data["result"])

# data AKG dan toleransi yang diinginkan
kebutuhan_kalori_harian = 2650
kebutuhan_protein_harian = 65
kebutuhan_lemak_harian = 75
kebutuhan_karbohidrat_harian = 430
toleransi = 0.05

# fungsi untuk menghitung total nutrisi pada suatu kombinasi
def total_nutrisi(kombinasi):
    total_kalori = sum(item["calories"] for item in kombinasi)
    total_protein = sum(item["protein"]["quantity"] for item in kombinasi)
    total_lemak = sum(item["fat"]["quantity"] for item in kombinasi)
    total_karbohidrat = sum(item["carbs"]["quantity"] for item in kombinasi)
    return total_kalori, total_protein, total_lemak, total_karbohidrat

# fungsi yang menerapkan aljabar boolean untuk mengecek apakah suatu kombinasi valid atau tidak
def is_within_tolerance(kombinasi):
    total_kalori, total_protein, total_lemak, total_karbohidrat = total_nutrisi(kombinasi)
    return (
        kebutuhan_kalori_harian * (1 - toleransi) <= total_kalori <= kebutuhan_kalori_harian * (1 + toleransi) and
        kebutuhan_protein_harian * (1 - toleransi) <= total_protein <= kebutuhan_protein_harian * (1 + toleransi) and
        kebutuhan_lemak_harian * (1 - toleransi) <= total_lemak <= kebutuhan_lemak_harian * (1 + toleransi) and
        kebutuhan_karbohidrat_harian * (1 - toleransi) <= total_karbohidrat <= kebutuhan_karbohidrat_harian * (1 + toleransi)
    )

# fungsi yang melakukan pengecekan kevalidan semua kombinasi yang terbentuk,
# dan hanya akan mengembalikan kombinasi yang valid saja
def process_combination(combination):
    if is_within_tolerance(combination):
        return combination

# Program utama
if __name__ == '__main__':
    print(len(data_makanan))
    
    start = timeit.default_timer()
    kombinasi_valid = []

    # proses pemebentukan semua kombinasi dari dataset yang dimiliki menggunakan bantuan dari
    # multiprocessing untuk mempercepat proses pembuatan kombinasinya
    with Pool() as pool:
        for panjang_kombinasi in range(3, 5):
            kombinasi = itertools.combinations(data_makanan, panjang_kombinasi)
            for result in pool.imap(process_combination, kombinasi):
                if result:
                    kombinasi_valid.append(result)
    
    stop = timeit.default_timer() 
    

    # Menampilkan hasil
    print("Kombinasi Makanan yang Memenuhi Syarat:")
    for kombinasi in kombinasi_valid:
        nama_makanan = [item["name"] for item in kombinasi]
        print(", ".join(nama_makanan))
        total_kalori, total_protein, total_lemak, total_karbohidrat = total_nutrisi(kombinasi)
        print(f"Total Kalori: {total_kalori}, Protein: {total_protein} g, Lemak: {total_lemak} g, Karbohidrat: {total_karbohidrat} g\n")
    
    # Menyimpan hasil dalam file
    with open('hasil_kombinasi_makanan_tes_case_1.txt', 'w') as outfile:
        outfile.write("Kombinasi Makanan yang Memenuhi Syarat:\n")
        for kombinasi in kombinasi_valid:
            nama_makanan = [item["name"] for item in kombinasi]
            total_kalori, total_protein, total_lemak, total_karbohidrat = total_nutrisi(kombinasi)
            outfile.write(f"Kombinasi: {', '.join(nama_makanan)}\n")
            outfile.write(f"Total Kalori: {total_kalori}, Protein: {total_protein} g, Lemak: {total_lemak} g, Karbohidrat: {total_karbohidrat} g\n\n")
    
    print("\n\nHasil kombinasi juga dituliskan pada file hasil_kombinasi_makanan_tes_case_1.txt")
    print("\n\nLama waktu eksekusi: ", stop-start, "s")
    