import pandas as pd

# Leer el archivo Excel
df = pd.read_excel('salarios.xlsx')

# Mostrar las primeras filas
print(df.head())