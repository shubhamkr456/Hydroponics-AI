from relay import turn_on, turn_off
from light_sensor import is_dark


def control(
    mode,
    hour,
    minute,
    start_hour,
    start_minute,
    end_hour,
    end_minute
):

    # -----------------------------
    # AUTO MODE
    # -----------------------------
    if mode == "AUTO":

        current = hour * 60 + minute
        start = start_hour * 60 + start_minute
        end = end_hour * 60 + end_minute

        if start <= current < end:


#
            if is_dark():

                turn_on()

                return True

            else:

                turn_off()

                return False

        else:

            turn_off()

            return False

    # -----------------------------
    # MANUAL MODE
    # -----------------------------
    return None
