import pandas as pd
from matplotlib import pyplot as plt
import analysis

plt.style.use('seaborn-whitegrid')
params = {'text.usetex' : True,
          'font.size' : 11,
          'font.family' : 'Times New Roman',
          'xtick.labelsize': 10,
          'ytick.labelsize': 10
          }
plt.rcParams.update(params)

#import warnings
#swarnings.filterwarnings("ignore")

dados = analysis.leituraDados(['pr', 'sc', 'rs'], [2015, 2016, 2017, 2018, 2019])
dados = analysis.filtraDados(dados, 1500)
medida = 'mean'

indicadores = ['ind_pos', 'per_asc_sat', 'per_asc_alt', 'raz_asc_sil', 'per_hsil']
titulos = ['IP', '\% ASC/SAT', '\% ASC/ALT', 'Razão ASC/SIL', '\% HSIL']
baselines = [[3], [5], [60], [3], [0.4], [5]]
marcadores = ['v', '^', 'o']
legendas = {
    'sc': 'SC (Santa Catarina)',
    'pr': 'PR (Paraná)',
    'rs': 'RS (Rio Grande do Sul)',
}

fig = plt.figure()
for i in range(len(indicadores)):
    if i == 4:
        ax = plt.subplot2grid((3, 4), (2, 1), colspan = 2)
    else:
        ax = fig.add_subplot(3, 2, i + 1)
    ax.set_title(titulos[i])
    d = dados.groupby(['ano', 'estado'], as_index = False).agg({indicadores[i]: medida})
    estados = d['estado'].unique()
    anos = d['ano'].unique()
    c = 0
    for estado in estados:
        ax.plot(d[d['estado'] == estado]['ano'], d[d['estado'] == estado][indicadores[i]], label = legendas[estado] , marker = marcadores[c], linestyle = '-', markersize = 7 if c == 2 else 7.5)
        c += 1
    for value in baselines[i]:
        lim = ax.get_ylim()
        if value > lim[0] and value < lim[1]:
            ax.axhline(y = value, linewidth = 1.3, color = 'r', linestyle = '--')
    ax.set_xticks(anos)
    #ax.legend()
    ax.grid(False)
    ax.yaxis.grid(linestyle = ':', color = 'black')
    if i in [1, 3]:
        ax.yaxis.tick_right()

fig.set_size_inches(6.7, 8)
fig.subplots_adjust(left = 0.03)
fig.subplots_adjust(right = 0.962)
fig.subplots_adjust(top = 0.948)
fig.subplots_adjust(bottom = 0.098)
fig.subplots_adjust(hspace = 0.329)
fig.subplots_adjust(wspace = 0.02)

handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc = 'lower center', ncol = 3)
#plt.show()
#plt.savefig('plot-evolution-indices.pdf', format = 'pdf', dpi = 1000)
plt.savefig('plot-evolution-indices.png', format = 'png', dpi = 1000)
