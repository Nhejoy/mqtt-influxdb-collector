# MQTT to InfluxDB Listener for ChirpStack

This project is a Python service that subscribes to an MQTT topic from a **ChirpStack LoRaWAN Network Server**, processes incoming uplink messages, and stores relevant metrics in **InfluxDB** for monitoring and analysis.

---

## Overview

The script connects to an MQTT broker, listens for uplink messages published by ChirpStack, decodes the payload, extracts radio and device metadata, and writes the processed data into an InfluxDB bucket.

The service runs continuously and automatically reconnects if the MQTT connection is lost.

---

## Features

- MQTT subscription using **paho-mqtt**
- Compatible with **ChirpStack MQTT integration**
- Base64 payload decoding
- Extraction of device and radio metrics
- Storage of time-series data in **InfluxDB 2.x**
- Configuration via environment variables
- Automatic reconnection handling

---

## Data Processing

For each received uplink message:

1. The JSON payload is parsed.
2. The first gateway reception (`rxInfo[0]`) is used.
3. The `data` field is Base64-decoded and converted to hexadecimal.
4. Application-specific values are extracted:
   - `data`: First two bytes of the payload
   - `state`: Last byte of the payload
5. A measurement named `romosa` is written to InfluxDB with:
   - **Tag**: `devEui`
   - **Fields**: `fcnt`, `rssi`, `snr`, `data`, `state`

---

## Technologies Used

- Python 3
- Paho MQTT Client
- InfluxDB Python Client (2.x)
- ChirpStack LoRaWAN
- dotenv

---

## Configuration

Create a `.env` file in the project root with the following variables:

```env
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=chirpstack/application/+/device/+/event/up

INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_token_here
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=your_bucket
