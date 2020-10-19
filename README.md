# home-automation

## Components

### LED Lighting

- jasper-client to recognize voice command and invoke server with color name
- python http server to take color name and adjust GPIO outputs to respective color, keep track of state/dimming, and apply effects

### Presence detection

- server queries bluetooth/wi-fi clients and keeps track of presence. triggers actions upon return/absence

https://gpiozero.readthedocs.io/en/stable/api_output.html#rgbled
https://gpiozero.readthedocs.io/en/stable/recipes.html#full-color-led
https://www.w3.org/TR/css-color-3/#svg-color
https://jasperproject.github.io/documentation/
