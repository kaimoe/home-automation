# home-automation

## Components

### LED Lighting

- Two different http servers to control SMD5050 LED strip with certain colors, keep track of auto-dimming, etc:
  - Arduino (MKR series tested, all WiFiNINA-compatible boards should work) project
  - Python version intended to work on any Raspberry Pi board
- jasper-client to recognize voice command and invoke server with color name (abandoned)

### Presence detection

- Server queries bluetooth/wi-fi clients and keeps track of presence. triggers actions upon return/absence (planned)

