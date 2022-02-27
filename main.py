import string
from fastapi import FastAPI
from tinydb import TinyDB,Query,where
import shutil
import json
import pprint
#make sure I add a way to encypt the database
app = FastAPI()
db = TinyDB('db.json')
backup_db = TinyDB('backup_db.json')
slo = Query()

dict_db = dict(db.all()[0])

# dict_db["S20"] = "It worked!!"
# # print(dict_db)
# # for obj in dict_db:
# #     print(dict_db[obj])

# with open("db.json","r+") as f:
#     f.truncate(0)
#     f.close()


# db.insert(dict_db)
# shutil.copyfile('db.json', 'backup_db.json')



# print(db_json)


@app.get("/slo/all")
async def get_all_slo():
    all_slo = [slo for slo in dict_db]
    return all_slo



@app.get("/measure/{slo}")
async def get_measures(slo):
    slo = slo.upper()
    measures = [measure for measure in dict_db[slo]]
    return measures



@app.get("/dates/{slo}/{measure}")
async def get_all_measure_dates(slo,measure):
    dates = set()
    slo = slo.upper()
    measure = measure.upper()
    targets = dict_db[slo][measure]
   
    for target in targets:

        current_dates = dict_db[slo][measure][target]

        for date in current_dates:
            dates.add(date)
    dates = list(dates)
    dates = sorted(dates, key=lambda date: int(date[0].split("-")[0]))
    # print(dates)
    return dates


#choose remainer of dates 
@app.get("/startdate/{slo}/{measure}")
async def get_all_measure_dates_after_start(slo:str, measure:str, start: str ):

    dates = await get_all_measure_dates(slo, measure)
    start_index = 0
    results = []

    for index, d in enumerate(dates):

        if d == start:
            start_index = index

    
    results = dates[start_index:len(dates)]

    return results 
    

@app.get("/targets/{slo}/{measure}")
async def get_all_targets(slo:str,measure:str):
    targets = []
    slo = slo.upper()
    measure = measure.upper()
    targets_objs = dict_db[slo][measure]

    for target in targets_objs:
        targets.append(target)

    

    return targets


