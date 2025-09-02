from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json
import httpx

def is_valid_date(s: str):
    try: 
        requested_date = datetime.fromisoformat(s.replace("Z", "+00:00"))
        date_now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)        
        return (date_now <= requested_date)
    except:
        return False


districts_locations = {}
with open("districts_islands-locations_ids.json", mode="r", encoding="utf-8") as json_file:
    districts_locations = json.load(json_file)

weather_types = {}
with open("weather-type-classe.json", mode="r", encoding="utf-8") as json_file:
    weather_types = json.load(json_file)

def get_weather_type(id: int):
    for t in weather_types["data"]:
        if(t["idWeatherType"] == id):
            return t["descWeatherTypePT"]
    return "n/a"






app = FastAPI()

@app.get("/")
def foo(request: Request):
    return { "root": "dummy" }


@app.get("/weather-forecast/{iso_date}/{district}/{location}")
async def weather_forecast(request: Request, iso_date: str, district: str, location: str):
    """
    Get the forecast for a pair [district/island]-location on a specified date. 
    If data is available, returns the expected minimum temperature, maximum temperature, and a description of the weather in PT, all for the specified date.
    Keep in mind that IPMA does not provide forecast data for dates too far into the future. 9 days in advance seems to be the limit.
    """
    if(not is_valid_date(iso_date)):
        raise HTTPException(status_code=400, detail="Invalid date.")
    if(district not in districts_locations):
        raise HTTPException(status_code=404, detail="No such district or island.")
    if(location not in districts_locations[district]):
        raise HTTPException(status_code=404, detail="No such location for district/island provided.")
    
    
    aggregate_id = districts_locations[district][location]
    aggregate_endpoint = f"https://api.ipma.pt/public-data/forecast/aggregate/{aggregate_id}.json"

    async with httpx.AsyncClient() as client:
        res = await client.get(aggregate_endpoint, timeout=10)
        if(res.status_code == 200):
            data = res.json()
            requested_date = datetime.fromisoformat(iso_date)
            for element in data:
                element_date = datetime.fromisoformat(element["dataPrev"])
                print(element["dataPrev"])
                # match the date, but also need to have the tMax:tMin data (which always come in pairs) and signal the average forecast for the day
                if(element_date == requested_date and "tMax" in element):
                    return { 
                        "tMax" : element["tMax"],
                        "tMin" : element["tMin"],
                        "weatherType": get_weather_type(element["idTipoTempo"])
                    }
        else:
            raise HTTPException(status_code=res.status_code, detail="IPMA API failed.")

    raise HTTPException(status_code=404, detail="No forecast available for the date provided.")
