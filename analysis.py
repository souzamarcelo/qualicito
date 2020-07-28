import pandas as pd
from matplotlib import pyplot as plt

def leituraDados(estados, anos, filtroExames, limitesClasses = [1500, 5000, 10000]):
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
    d = d.groupby(['estado', 'ano']).agg({'lab': 'count'})
    d = d.unstack('ano')
    d.columns = d.columns.droplevel()
    d.columns.name = ''
    d.reset_index(inplace = True)
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
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
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
    d.sort_values('estado', inplace = True, ignore_index = True)
    d['total'] = d['2015'] + d['2016'] + d['2017'] + d['2018'] + d['2019']
    d = d.append(d.sum(numeric_only = True), ignore_index = True)
    d.iloc[-1, d.columns.get_loc('estado')] = 'total'
    return d


def tabelaIndicadores(dados, medida):
    d = dados
    d['ano'] = d['ano'].map(lambda x: str(x))
    d = d.groupby(['estado', 'ano']).agg({'ind_pos': medida, 'per_asc_sat': medida,'per_asc_alt': medida, 'raz_asc_sil': medida, 'per_hsil': medida, 'per_ins': medida})
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
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr', medida + '_sul'], ordered = True)
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
    d.estado = pd.Categorical(d.estado, categories = ['rs', 'sc', 'pr'], ordered = True)
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
                ax.annotate(s = str(value), xy = (ax.get_xlim()[1], value), xycoords = 'data', xytext = (-2, 2), textcoords='offset points', fontsize = 10, color = 'r', horizontalalignment = 'right', verticalalignment = 'bottom')
        ax.set_xticks(anos)
        ax.legend()
    fig.set_size_inches(12, 10)
    fig.tight_layout()
    fig.subplots_adjust(hspace = 0.3)
    return plt


def plotCorrelacao(dados, indicador1, indicador2, baselines1, baselines2):
    plt.style.use('default')
    fig, ax = plt.subplots()
    #d = dados[dados['ano'] == 2019]
    d = dados
    d.reset_index(inplace = True)
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
            ax.annotate(s = str(value), xy = (value, ax.get_ylim()[1]), xycoords = 'data', xytext = (-2, -2), textcoords='offset points', fontsize = 10, color = 'r', horizontalalignment = 'right', verticalalignment = 'top')
    for value in baselines2:
        lim = ax.get_ylim()
        if value > lim[0] and value < lim[1]:
            ax.axhline(y = value, linewidth = 1.3, color = 'r', linestyle = '--')
            ax.annotate(s = str(value), xy = (ax.get_xlim()[1], value), xycoords = 'data', xytext = (-2, 2), textcoords='offset points', fontsize = 10, color = 'r', horizontalalignment = 'right', verticalalignment = 'bottom')

    ax.set_xlabel(indicador1)
    ax.set_ylabel(indicador2)
    ax.set_title('Correlação entre indicadores')
    ax.legend()
    ax.grid(False)
    return plt

# Rotinas de teste
dados = leituraDados(['rs', 'sc', 'pr'], [2015, 2016, 2017, 2018, 2019], 1500)
#plotCorrelacao(dados, 'ind_pos', 'per_asc_alt', [2, 3, 10], [60]).show()