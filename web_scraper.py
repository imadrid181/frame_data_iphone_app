import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pandas as pd

DATA_TABLES = ["DataTables_Table_0", "DataTables_Table_1", "DataTables_Table_2", "DataTables_Table_3", "DataTables_Table_4"]

"""Loads Dynamic portion of website and then return the source code."""
def parse(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    time.sleep(1)
    sourceCode = driver.page_source
    return sourceCode

def getTable(sourceCode, tableName):
    soup = BeautifulSoup(sourceCode, 'lxml')
    table = soup.find('table', id=tableName)
    return table

def tableToDataFrame(table):
    if table is None:
        raise TypeError("Table was not downloaded")
    
    header = []
    rows = []
    for i, row in enumerate(table.find_all('tr')):
        if i == 0:
            header = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])
          
    data = [inner[2:] for inner in rows[1:]]
    index = flatten_concatenation([inner[1:2] for inner in rows[1:]])
    
    tableDF = pd.DataFrame(data=data, index=index, columns=header[2:])
    return tableDF

def flatten_concatenation(array):
    flat_arr = []
    for row in array:
        flat_arr += row
    return flat_arr

def getFrameData(character):
    url = "https://www.dustloop.com/w/GBVSR/{character}/Frame_Data".format(character=character)
    sourceCode = parse(url)

    frameData_DF = None
    for table in DATA_TABLES:
        if frameData_DF is None:
            tempTable = getTable(sourceCode, table)
            frameData_DF = tableToDataFrame(tempTable)
        else:
            tempTable = getTable(sourceCode, table)
            tempDF = tableToDataFrame(tempTable)
            frameData_DF = pd.concat([frameData_DF, tempDF], axis=0)
        
    return frameData_DF
        
fr = getFrameData('Eustace')
print(pd.DataFrame.to_json(fr))