<svg width="128px" height="128px" viewBox="0 0 50.8 50.8" xml:space="preserve"><path d="M7.859 29.266a14.947 14.947 0 0 1 5.864-16.112 14.947 14.947 0 0 1 17.147 0 14.947 14.947 0 0 1 5.865 16.112m-8.266 0h14.129m-37.298 0h4.487m.003 5.594h8.943m15.398 0h2.514m5.3 0h2.514m-31.771 5.594h23.757m-9.294-5.594h1.844M9.79 29.266a2.797 2.797 0 0 1 2.797 2.798A2.797 2.797 0 0 1 9.79 34.86m8.943 0a2.797 2.797 0 0 1 2.798 2.798 2.797 2.797 0 0 1-2.798 2.797m8.418 0a2.797 2.797 0 0 1-2.422-1.398 2.797 2.797 0 0 1 0-2.797 2.797 2.797 0 0 1 2.422-1.4" style="opacity:1;fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:3.175;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:0;stroke-dasharray:none;stroke-opacity:1" /><path d="M28.47 34.86a2.797 2.797 0 0 1-2.422-1.398 2.797 2.797 0 0 1 0-2.797 2.797 2.797 0 0 1 2.423-1.399" style="opacity:1;fill:none;fill-rule:evenodd;stroke:#000000;stroke-width:3.175;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:0;stroke-dasharray:none;stroke-opacity:1" /></svg>

# Open Weather Reference

OpenWeather book enables users to fetch real-time temperature data for any city worldwide via the OpenWeather API.

OpenWeather provides comprehensive weather data services, including current, forecast, and historical weather information. Explore a wide range of APIs for solar radiation, road risk assessment, solar energy prediction, and more, with global coverage and user-friendly access. Ideal for developers and businesses seeking accurate and reliable weather insights.

1. [Connectivity](#connectivity)
   1. [Connect using API Key](#connect-using-api-key)
2. [Configuration](#configuration)
3. [Procedures](#procedures)
   1. [to get the (current temperature) at a city](#to-get-the-(current-temperature)-at-a-city)

## Connectivity

This books supports the connectivity methods described in this section.In here you will find information about what information is required in order to employ each method.

### Connect using API Key

Authenticate to Open Weather API using the specified API key. You can obtain you own API key by visiting

| Label   | Description                           | Type   |
| ------- | ------------------------------------- | ------ |
| API Key | The API key to be used for connecting | `text` |

## Configuration

The following table details all the available configuration options for this book.

| Concept   | Description                                             | Type     | Default Value |
| --------- | ------------------------------------------------------- | -------- | ------------- |
| `timeout` | Timeout in seconds when making API calls to OpenWeather | `number` | 30            |

Configuration can be set or retrieved as shown in the following examples:

```generic
the department's Open Weather's timeout is 30
```

## Procedures

### to get the (current temperature) at a city

***

Fetch the current temperature for a specified city.

#### Input Concepts

| Concept | Description                                                                                                                                         | Type   | Required | Default Value |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------- | ------------- |
| `city`  | The name of the city. Please refer to ISO 3166 for the state codes or country codes.                                                                | `noun` | Yes      |               |
| `unit`  | Unit of measurement. standard, metric and imperial units are available. If you do not specify the units, standard units will be applied by default. | `noun` | No       | standard      |

#### Output Concepts

| Concept               | Description                                                                                | Type     |
| --------------------- | ------------------------------------------------------------------------------------------ | -------- |
| `current temperature` | The current temperature in the specified units of measurement, or None if an error occurs. | `number` |

#### Examples

Retrieve the current temperature at London

```generic
get the current temperature at London
```

Retrieve the current temperature at London in Celsius

```generic
get the current temperature at Buenos Aires with
    the unit is metric
```