from PIL import Image
from utils import Player


emoji = "img\\bachira_icon.png"
field = "img\\field.png"
img_result = "image_resultante.png"
emoji_rin = "img\\itoshi-r_icon.png"
red_circle = "img\\red_circle.png"


def clear_field(field, img_result):
    img_fond = Image.open(field).convert("RGBA")
    img_fond.save(img_result)


def superposer_images(img_result,  field, players):
    clear_field(field, img_result)
    img_fond = Image.open(img_result).convert("RGBA")
    emoji_size = 10
    for i in players:
        emoji_paste = Image.open(i.emoji).convert(
            "RGBA").resize((emoji_size, emoji_size))
        position_to_substract = (int(emoji_size/2), int(emoji_size/2))

        final_position = (i.position[0] - position_to_substract[0],
                          i.position[1] - position_to_substract[1])

        img_fond.paste(emoji_paste, final_position, emoji_paste)
        img_fond.save(img_result)


bachira = Player("Bachira", (23, 51), emoji)
rin = Player("Rin", (23, 873), emoji_rin)
red_circle = Player("red_circle", (1, 1), red_circle)
tuple = (rin, bachira, red_circle)
superposer_images(img_result, field, tuple)
print("done")
# superposer_images(img_result, field, tuple)
# tuple[0].move_down()
# tuple[0].move_down()
# superposer_images(img_result, field, tuple)

# field = "https://i.imgur.com/tLxY7fc.png"


# print(bachira.position)
# bachira.move_down()
# print(bachira.position)

# Coordonnées (x, y) où vous souhaitez placer l'image du dessus
# position = (0, 0)
# img_after = "C:\\Users\\d\\dev\\projects\\gacha_blue_lock\\image_resultante.png"
# img_after_convert = Image.open(img_after).convert("RGBA")
# superposer_images(image_fond, image_dessus, (0, 0))
# superposer_images(img_result, image_dessus, (23, 51))
# superposer_images(img_result, image_dessus, (23, 873))
# superposer_images(img_result, image_dessus, (640, 51))
# superposer_images(img_result, image_dessus, (640, 873))
# superposer_images(img_result, emoji, field,
#                   ((23, 51), (23, 873), (640, 51), (640, 873)))


def deplacer_joueur(position, img_result, emoji, field):
    superposer_images(img_result, emoji, field, position)
# superposer_images(img_after_convert, image_dessus, (50, 50))
# superposer_images(img_after_convert, image_dessus, (100, 100))
