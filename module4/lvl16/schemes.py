from pydantic import BaseModel, ConfigDict, Field

class PlaceIn(BaseModel):
    name: str
    
class PlaceOut(BaseModel):
    name: str
    latitude: float
    longitude: float
    
    
class WeatherIn(BaseModel):
    name: str
    latitude: float
    longitude: float


class WeatherOut(BaseModel):
    temperature: float = Field(validation_alias="temperature_2m")
    wind_speed: float = Field(validation_alias="wind_speed_10m")
    
    
class Country(BaseModel):
    name: str
    capital: str | None
    currency: str | None
    emoji: str
    
    
class Rate(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    code: str = Field(validation_alias="cc")
    name: str = Field(validation_alias="txt")
    rate: float
    date: str = Field(validation_alias="exchangedate")


class Trip(BaseModel):
    country: Country
    weather: WeatherOut | None
    rate: Rate | None
