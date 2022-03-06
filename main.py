import string
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tinydb import TinyDB,Query,where
import shutil
import json
import pprint


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#make sure I add a way to encypt the database

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


@app.get("/slo/description/{slo}")
async def get_slo_descritpion(slo):
    slo = slo.upper()
    slo_description = dict_db[slo]["description"]
    return slo_description



@app.get("/measure/{slo}")
async def get_measure(slo):
    slo = slo.upper()
    measures = [measure for measure in dict_db[slo]]
    return measures


@app.get("/measure/description/{slo}/{measure}")
async def get_measure_description(slo, measure):
    slo = slo.upper()
    measure = measure.upper()

    measure_description = dict_db[slo][measure]["description"]

    return measure_description



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

    dates.sort(key=lambda date: int(date[0:2]))
    

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


@app.get("/result/{slo}/{measure}/{target}")
def get_result_summary(slo:str,measure:str,target:str,date:str):
    slo = slo.upper()
    measure = measure.upper()
    target = target.upper()
    
    result_summary = dict_db[slo][measure][target][date]["description"]
    return result_summary


