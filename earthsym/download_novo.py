import os
import zipfile
import cdsapi

# ==========================================
# 1. PARÂMETROS DE ENTRADA (Altere aqui)
# ==========================================
MODELO = "taiesm1"
VARIAVEL = "surface_temperature"
OUTPUT_DIR = "/dados4/pesquisa/meteoromuri/earthsym/"

# ==========================================
# 2. CONFIGURAÇÕES FIXAS
# ==========================================
DATASET = "projections-cmip6"
CENARIOS = ["ssp1_2_6", "ssp2_4_5", "ssp5_8_5"]

MESES = [f"{m:02d}" for m in range(1, 13)]
ANOS = [str(y) for y in range(2015, 2101)]

client = cdsapi.Client()

# ==========================================
# 3. LOOP DE DOWNLOAD E EXTRAÇÃO
# ==========================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

for cenario in CENARIOS:
    print(f"\n--- Processando Cenário: {cenario.upper()} ---")

    # Monta a requisição dinamicamente
    request = {
        "temporal_resolution": "monthly",
        "experiment": cenario,
        "variable": VARIAVEL,
        "model": MODELO,
        "month": MESES,
        "year": ANOS,
    }

    # Define o nome do arquivo .zip
    zip_path = os.path.join(
        OUTPUT_DIR, f"{VARIAVEL}_{MODELO}_{cenario}.zip"
    )

    try:
        print(f"Baixando dados para {MODELO} ({cenario})...")
        client.retrieve(DATASET, request).download(zip_path)

        print("Extraindo arquivos NetCDF...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(OUTPUT_DIR)

        # Remove o arquivo .zip para economizar espaço
        os.remove(zip_path)
        print(f"Sucesso para o cenário {cenario}!")

    except Exception as e:
        print(f"Erro ao processar {cenario}: {e}")

print("\n Processo finalizado para todos os cenários!")
