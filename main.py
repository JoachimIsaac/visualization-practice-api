import string
from fastapi import FastAPI, Request, status
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
# print(dict_db)
# for obj in dict_db:
#     print(dict_db[obj])


db.insert(dict_db)
# shutil.copyfile('db.json', 'backup_db.json')
# print(dict_db["S1"]["M1"]["T1"])


# print(db_json)


    



def get_dates_up_to_end_date(dates,end_date):

    end_index = 0

    for index, date in enumerate(dates):

        if(date == end_date):
            end_index = index

    result = dates[0:end_index+1] 

    return result


def get_all_target_values(slo,measure,target_type):

    target_values = []

    target_obj = dict_db[slo][measure][target_type]

    for date in target_obj:
       target_value = target_obj[date]["target"]

       target_values.append(target_value)

    return target_values



def get_all_percentage_met_values(slo,measure,target_type):
    percentage_met_values = []

    target_obj = dict_db[slo][measure][target_type]

    for date in target_obj:

       percentage_met_value = target_obj[date]["percentage"]

       percentage_met_values.append(percentage_met_value)

    return percentage_met_values


def get_most_recent_target_description(slo, measure, target_type):

    most_recent_target_description = ""

    target_obj = dict_db[slo][measure][target_type]

    dates = []

    if(len(target_obj) != 0):
        for date in target_obj:
            dates.append(date)

        dates.sort(key=lambda date: int(date[0:2]))

        most_recent_target_date = dates[len(dates)-1]

        most_recent_target_description = dict_db[slo][measure][target_type][most_recent_target_date]["description"]


    return most_recent_target_description


def create_plot_title_multi_target(slo,measure):

    slo_description = dict_db[slo]["description"]
    get_measure_description = dict_db[slo][measure]["description"]

    title = f"{slo}{measure} T1 & T2 \n {slo_description} & {get_measure_description}"

    return title



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
    print(targets)
    for target in targets:
        
        current_dates = dict_db[slo][measure][target]
        # print(current_dates)
        for date in current_dates:
            if(len(date) == 5):
                dates.add(date)

    dates = list(dates)
    # print(dates)
    dates.sort(key=lambda date: int(date[0:2]))
    

    return dates


#choose remainder of dates 
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






@app.get("/plot")
async def get_plot_data(slo:str,measure:str,start_date:str,end_date:str):

    slo = slo.upper()
    measure = measure.upper()
    dates_from_start = await get_all_measure_dates_after_start(slo,measure,start_date)

    dates_from_start_to_end = get_dates_up_to_end_date(dates_from_start, end_date)

    #if there are missing dates/percentage/met we have to/fill in the data with fillers like 0, in the correct places.
    t1_values = get_all_target_values(slo, measure,"T1")
    
    percentages_met_t1 = get_all_percentage_met_values(
        slo, measure, "T1")
    

    most_recent_t1_description = get_most_recent_target_description(
        slo, measure, "T1")

    most_recent_t2_description =  get_most_recent_target_description(
        slo, measure, "T2") if has_two_targets(slo, measure) else []

    percentages_met_t2 = get_all_percentage_met_values(
        slo, measure, "T2") if has_two_targets(slo, measure) else []

    t2_values = get_all_target_values(
        slo, measure, "T2") if has_two_targets(slo, measure) else []

    title = create_plot_title_multi_target(slo, measure)

    plot_data = {
        "title":title,
        "dates": dates_from_start_to_end,
        "T1": t1_values,
        "T2":t2_values,
        "percentagesMetT1":percentages_met_t1,
        "percentagesMetT2":percentages_met_t2,
        "mostRecentT1Des": most_recent_t1_description,
        "mostRecentT2Des": most_recent_t2_description
    }

    return plot_data
    

@app.get("/input/options/{slo}/{measure}/{date}")
async def get_state(slo:str,measure:str,date:str):

    states = []
    slo = slo.upper()
    measure = measure.upper()

    
    if date in dict_db[slo][measure]["T1"]:
        states.append("Edit T1")
    else:
        states.append("Add T1")


    if "T2" in dict_db[slo][measure]:
        if date in dict_db[slo][measure]["T2"]:
            states.append("Edit T2")
        else:
            states.append("Add T2")

    return states


@app.post("/input/{slo}/{measure}/{target}/{date}")
async def add_new_slo_data(slo,measure,date,target,information:Request):

    data = await information.json()

    #would need to check if the date that was passed in is valid also 

    print(type(data))
    #If there is no date we add it, if a date already exists taht means we need to edit it
    if(date not in dict_db[slo][measure][target]):
        
        dict_db[slo][measure][target][date] = data

        with open("db.json", "r+") as f:
            f.truncate(0)
            f.close()

        db.insert(dict_db)

        return {
            "status":"SUCCESS the data was stored",
            "data":data
        }

    else:

        return{
            "status": "FAILDED the data was not stored, Data on this date is already there",
            "data": data
        }




@app.put("/edit/{slo}/{measure}/{target}/{date}")
async def edit_slo_data(slo, measure, date, target, information: Request):
    slo = slo.upper()
    measure = measure.upper()
    
    data = await information.json()

    #would need to check if the date that was passed in is valid also

    if(date in dict_db[slo][measure][target]):#if a date is there we can edit it , not date would mean we add

        dict_db[slo][measure][target][date] = data

        with open("db.json", "r+") as f:
            f.truncate(0)
            f.close()

        db.insert(dict_db)

        return {
            "status": "SUCCESS the data was edited",
            "data": data
        }

    else:

        return{
            "status": "FAILDED the entry for that date doesn't exist ",
            "data": data

        }


@app.get("/target/T2/exist/{slo}/{measure}")
def has_two_targets(slo:str,measure:str):

    slo = slo.upper()
    measure = measure.upper()

    if("T2" in dict_db[slo][measure]):
        
        return True

    else:

        return False

