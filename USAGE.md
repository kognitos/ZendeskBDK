<img src="src/openweather/data/icon.svg" width="128" height="128">

# Open Weather Reference

OpenWeather book enables users to fetch real-time temperature data for any city worldwide via the OpenWeather API.

OpenWeather provides comprehensive weather data services, including current, forecast, and historical weather information. Explore a wide range of APIs for solar radiation, road risk assessment, solar energy prediction, and more, with global coverage and user-friendly access. Ideal for developers and businesses seeking accurate and reliable weather insights.

## to get the current temperature at a city

Fetch the current temperature for a specified city.

### Input Concepts

| Concept | Description | Required | Type       | Default Value |
| ------- | ----------- | -------- | ---------- | ------------- |
| city    | None        | Yes      | Conceptual | None          |
| units   | None        | No       | String     | standard      |

### Output Concepts

| Concept             | Description | Required | Type   | Default Value |
| ------------------- | ----------- | -------- | ------ | ------------- |
| current temperature | None        | No       | Number | None          |