import itertools
import json
from multiprocessing import Pool
import timeit

# fungsi untuk menghitung BMR dikalikan tingkat aktiitas seseorang
def calculate_activity_level(bmr, activity_level):
    if activity_level == 'sedentary':
        return bmr * 1.2
    elif activity_level == 'lightly active':
        return bmr * 1.375
    elif activity_level == 'moderately active':
        return bmr * 1.55
    elif activity_level == 'very active':
        return bmr * 1.725
    elif activity_level == 'extra active':
        return bmr * 1.9
    else:
        return bmr

# fungsi untuk menghitung kebutuhan kalori harian seseorang
def calculate_daily_calories(weight, height, age, gender, activiy_level):
    if gender.lower() == 'male':
        bmr = 66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age)
    else: 
        bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)
    return calculate_activity_level(bmr, activiy_level)

# fungsi untuk menghitung kebutuhan makronutrien harian seseorang
def calculate_macro_requirements(total_calories):
    protein_calories = total_calories * 0.15  # 15% dari total kalori
    protein_grams = protein_calories / 4

    fat_calories = total_calories * 0.20  # 20% dari total kalori
    fat_grams = fat_calories / 9

    carbs_calories = total_calories * 0.65  # 65% dari total kalori
    carbs_grams = carbs_calories / 4

    return protein_grams, fat_grams, carbs_grams

# Load data dari dataset makanan
with open("data_makanan_4.json", 'r') as file:
    data = json.load(file)

data_makanan = list(data["result"])[0:100]

# Toleransi yang diinginkan
toleransi = 0.05

# fungsi untuk menghitung total nutrisi pada suatu kombinasi
def total_nutrisi(kombinasi):
    total_kalori = sum(item["calories"] for item in kombinasi)
    total_protein = sum(item["protein"]["quantity"] for item in kombinasi)
    total_lemak = sum(item["fat"]["quantity"] for item in kombinasi)
    total_karbohidrat = sum(item["carbs"]["quantity"] for item in kombinasi)
    return total_kalori, total_protein, total_lemak, total_karbohidrat

# fungsi yang menerapkan aljabar boolean untuk mengecek apakah suatu kombinasi valid atau tidak
def is_within_tolerance(kombinasi, kebutuhan_kalori_harian, kebutuhan_protein_harian, kebutuhan_lemak_harian, kebutuhan_karbohidrat_harian, toleransi):
    total_kalori, total_protein, total_lemak, total_karbohidrat = total_nutrisi(kombinasi)
    return (
        kebutuhan_kalori_harian * (1 - toleransi) <= total_kalori <= kebutuhan_kalori_harian * (1 + toleransi) and
        kebutuhan_protein_harian * (1 - toleransi) <= total_protein <= kebutuhan_protein_harian * (1 + toleransi) and
        kebutuhan_lemak_harian * (1 - toleransi) <= total_lemak <= kebutuhan_lemak_harian * (1 + toleransi) and
        kebutuhan_karbohidrat_harian * (1 - toleransi) <= total_karbohidrat <= kebutuhan_karbohidrat_harian * (1 + toleransi)
    )

# fungsi yang melakukan pengecekan kevalidan semua kombinasi yang terbentuk,
# dan hanya akan mengembalikan kombinasi yang valid saja
def process_combination(combination, kebutuhan_kalori_harian, kebutuhan_protein_harian, kebutuhan_lemak_harian, kebutuhan_karbohidrat_harian, toleransi):
    if is_within_tolerance(combination, kebutuhan_kalori_harian, kebutuhan_protein_harian, kebutuhan_lemak_harian, kebutuhan_karbohidrat_harian, toleransi):
        total_kalori, total_protein, total_lemak, total_karbohidrat = total_nutrisi(combination)
        return combination, (total_kalori, total_protein, total_lemak, total_karbohidrat)
    return None

# Program utama
if __name__ == '__main__':
    # menerima masukan pengguna
    weight = float(input("Masukan berat badan dalam kg: "))
    height = float(input("Masukan tinggi badan dalam cm: "))
    age = int(input("Masukan umur dalam tahun: "))
    gender = input("Masukan jenis kelamin (male/female): ")
    activity_level = input("Masukan tingkat aktivitas (sedentary, lightly active, moderately active, very active, extra active): ")

    start = timeit.default_timer()

    # Menghitung AKG
    kebutuhan_kalori_harian = calculate_daily_calories(weight, height, age, gender, activity_level)
    kebutuhan_protein_harian, kebutuhan_lemak_harian, kebutuhan_karbohidrat_harian = calculate_macro_requirements(kebutuhan_kalori_harian)
    
    print("\nKebutuhan kalori harian: ", kebutuhan_kalori_harian)
    print("Kebutuhan protein harian: ", kebutuhan_protein_harian)
    print("Kebutuhan lemak harian: ", kebutuhan_lemak_harian)
    print("Kebutuhan karbohidrat harian: ", kebutuhan_karbohidrat_harian, "\n\n")
    
    kombinasi_valid = []

    # proses pemebentukan semua kombinasi dari dataset yang dimiliki menggunakan bantuan dari
    # multiprocessing untuk mempercepat proses pembuatan kombinasinya
    with Pool() as pool:
        for panjang_kombinasi in range(3, 5): #3-4 macam makanan dalam suatu kombinasi
            kombinasi = itertools.combinations(data_makanan, panjang_kombinasi)
            results = pool.starmap(process_combination, [(komb, kebutuhan_kalori_harian, kebutuhan_protein_harian, kebutuhan_lemak_harian, kebutuhan_karbohidrat_harian, toleransi) for komb in kombinasi])
            for result in filter(None, results):
                kombinasi_valid.append(result)
    
    stop = timeit.default_timer() 

    # Menampilkan hasil
    print("Kombinasi Makanan yang Memenuhi Syarat:")
    for kombinasi in kombinasi_valid:
        nama_makanan = [item["name"] for item in kombinasi[0]]
        print(", ".join(nama_makanan))
        print(f"Total Kalori: {kombinasi[1][0]}, Protein: {kombinasi[1][1]} g, Lemak: {kombinasi[1][2]} g, Karbohidrat: {kombinasi[1][3]} g\n")
    
    # Menyimpan hasil dalam file
    with open('hasil_kombinasi_makanan_tes_case_2.txt', 'w') as outfile:
        outfile.write("Kombinasi Makanan yang Memenuhi Syarat:\n")
        for kombinasi in kombinasi_valid:
            nama_makanan = [item["name"] for item in kombinasi[0]]
            outfile.write(f"Kombinasi: {', '.join(nama_makanan)}\n")
            outfile.write(f"Total Kalori: {kombinasi[1][0]}, Protein: {kombinasi[1][1]} g, Lemak: {kombinasi[1][2]} g, Karbohidrat: {kombinasi[1][3]} g\n\n")
            
    print("\n\nHasil kombinasi juga dituliskan pada file hasil_kombinasi_makanan_tes_case_2.txt")
    print("\n\nLama waktu eksekusi: ", stop-start, "s")
    