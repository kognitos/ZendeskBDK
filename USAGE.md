<img src="src/openweather/data/icon.svg" width="128" height="128">

# Open Weather Reference

OpenWeather book enables users to fetch real-time temperature data for any city worldwide via the OpenWeather API.

OpenWeather provides comprehensive weather data services, including current, forecast, and historical weather information. Explore a wide range of APIs for solar radiation, road risk assessment, solar energy prediction, and more, with global coverage and user-friendly access. Ideal for developers and businesses seeking accurate and reliable weather insights.

## to get the (current temperature) at a city

Fetch the current temperature for a specified city.

### Input Concepts

| Concept | Description                                                                                                                                         | Type   | Required | Default Value |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------- | ------------- |
| `city`  | The name of the city. Please refer to ISO 3166 for the state codes or country codes.                                                                | `noun` | Yes      |               |
| `unit`  | Unit of measurement. standard, metric and imperial units are available. If you do not specify the units, standard units will be applied by default. | `noun` | No       | standard      |

### Output Concepts

| Concept               | Description                                                                                | Type     |
| --------------------- | ------------------------------------------------------------------------------------------ | -------- |
| `current temperature` | The current temperature in the specified units of measurement, or None if an error occurs. | `number` |

### Examples

Retrieve the current temperature at London

```generic
get the current temperature at London
```

Retrieve the current temperature at London in Celsius

```generic
get the current temperature at Buenos Aires with
    the unit is metric
```