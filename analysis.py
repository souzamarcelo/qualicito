import pandas as pd

def leituraDados(estados, anos, filtroExames, limitesClasses):
    # Leitura e cálculos
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
    
    # Filtro
    dados = dados[dados['ex_total'] >= filtroExames]
    
    # Classes para labs
    dados['classe'] = dados['ex_total'].map(lambda x: 'pouco' if x < limitesClasses[0] else 'razoavel' if x < limitesClasses[1] else 'bom' if x < limitesClasses[2] else 'ideal')

    # Identificador para labs
    listaLabs = list(dados['lab_desc'].unique())
    dados['lab'] = dados['lab_desc'].map(lambda x: listaLabs.index(x) + 1)
    dados = dados.reset_index()
    
    # Remove inf
    dados.loc[dados['sil_total'] == 0, 'raz_asc_sil'] = float('NaN')

    return dados


def quantidadeLaboratorios(dados):
    d = dados
    d['ano'] = d['ano'].map(lambda x: str(x))
    d = d.groupby(['estado', 'classe', 'ano']).agg({'lab': 'count'})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    totais = d.groupby(['estado']).agg({'2015': 'sum', '2016': 'sum', '2017': 'sum', '2018': 'sum', '2019': 'sum', 'classe': lambda x: 'TOTAL'})
    totais.reset_index(inplace = True)
    d = d.append(totais)
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
    d.classe = pd.Categorical(d.classe, categories = ['pouco', 'razoavel', 'bom', 'ideal', 'TOTAL'], ordered = True)
    d.sort_values(['estado', 'classe'], inplace = True, ignore_index = True)

    for estado in d['estado'].unique():
        for ano in [2015, 2016, 2017, 2018, 2019]:
            total = d[(d['estado'] == estado) & (d['classe'] != 'TOTAL')][str(ano)].sum()
            for classe in d['classe'].unique():
                value = float(d[(d['estado'] == estado) & (d['classe'] == classe)][str(ano)])
                d.loc[(d['estado'] == estado) & (d['classe'] == classe), str(ano)] = str(int(value)) + ' (' + str(round(value / total * 100, 1)) + '%)'

    return d


def quantidadeExames(dados):
    d = dados
    d['ano'] = d['ano'].map(lambda x: str(x))
    d = d.groupby(['estado', 'classe', 'ano']).agg({'ex_total': 'sum'})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
    d.classe = pd.Categorical(d.classe, categories = ['pouco', 'razoavel', 'bom', 'ideal'], ordered = True)
    d.sort_values(['estado', 'classe'], inplace = True, ignore_index = True)
    d['total'] = d['2015'] + d['2016'] + d['2017'] + d['2018'] + d['2019']
    d = d.append(d.sum(numeric_only = True), ignore_index = True)
    d.iloc[-1, d.columns.get_loc('estado')] = 'total'
    d.iloc[-1, d.columns.get_loc('classe')] = '-'
    return d


def tabelaIndicador(dados, indicador, medida):
    d = dados[['lab', 'ano', 'estado', 'classe', indicador]]
    d = d.groupby(['estado', 'classe', 'ano']).agg({indicador: medida})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
    d.classe = pd.Categorical(d.classe, categories = ['pouco', 'razoavel', 'bom', 'ideal'], ordered = True)
    d.sort_values(['estado', 'classe'], inplace = True, ignore_index = True)
    return d




# Rotinas de teste
estados = ['rs', 'sc', 'pr']
anos = [2015, 2016, 2017, 2018, 2019]
m = 1500
v = [5000, 10000, 15000] #v1, v2, v3
dados = leituraDados(estados, anos, m, v)
#print(tabelaIndicador(dados, 'per_asc_alt', 'mean'))
#print(tabelaIndicador(dados, 'ind_pos', 'mean'))