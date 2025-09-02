# ggpoker_brasil-challenge-IPMA

This is a small API built for the "Desafui Prático - API de Previsão de Tempo (IPMA)" using Python with FastAPI.

## Installation
This project needs the following things:
- Python 3 with pip and venv
- FastAPI with uvicorn and gunicorn
  
### Python & pip Installation
Python installation is relatively straight forward. On Windows we can download it from [here](https://www.python.org/downloads/).  
On a debian-like system like Ubuntu, Mint and Kali we can install it using a packet manager such as APT:
```console
sudo apt install update
sudo apt install python3
```
pip should come installed by default with Python.

### venv set-up
venv is used as a way to manage local dependencies without too many headaches.  
cd into the root directory of this repo then run:
```console
python -m venv venv
```
The second "venv" is the name of our virtual environment and will be the name of the newly created directory responsible for managing the environment.  
Run the venv activation script in order to activate our virtual environment, which is platform dependent.  
On Windows (specially newer versions) prefer to use the one for PowerShell:
```console
.\venv\Scripts\Activate.ps1
```  
On Linux use whichever matches your Shell. Example with bash:
```console
source /venv/bin/activate
```  

Finally, with venv activated, install the project's dependencies by running this from the root directory:
```console
pip install -r requirements.txt
```  


## Running the API
With venv **activated**, we can run the API locally with uvicorn like so:
```console
uvicorn app.main:app
```  
On a production environment:
```console
gunicorn main:app --timeout 10000 --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

There's also a Dockerfile which we can build from:
```console
docker build -t weather-forecast-IPMA .
docker run -p 8000:8000 weather-forecast-IPMA
```  
Either way the application should now be accessible on localhost:8000.

## The weather-forecast endpoint
As a proof of concept, there is one single endpoint `/weather-forecast` which fetches three pieces of data for the client-side: *Maximum Temperature*, *Minimimum Temperature*, and *Weather Type*.  

Every request is expected to be a `GET` with three query parameters like this:
```
/weather-forecast/{iso_date}/{district}/{location}
```
| Query Param   | Description   |
| ------------- | ------------- |
| `iso_date` | A date in the ISO 8601 format. E.g. `2025-09-02` for the 2nd of September of 2025 |
| `district` | Either a district, or an island. E.g. `Aveiro`, `Évora`, `Faial`, `Flores` |
| `location` | A city/village of the district/island. E.g. `Ovar`, `Arraiolos`, `Horta`, `Santa Cruz das Flores` |

On every successful (Status 200) request, the response body will be like this:
```JSON
{
    "tMax": "string",
    "tMin": "string",
    "weatherType": "string"
}
```
Where `tMax` is the Maximum Temperature forecasted for a certain day, `tMin` the minimum, and `weatherType` a short description of the weather in general (in Portuguese).   

> One could easily fetch more data such as UV ray incidence (`iUV`) or the chance of rain (`probabilidadePrecipita`), but since we do not have a good way of speculating the scope of this kind of project, I've opted to maintain it small and simple.

Since this project only concerns with the fetching of *forecast* data, it's not possible to fetch the history of previous forecasts. On top of that, due to how weather forecast models work, one can only fetch data up to a certain point in the future. In the case of the IPMA, we have fairly consistent data in the span of 10 days including the present day that.  

For instance, as of the writing of this README, one can fetch data for the forecast of Ovar in Aveiro in the 2nd of September of 2025 by sending a GET request to the endpoint like this:
```
curl http://localhost:8000/weather-forecast/2025-09-02/Aveiro/Ovar
```

This request returns the following data content:
```JSON
{
    "tMax": "22.9",
    "tMin": "15.2",
    "weatherType": "Céu parcialmente nublado"
}
```

If we try to fetch data for the same district+location but from the *past* (2025-09-01), we get an HTTP Status 400 and an error body:
```JSON
{
    "detail": "Invalid date."
}
```
Some other error messages have been implemented for the following cases:
- `district` value not in the list of districts of the IPMA: "No such district or island."
- `location` value not in IPMA's list or does not correspond with the district: "No such location for district/island provided."
- `iso_date` value not in the data fetched from IPMA: "No forecast available for the date provided."
- In the case that it fails on the request to IPMA's API: "IPMA API failed."