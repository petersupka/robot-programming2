from microbit import sleep, pin14, pin15

sum_ticks_dict = {"right": {"sum_ticks": 0, "previous_pos": 0}, "left": {"sum_ticks": 0, "previous_pos": 0}}

def left_sum_ticks():
    surova_data_leva = pin14.read_digital()
    if sum_ticks_dict["left"]["previous_pos"] != surova_data_leva:
        sum_ticks_dict["left"]["sum_ticks"] += 1
        sum_ticks_dict["left"]["previous_pos"] = surova_data_leva
    return sum_ticks_dict["left"]["sum_ticks"]

def right_sum_ticks():
    surova_data_prava = pin15.read_digital()
    if sum_ticks_dict["right"]["previous_pos"] != surova_data_prava:
        sum_ticks_dict["right"]["sum_ticks"] += 1
        sum_ticks_dict["right"]["previous_pos"] = surova_data_prava
    return sum_ticks_dict["right"]["sum_ticks"]

if __name__ == "__main__":

    while True:
        print(left_sum_ticks(), right_sum_ticks())
        sleep(5)
