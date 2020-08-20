
import re
import numpy as np
import pandas as pd

from tika import parser
import textract


def get_geds(path,pdf_files):
    geds_month = pd.DataFrame()
    for pdf_file in pdf_files:
        
        # text = textract.process(f"{path}{pdf_file}").decode("utf-8")
        text = parser.from_file(path + pdf_file)['content']
        
        grati_s    = ' Gratificação Especial de Desempenho '
        ged_s      = ' GED '
        mat_s      = '\nMat \d'
        decision_s = 'Decisão '
        
        grat_positions = [(x.start()) for x in re.finditer(grati_s, text)]

        if grat_positions == []:
            df_geds = empty_df(pdf_file)
            print(pdf_file, 'nao possui GEDs - Grat')

            
        else:
            break_positions = [(x.start()) for x in re.finditer('\n', text)]

            mat_positions = [(x.start()) for x in re.finditer(mat_s, text)]
            decision_positions = [(x.end()) for x in re.finditer(decision_s, text)]
            
            if mat_positions == []:
                df_geds = empty_df(pdf_file)
                print(pdf_file, 'nao possui GEDs - Mat')
                

            else:
                print(pdf_file)
                grat_min = min(grat_positions)
                mat_max  = max(mat_positions)


                start   = break_positions[sum(np.array(break_positions) < grat_min)-1]
                
                if sum(np.array(decision_positions) < mat_max) == len(decision_positions):
                    end = mat_max
                else:
                    end = decision_positions[sum(np.array(decision_positions) < mat_max)]

                ged_lines = text[start:end].split('\n')
                ged_lines = [line for line in ged_lines if line !='']
                
                
                geds_list = []

                for i in range(len(ged_lines)):
                    if re.search(grati_s, ged_lines[i]) != None:
                        geds_list.append(ged_lines[i])
                    elif re.search('Mat ', ged_lines[i]) != None:
                        if i<len(ged_lines)-1:
                            if (re.search('Mat ', ged_lines[i+1]) == None) and (re.search('Decisão', ged_lines[i+1]) == None):
                                geds_list.append(ged_lines[i]+ ' ' + ged_lines[i+1])
                            else:
                                geds_list.append(ged_lines[i])
                        else:
                            geds_list.append(ged_lines[i])
                    elif re.search(' GED ', ged_lines[i]) != None:
                        geds_list.append(ged_lines[i])

                df_geds = pd.DataFrame()
                for line in geds_list:

                    row              = pd.DataFrame([pdf_file.split('.')[0]], columns=['data'])

                    if re.search(grati_s, line) != None:
                        tipo = line.split(',')[0]
                    else:
                        splited_line = line.split(',')
                        
                        if len(splited_line)<2:
                            pass
                        else:
                            matricula = splited_line[0]
                            nome = splited_line[1]

                            if len(splited_line)<3:
                                ged = 0
                            else:
                                ged = splited_line[2]


                        row['tipo']      = tipo
                        row['matricula'] = matricula
                        row['nome']      = nome
                        row['ged']       = ged

                    df_geds = pd.concat([df_geds,row],0)
        df_geds.to_csv('../data/generic/pdf/ass/geds_raw.csv', index=False, mode='a', header=False)
            
        geds_month =  pd.concat([geds_month,df_geds],0)
    
    return geds_month



def empty_df(file):
    df_geds              = pd.DataFrame([file.split('.')[0]], columns=['data'])

    df_geds['tipo']      = np.nan
    df_geds['matricula'] = np.nan
    df_geds['nome']      = np.nan
    df_geds['ged']       = np.nan
    
    return df_geds