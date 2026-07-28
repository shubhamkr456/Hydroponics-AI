from machine import Pin, ADC
import dht
import time

# ==========================================
# SENSOR CONFIGURATION
# ==========================================

# --- TDS Sensor Config ---
TDS_PIN = 34
VREF = 3.3
ADC_RES = 4095.0
SCOUNT = 30

NUM_POINTS = 6
CAL_VOLTAGES = [0.05, 0.51, 0.82, 1.29, 1.41, 1.73]
CAL_TDS = [67, 267.0, 426.0, 542.0, 720.0, 870]

# --- Ultrasonic Config ---
TRIG_PIN = 5
ECHO_PIN = 18

# --- LDR Config ---
LDR_PIN = 35
MIN_RAW = 0
MAX_RAW = 2600

# --- DHT22 Config ---
DHT_PIN = 23

# ==========================================
# SENSOR INITIALIZATION
# ==========================================

# TDS
tds_sensor = ADC(Pin(TDS_PIN))
tds_sensor.atten(ADC.ATTN_11DB)
tds_sensor.width(ADC.WIDTH_12BIT)

# Ultrasonic
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# LDR
ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

# DHT22
dht_sensor = dht.DHT22(Pin(DHT_PIN))

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_median_num(data_list):
    sorted_data = sorted(data_list)
    length = len(sorted_data)

    if length % 2 != 0:
        return sorted_data[length // 2]
    else:
        return (sorted_data[length // 2] +
                sorted_data[length // 2 - 1]) / 2.0


def interpolate_tds(voltage):

    if voltage <= CAL_VOLTAGES[0]:
        return CAL_TDS[0] * (voltage / CAL_VOLTAGES[0])

    if voltage >= CAL_VOLTAGES[-1]:
        slope = (
            (CAL_TDS[-1] - CAL_TDS[-2]) /
            (CAL_VOLTAGES[-1] - CAL_VOLTAGES[-2])
        )
        return CAL_TDS[-1] + slope * (voltage - CAL_VOLTAGES[-1])

    for i in range(NUM_POINTS - 1):
        if CAL_VOLTAGES[i] <= voltage <= CAL_VOLTAGES[i + 1]:

            slope = (
                (CAL_TDS[i + 1] - CAL_TDS[i]) /
                (CAL_VOLTAGES[i + 1] - CAL_VOLTAGES[i])
            )

            return CAL_TDS[i] + slope * (
                voltage - CAL_VOLTAGES[i]
            )

    return 0.0


# ==========================================
# SENSOR FUNCTIONS
# ==========================================

def read_tds_sensor():

    analog_buffer = []

    for _ in range(SCOUNT):
        analog_buffer.append(tds_sensor.read())
        time.sleep_ms(2)

    average_raw_adc = get_median_num(analog_buffer)

    analog_voltage = (
        average_raw_adc / ADC_RES
    ) * VREF

    temperature = 25.0

    comp_coeff = 1.0 + 0.02 * (
        temperature - 25.0
    )

    comp_voltage = analog_voltage / comp_coeff

    tds_value = interpolate_tds(comp_voltage)

    return int(tds_value), analog_voltage


def get_distance():

    trig.value(0)
    time.sleep_us(2)

    trig.value(1)
    time.sleep_us(10)

    trig.value(0)

    while echo.value() == 0:
        pulse_start = time.time_ns()

    while echo.value() == 1:
        pulse_end = time.time_ns()

    pulse_duration = (pulse_end - pulse_start) / 1e9

    distance = (pulse_duration * 34300) / 2

    return distance


def map_value(x, in_min, in_max, out_min, out_max):

    x = max(in_min, min(x, in_max))

    return int(
        (x - in_min) *
        (out_max - out_min) /
        (in_max - in_min)
        + out_min
    )


def read_ldr_sensor():

    raw_value = ldr.read()

    light_percentage = map_value(
        raw_value,
        MIN_RAW,
        MAX_RAW,
        0,
        100
    )

    return raw_value, light_percentage


def read_dht_sensor():

    try:
        dht_sensor.measure()
        return (
            dht_sensor.temperature(),
            dht_sensor.humidity()
        )

    except OSError:
        return None, None


# ==========================================
# MASTER FUNCTION
# ==========================================

def read_all():

    ppm, tds_voltage = read_tds_sensor()

    distance = get_distance()

    ldr_raw, light_pct = read_ldr_sensor()

    temp, humidity = read_dht_sensor()

    return {
        "temperature": temp,
        "humidity": humidity,
        "tds": ppm,
        "tds_voltage": round(tds_voltage, 3),
        "reservoir_distance_cm": round(distance, 2),
        "ldr_raw": ldr_raw,
        "light_percentage": light_pct
    }