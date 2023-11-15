import pandas as pd

br = pd.read_csv("./database/aerodromospublicosv1.csv", sep=';')
brazilian_airports = br["CÓDIGO OACI"].tolist()

airport_acronym = "SBGR"

df = pd.read_csv("./database/VRA_2023_01.csv", sep=';')

isOrigin = df['Sigla ICAO Aeroporto Origem'] == airport_acronym
isDest = df['Sigla ICAO Aeroporto Destino'] == airport_acronym

hasLadingData = ~pd.isna(df['Partida Prevista'])
hasTakeOffData = ~pd.isna(df['Chegada Prevista'])

mask = (isOrigin | isDest) & hasLadingData & hasTakeOffData 

df = df[mask] 

df = df[df['Sigla ICAO Aeroporto Origem'].isin(brazilian_airports)]
df = df[df['Sigla ICAO Aeroporto Destino'].isin(brazilian_airports)]

dados = {
    'origin': df['Sigla ICAO Aeroporto Origem'],
    'destination': df['Sigla ICAO Aeroporto Destino'],
    'landing_data': df['Chegada Prevista'],
    'takeoff_data': df['Chegada Prevista']
}

data_frame = pd.DataFrame(data = dados)
print(len(data_frame))
data_frame.to_csv('{}.csv'.format(airport_acronym), index=False)

