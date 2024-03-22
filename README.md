# Scuffed-reflow-oven
A project of a scuffed refolw oven

## NOTE: DO AT YOUR OWN RISK!!!
## Schematics

### Overview
    (UNI-T UT61E)-----SERIAL----(PC)----Serial----(RPi Pico)----(SolidState Relais)----(Oven Mains)

### RPi Pico - SSR

             (VSYS)-----
                       .
                       .
                       (+)
                       (SSR)
                       (-)
                       .
                       .
                       (C)
    (RPi Pico GP22)----(B)
                       (E)
                       .
                       .
                       (GND)
