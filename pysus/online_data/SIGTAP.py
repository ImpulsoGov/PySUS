# ftp.retrbinary("RETR " + file ,open("pub/sistemas/tup/downloads/" + file, 'wb').write)
import pandas as pd
import urllib.request
import io
from zipfile import ZipFile
from ftplib import FTP


def getfullfilename(year: int, month: int):
    TabelaUnificada = 'TabelaUnificada_{}{}'.format(year,month)
    ftp = FTP("ftp2.datasus.gov.br")
    ftp.login()
    ftp.cwd("pub/sistemas/tup/downloads/")
    filenames = ftp.nlst()
    result = list(filter(lambda x: x.startswith(TabelaUnificada), filenames))
    ftp.close()
    return result[0]

def download(file: str, year: int, month: int, cache: bool=True) -> object:
    TabelaUnificadaName = getfullfilename(year, month)
    mysock = urllib.request.urlopen('ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/' + TabelaUnificadaName)
    memfile = io.BytesIO(mysock.read())
    with ZipFile(memfile, 'r') as myzip:
        f = myzip.open(file + '.txt')
        col = myzip.open(file + '_layout.txt')
        colunas, content = col.read(), f.read()
    colunas, content = colunas.decode("unicode_escape"), content.decode("unicode_escape")
    dfcol = (pd.DataFrame([x.split(',') for x in colunas.split('\r\n')]))
    dfcol = dfcol.rename(columns=dfcol.iloc[0]).drop([0]).dropna()

    df = (pd.DataFrame([x.split('\r\n') for x in content.split('\r\n')]))
    FinalDF = pd.DataFrame(columns=dfcol['Coluna'].tolist())
    
    # TEM QUE MELHORAR AQUI
    for i in dfcol.index:
        inicio = int(dfcol.loc[i]['Inicio'])
        fim = int(dfcol.loc[i]['Fim'])
        row = []
        for s in range(len(df)):
            row.append(df.loc[s][0][inicio-1:fim])
        FinalDF[dfcol.loc[i]['Coluna']] = row
    return FinalDF
