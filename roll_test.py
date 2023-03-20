import random


def get_random_float():
    return round(random.uniform(0.00, 100.00), 2)


def get_card_rarity():
    randFloat = get_random_float()
    if randFloat <= 0.5:  # 0.5%
        return "legendary"
    if randFloat <= 5.5:  # 5%
        return "epic"
    if randFloat <= 45.5:  # 40%
        return "rare"
    else:
        return "common"


print(get_card_rarity())
