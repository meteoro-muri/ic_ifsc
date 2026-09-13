import requests

url = "https://raw.githubusercontent.com/matheusf30/operacional_dengue/refs/heads/main/dados_operacao/tmax_diario_2025.csv"
resp = requests.get(url)
with open("myfile.csv", "w") as f:
    f.write(resp.text)

print(f)
