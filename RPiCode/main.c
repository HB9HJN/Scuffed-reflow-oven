#include <stdio.h>
#include "pico/stdlib.h"

int main() {

    const uint led_pin = 22;
    char inp;
    stdio_init_all();

    gpio_init(led_pin);
    gpio_set_dir(led_pin, GPIO_OUT);
    while (true) {
        inp = getchar_timeout_us(0);

        if(inp == '1'){
            gpio_put(led_pin, 1);
            printf("ON");
        }else if(inp == '0'){
            gpio_put(led_pin, 0);
            printf("OFF");
        }
    }
}