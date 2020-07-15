import pandas as pd

def readData(origem, anos):
    dados = None
    for ano in anos:
        dadosAno = pd.read_csv('dados-datasus/' + str(ano) + '-' + origem + '.csv', encoding='ISO-8859-1', sep = ';')
        dadosAno.columns = ['prestador', 'exames', 'ins_mat_acelular', 'ins_pres_sangue', 'ins_pres_piocitos', 'ins_pres_art_desec', 'ins_pres_cont_exte', 'ins_pres_sup_celul', 'ins_outros', 'asc_us', 'asc_h', 'lsil', 'hsil', 'exames_alterados']
        dadosAno['ano'] = ano
        dadosAno['exames_insatisfatorios'] = dadosAno['ins_mat_acelular'] + dadosAno['ins_pres_sangue'] + dadosAno['ins_pres_piocitos'] + dadosAno['ins_pres_art_desec'] + dadosAno['ins_pres_cont_exte'] + dadosAno['ins_pres_sup_celul'] + dadosAno['ins_outros']
        dadosAno['exames_satisfatorios'] = dadosAno['exames'] - dadosAno['exames_insatisfatorios']
        dadosAno['asc_total'] = dadosAno['asc_us'] + dadosAno['asc_h']
        dadosAno['sil_total'] = dadosAno['lsil'] + dadosAno['hsil']
        dadosAno = dadosAno[['prestador', 'ano', 'exames', 'exames_satisfatorios', 'exames_insatisfatorios', 'exames_alterados', 'asc_total', 'sil_total', 'hsil']]
        dadosAno['indice_positividade'] = dadosAno['exames_alterados'] / dadosAno['exames_satisfatorios'] * 100
        dadosAno['percentual_asc_sat'] = dadosAno['asc_total'] / dadosAno['exames_satisfatorios'] * 100
        dadosAno['percentual_asc_alt'] = dadosAno['asc_total'] / dadosAno['exames_alterados'] * 100
        dadosAno['razao_asc_sil'] = dadosAno['asc_total'] / dadosAno['sil_total']
        dadosAno['percentual_hsil'] = dadosAno['hsil'] / dadosAno['exames_satisfatorios'] * 100
        dadosAno['percentual_insatisfatorio'] = dadosAno['exames_insatisfatorios'] / dadosAno['exames'] * 100
        dadosAno = dadosAno[dadosAno['prestador'] != 'Total']
        dados = dadosAno if dadosAno is None else pd.concat([dados, dadosAno], ignore_index = True)
    return dados