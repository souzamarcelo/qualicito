import pandas as pd
from matplotlib import pyplot as plt

def leituraDados(estados, anos, limitesClasses = [1500, 5000, 10000]):
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
    
    # Classes para labs
    dados['classe'] = dados['ex_total'].map(lambda x: 'pouco' if x < limitesClasses[0] else 'razoavel' if x < limitesClasses[1] else 'bom' if x < limitesClasses[2] else 'ideal')

    # Identificador para labs
    listaLabs = list(dados['lab_desc'].unique())
    dados['lab'] = dados['lab_desc'].map(lambda x: listaLabs.index(x) + 1)
    dados = dados.reset_index()
    
    # Remove inf
    dados.loc[dados['sil_total'] == 0, 'raz_asc_sil'] = float('NaN')

    return dados


def filtraDados(dados, filtroExames):
    return dados[dados['ex_total'] >= filtroExames]


def printLabsExames(dados):
    print('\t- Total de laboratórios: %d (RS: %d; SC: %d; PR: %d)' %
                    (len(dados['lab'].unique()),
                    len(dados[dados['estado'] == 'rs']['lab'].unique()),
                    len(dados[dados['estado'] == 'sc']['lab'].unique()),
                    len(dados[dados['estado'] == 'pr']['lab'].unique())))
    print('\t- Esses laboratórios fizeram um total de %d exames (RS: %d; SC: %d; PR: %d)' %
                    (dados['ex_total'].sum(),
                    dados[dados['estado'] == 'rs']['ex_total'].sum(),
                    dados[dados['estado'] == 'sc']['ex_total'].sum(),
                    dados[dados['estado'] == 'pr']['ex_total'].sum()))


def quantidadeLaboratorios(dados):
    d = dados
    d['ano'] = d['ano'].map(lambda x: str(x))
    d = d.groupby(['estado', 'ano']).agg({'lab': 'count'})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['pr', 'sc', 'rs'], ordered = True)
    d.sort_values('estado', inplace = True, ignore_index = True)
    d = d.append(d.sum(numeric_only = True), ignore_index = True)
    d.iloc[-1, d.columns.get_loc('estado')] = 'total'
    return d


def quantidadeExames(dados):
    d = dados
    d['ano'] = d['ano'].map(lambda x: str(x))
    d = d.groupby(['estado', 'ano']).agg({'ex_total': 'sum'})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['pr', 'sc', 'rs'], ordered = True)
    d.sort_values('estado', inplace = True, ignore_index = True)
    d['total'] = d['2015'] + d['2016'] + d['2017'] + d['2018'] + d['2019']
    d = d.append(d.sum(numeric_only = True), ignore_index = True)
    d.iloc[-1, d.columns.get_loc('estado')] = 'total'
    return d


def tabelaIndicadores(dados, medida):
    d = dados
    d['ano'] = d['ano'].map(lambda x: str(x))
    d = d.groupby(['estado', 'ano']).agg({'ind_pos': medida, 'per_asc_sat': medida, 'per_asc_alt': medida, 'raz_asc_sil': medida, 'per_hsil': medida, 'per_ins': medida})
    d = d.unstack('estado')
    d = d.T
    d.columns.name = ''
    d = d.reset_index()
    d = d.rename(columns={'level_0': 'indicador'})
    totais = {'indicador': []}
    for indicador in d['indicador'].unique():
        totais['indicador'].append(indicador)
        for ano in [2015, 2016, 2017, 2018, 2019]:
            if str(ano) not in totais: totais[str(ano)] = []
            totais[str(ano)].append(dados[dados['ano'] == str(ano)][str(indicador)].agg(medida))
    totais = pd.DataFrame.from_dict(totais)
    totais['estado'] = medida + '_sul'
    d = d.append(totais)
    d.estado = pd.Categorical(d.estado, categories = ['pr', 'sc', 'rs', medida + '_sul'], ordered = True)
    d.indicador = pd.Categorical(d.indicador, categories = ['ind_pos', 'per_asc_sat', 'per_asc_alt', 'raz_asc_sil', 'per_hsil', 'per_ins'], ordered = True)
    d.sort_values(['indicador', 'estado'], inplace = True, ignore_index = True)
    return d


