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
    
    # Identificador para labs
    listaLabs = list(dados['lab_desc'].unique())
    dados['lab'] = dados['lab_desc'].map(lambda x: listaLabs.index(x) + 1)
    dados = dados.reset_index()

    # Classes para labs
    listaLabs = list(dados['lab'].unique())
    for lab in listaLabs:
        minExames = dados[dados['lab'] == lab]['ex_total'].min()
        dados.loc[dados['lab'] == lab, 'classe'] = 'pouco' if minExames < limitesClasses[0] else 'razoavel' if minExames < limitesClasses[1] else 'bom' if minExames < limitesClasses[2] else 'ideal'

    return dados


def laboratoriosEstadoClasse(dados):
    d = dados[dados['ano'] == 2019].groupby(['estado', 'classe']).agg({'lab': 'count'})
    d = d.unstack('classe')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
    d.sort_values('estado', inplace = True, ignore_index = True)
    d = d[['estado', 'pouco', 'razoavel', 'bom', 'ideal']]
    d['total'] = d['pouco'] + d['razoavel'] + d['bom'] + d['ideal']
    return d


def examesEstadoClasseAno(dados):
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


estados = ['rs', 'sc', 'pr']
anos = [2015, 2016, 2017, 2018, 2019]
m = 1500
v = [5000, 10000, 15000] #v1, v2, v3
dados = leituraDados(estados, anos, m, v)