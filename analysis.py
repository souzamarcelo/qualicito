import pandas as pd

def leituraDados(estados, anos, filtroExames):
    dados = None
    for ano in anos:
        for estado in estados:
            alt = pd.read_csv('dados-datasus/' + str(ano) + '-' + estado + '-alterados.csv', encoding='ISO-8859-1', sep = ';')
            adeq = pd.read_csv('dados-datasus/' + str(ano) + '-' + estado + '-adequabilidade.csv', encoding='ISO-8859-1', sep = ';')
            alt = alt[['Prestador de serviço', ' ASC-US', ' ASC-H', 'Les IE Baixo Grau', 'Les IEp Alto Grau', 'Exames Alterados']]
            alt.columns = ['lab_desc', 'asc_us', 'asc_h', 'lsil', 'hsil', 'ex_alt']
            adeq.columns = ['lab_desc', 'ex_rej', 'ex_sat', 'ex_ins', 'ex_total']
            dadosAnoEstado = pd.merge(alt, adeq, on = 'lab_desc')
            dadosAnoEstado = dadosAnoEstado[dadosAnoEstado['lab_desc'] != 'Total']
            dadosAnoEstado['ano'] = ano
            dadosAnoEstado['estado'] = estado
            dadosAnoEstado['asc_total'] = dadosAnoEstado['asc_us'] + dadosAnoEstado['asc_h']
            dadosAnoEstado['sil_total'] = dadosAnoEstado['lsil'] + dadosAnoEstado['hsil']
            dadosAnoEstado['ind_pos'] = dadosAnoEstado['ex_alt'] / dadosAnoEstado['ex_sat'] * 100
            dadosAnoEstado['per_asc_sat'] = dadosAnoEstado['asc_total'] / dadosAnoEstado['ex_sat'] * 100
            dadosAnoEstado['per_asc_alt'] = dadosAnoEstado['asc_total'] / dadosAnoEstado['ex_alt'] * 100
            dadosAnoEstado['raz_asc_sil'] = dadosAnoEstado['asc_total'] / dadosAnoEstado['sil_total']
            dadosAnoEstado['per_hsil'] = dadosAnoEstado['hsil'] / dadosAnoEstado['ex_sat'] * 100
            dadosAnoEstado['per_ins'] = dadosAnoEstado['ex_ins'] / dadosAnoEstado['ex_total'] * 100
            dados = pd.concat([dados, dadosAnoEstado], ignore_index = True)
    labsRemover = list(dados[dados['ex_total'] < filtroExames]['lab_desc'].unique())
    for lab in dados['lab_desc'].unique():
        if len(dados[dados['lab_desc'] == lab]) < len(anos):
            labsRemover.append(lab)
    dados = dados[~dados['lab_desc'].isin(labsRemover)]
    listLabs = list(dados['lab_desc'].unique())
    dados['lab'] = dados['lab_desc'].map(lambda x: listLabs.index(x) + 1)
    dados = dados.reset_index()
    return dados