def tabelaIndicadoresLaboratorios(dados):
    d = dados.copy()
    d['ano'] = d['ano'].map(lambda x: str(x))
    d['ind_pos'] = d['ind_pos'].map(lambda x: 'ad' if x >= 3 else 'in')
    d['per_asc_sat'] = d['per_asc_sat'].map(lambda x: 'ad' if x <= 5 else 'in')
    d['per_asc_alt'] = d['per_asc_alt'].map(lambda x: 'ad' if x < 60 else 'in')
    d['raz_asc_sil'] = d['raz_asc_sil'].map(lambda x: 'ad' if x <= 3 else 'in')
    d['per_hsil'] = d['per_hsil'].map(lambda x: 'ad' if x >= 0.4 else 'in')
    d['per_ins'] = d['per_ins'].map(lambda x: 'ad' if x < 5 else 'in')
    
    indicadores = ['ind_pos', 'per_asc_sat', 'per_asc_alt', 'raz_asc_sil', 'per_hsil', 'per_ins']
    d = d[['lab', 'ano', 'estado'] + indicadores]
    anos = d['ano'].unique()
    estados = d['estado'].unique()
    
    tabela = {'indicador': [], 'estado': [], 'situacao': []}
    for indicador in indicadores:
        for estado in estados:
            for situacao in ['ad', 'in']:
                tabela['indicador'].append(indicador)
                tabela['estado'].append(estado)
                tabela['situacao'].append('adequado' if situacao == 'ad' else 'inadequado')
                for ano in anos:
                    if ano not in tabela: tabela[ano] = []
                    tabela[ano].append(len(d[(d['estado'] == estado) & (d['ano'] == ano) & (d[indicador] == situacao)]))
                    
    d = pd.DataFrame.from_dict(tabela)
    d = d.groupby(['indicador', 'estado', 'situacao'], as_index = False).agg({'2015': 'sum', '2016': 'sum', '2017': 'sum', '2018': 'sum', '2019': 'sum'})
    
    for indicador in indicadores:
        for estado in estados:
            for ano in anos:
                d2 = d[(d['indicador'] == indicador) & (d['estado'] == estado)]
                total = d2[ano].sum()
                adequado = d2[d2['situacao'] == 'adequado'][ano].sum()
                inadequado = d2[d2['situacao'] == 'inadequado'][ano].sum()
                perAdequado = round(adequado * 100 / total, 0)
                perInadequado = 100 - perAdequado
                d.loc[(d['indicador'] == indicador) & (d['estado'] == estado) & (d['situacao'] == 'adequado'), ano] = str(adequado) + ' (' + str(int(perAdequado)) + '%)'
                d.loc[(d['indicador'] == indicador) & (d['estado'] == estado) & (d['situacao'] == 'inadequado'), ano] = str(inadequado) + ' (' + str(int(perInadequado)) + '%)'
    
    d.estado = pd.Categorical(d.estado, categories = ['pr', 'sc', 'rs'], ordered = True)
    d.indicador = pd.Categorical(d.indicador, categories = ['ind_pos', 'per_asc_sat', 'per_asc_alt', 'raz_asc_sil', 'per_hsil', 'per_ins'], ordered = True)
    d.sort_values(['indicador', 'estado'], inplace = True, ignore_index = True)
    return d
    

def tabelaIndicador(dados, indicador, medida):
    d = dados[['lab', 'ano', 'estado', 'classe', indicador]]
    d = d.groupby(['estado', 'classe', 'ano']).agg({indicador: medida})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['pr', 'sc', 'rs'], ordered = True)
    d.classe = pd.Categorical(d.classe, categories = ['pouco', 'razoavel', 'bom', 'ideal'], ordered = True)
    d.sort_values(['estado', 'classe'], inplace = True, ignore_index = True)
    return d


