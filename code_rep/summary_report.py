# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 15:34:06 2021

@author: ENLCK
"""
import io
import pandas as pd
import seaborn as sns
import base64
from io import BytesIO
from matplotlib import pyplot as plt
from IPython.core.display import HTML
import os


cwd = os.getcwd() 


def build_visualization(df, col_name, folder='images', viz_type = "BOXPLOT"):
    if not os.path.exists(folder):
        os.mkdir(folder)
    img_folder=os.path.join(cwd,folder)
    
    fig, ax = plt.subplots(1,1, figsize = (5,2))
    sns.set_theme(style = 'whitegrid')
    
    if viz_type == "BOXPLOT":
        ax = sns.boxplot(x = df[col_name])
        file_name = col_name+'box_plot.png'
    
    elif viz_type == "BAR GRAPH":
        ax = df[col_name].value_counts().plot(kind='bar')
        file_name = col_name+'bar_graph.png'
    
    elif viz_type == "LINE GRAPH":
        ax = df[col_name].value_counts().plot(kind='line')
        file_name = col_name+'line_graph.png'
        
    plt.savefig(os.path.join(img_folder,file_name))
    plt.close()
    return fig
    



    
def build_metadata_source(source_dict = None):
    dataList = [] #empty list
    for d in source_dict:
        df = source_dict[d]['summary_table']
        
        for index, row in df.iterrows(): 
                mylist = [row.SRC_DF, row.COL_NAME]
                dataList.append(mylist)
    return dataList
    

def build_summary_tables(df, df_name=None, geo=False, metadata = None):
    buffer = io.StringIO()
    ### generate the basic information summary for the dataframe - printing the results to the buffer
    df.info(buf=buffer)
    num_cols = len(df.columns.tolist())
    #### gets the dataframe info
    s = buffer.getvalue()
    n = 0
    
    indx = []
    col_names = []
    num_vals = []
    obj_type = []    
    is_GIS = False
    is_GIS_indx = []
    is_GIS_ex_col_types = []
    is_GIS_in_col_types = []
    ex_col_names = []
    
    for i in s.split("\n"):
        if n <=4 or n > num_cols+4:
            pass
        
        else:
            details = i.split()
            indx.append(details[0])
            col_names.append(details[1])
            num_vals.append(details[2])
            
            if details[4] == 'geometry':
                ### geometry datasets cause exception errors within the describe dataframe function
                ### these columns need to be excluded from the function call - with the data to be summarized in
                ### a different way
                
                obj_type.append(details[4])
                
                is_GIS = True
                is_GIS_indx.append(details[0])
                is_GIS_ex_col_types.append(details[4])
                ex_col_names.append(details[1])
            
            elif details[4] == 'datetime64[ns,' and details[-1] =='America/Los_Angeles]':
                ### datetime with timezone datasets cause exception errors within the describe dataframe function
                obj_type.append("""datetime64[ns,', 'America/Los_Angeles]""")
                
            elif details[4] == 'datetime64[ns,' and details[-1] !='America/Los_Angeles]':
                ### datetime with timezone datasets cause exception errors within the describe dataframe function
                obj_type.append(f"""datetime64[ns,', '{details[-1]}""")
                
            elif details[4] == 'datetime64[ns,' and 'datetime64' not in is_GIS_in_col_types:
                    is_GIS_in_col_types.append('datetime64')
                
            else:    
                obj_type.append(details[4])
                
                if details[4] not in is_GIS_in_col_types:
                    is_GIS_in_col_types.append(details[4])
                
              
        n+=1

    ### gets the dataframe description 
    if is_GIS == True:
        exclude_cols = is_GIS_ex_col_types
        include_cols = is_GIS_in_col_types
        
        
    else:
        exclude_cols = None
        include_cols = 'all'
    
    df_desc = df.describe(include = include_cols, exclude = exclude_cols, datetime_is_numeric=True )
    df_count = []
    df_unique = []
    df_mean = []
    df_min = []
    df_max = []
    df_std = []
    df_top = []
    
    n = 0
    
    for c in col_names:
        #print(df_desc[c])
        if is_GIS == True and c in ex_col_names:
            df_count.append(num_vals[n])
            df_unique.append(num_vals[n])
            df_mean.append(None)
            df_min.append(None)
            df_max.append(None)
            df_std.append(None)
            df_top.append(None)
        else:
            try:
                df_count.append(df_desc[c][0])
                df_unique.append(df_desc[c][1])
                df_mean.append(df_desc[c][4])
                df_min.append(df_desc[c][6])
                df_max.append(df_desc[c][10])
                df_std.append(df_desc[c][5])
                df_top.append(df_desc[c][2])
            except:
                df_count.append(num_vals[n])
                df_unique.append(num_vals[n])
                df_mean.append(None)
                df_min.append(None)
                df_max.append(None)
                df_std.append(None)
                df_top.append(None)
                
        
        n+=1
    
    
    
    src_df = [df_name for _ in range(num_cols)]
    result = pd.DataFrame(list(zip(src_df, indx, col_names, num_vals, obj_type, \
                                   df_count, df_unique, df_mean, df_min, df_max, df_std, df_top  )),
                          columns = ["SRC_DF",'IDX',"COL_NAME","NUM_VALUES","DATA_TYPE", \
                                     "COUNT", "UNIQUE", "MEAN", "MIN", "MAX", "STD" ,"TOP"   ]
                          )
    
    if metadata.empty == False:
        updated_result = pd.merge(result, metadata, how = 'left', left_on = ['SRC_DF','COL_NAME'], right_on = ['df_name', 'col_name'])
        updated_result.drop(columns = ['df_name', 'col_name'], inplace = True)

        updated_result = updated_result[[ "SRC_DF",'IDX',"COL_NAME","NUM_VALUES","DATA_TYPE", 'DESCRIPTION', "COUNT", "UNIQUE", 
                                         "MEAN", "MIN", "MAX", "STD" ,"TOP" , 'PK_IND','SK_IND','FILTER_IND',
                                         'ANALYSIS_IND','CALCULATED_IND','SUMMARY_VIS_TYPE']]

        return updated_result
        
    else:
        return result

    