def plotIndicadores(dados, medida):
    plt.style.use('seaborn-whitegrid')
    indicadores = ['ind_pos', 'per_asc_sat', 'per_asc_alt', 'raz_asc_sil', 'per_hsil', 'per_ins']
    titulos = ['Índice de positividade', 'Percentual de ASC entre exames satisfatórios', 'Percentual de ASC entre exames alterados', 'Razão ASC/(LSIL + HSIL)', 'Percentual de HSIL entre exames satisfatórios', 'Percentual de exames insatisfatórios']
    baselines = [[2, 3, 10], [5], [60], [3], [0.4], [5]]

    fig = plt.figure()
    for i in range(len(indicadores)):
        ax = fig.add_subplot(3, 2, i + 1)
        ax.set_title(titulos[i])
        d = dados.groupby(['ano', 'estado'], as_index = False).agg({indicadores[i]: medida})
        estados = d['estado'].unique()
        anos = d['ano'].unique()
        c = 0
        for estado in estados:
            ax.plot(d[d['estado'] == estado]['ano'], d[d['estado'] == estado][indicadores[i]], label = estado.upper(), marker = 'o', linestyle = '-')
            c += 1
        for value in baselines[i]:
            lim = ax.get_ylim()
            if value > lim[0] and value < lim[1]:
                ax.axhline(y = value, linewidth = 1.3, color = 'r', linestyle = '--')
                ax.annotate(text = str(value), xy = (ax.get_xlim()[1], value), xycoords = 'data', xytext = (-2, 2), textcoords='offset points', fontsize = 10, color = 'r', horizontalalignment = 'right', verticalalignment = 'bottom')
        ax.set_xticks(anos)
        ax.legend()
    fig.set_size_inches(12, 10)
    fig.tight_layout()
    fig.subplots_adjust(hspace = 0.3)
    return plt


def plotCorrelacao(dados, indicador1, indicador2, baselines1, baselines2):
    plt.style.use('default')
    fig, ax = plt.subplots()
    d = dados
    colors = ['tab:blue', 'tab:orange', 'tab:green']
    estados = list(d['estado'].unique())

    for i in range(len(estados)):
        x = list(d[d['estado'] == estados[i]][indicador1])
        y = list(d[d['estado'] == estados[i]][indicador2])
        ax.scatter(x, y, c = colors[i], label = estados[i], alpha = 0.8, edgecolors = 'none')
        
    for value in baselines1:
        lim = ax.get_xlim()
        if value > lim[0] and value < lim[1]:
            ax.axvline(x = value, linewidth = 1.3, color = 'r', linestyle = '--')
            ax.annotate(text = str(value), xy = (value, ax.get_ylim()[1]), xycoords = 'data', xytext = (-2, -2), textcoords='offset points', fontsize = 10, color = 'r', horizontalalignment = 'right', verticalalignment = 'top')
    for value in baselines2:
        lim = ax.get_ylim()
        if value > lim[0] and value < lim[1]:
            ax.axhline(y = value, linewidth = 1.3, color = 'r', linestyle = '--')
            ax.annotate(text = str(value), xy = (ax.get_xlim()[1], value), xycoords = 'data', xytext = (-2, 2), textcoords='offset points', fontsize = 10, color = 'r', horizontalalignment = 'right', verticalalignment = 'bottom')

    ax.set_xlabel(indicador1)
    ax.set_ylabel(indicador2)
    ax.set_title('Correlação entre indicadores')
    ax.legend()
    ax.grid(False)
    return plt

# Rotinas de teste
#dados = leituraDados(['pr', 'sc', 'rs'], [2015, 2016, 2017, 2018, 2019])
#dados = filtraDados(dados, 1500)
#print(tabelaIndicadoresLaboratorios(dados))
