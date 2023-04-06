from PIL import Image


image_dessus = "C:\\Users\\d\\dev\\projects\\gacha_blue_lock\\img\\bachira_suit_pc.png"
image_fond = "C:\\Users\\d\\dev\\projects\\gacha_blue_lock\\img\\field.png"


def superposer_images(image_fond, image_dessus, position=(0, 0)):
    img_fond = Image.open(image_fond).convert("RGBA")

    img_dessus = Image.open(image_dessus).convert("RGBA").resize((50, 50))
    img_fond.paste(img_dessus, position, img_dessus)
    img_fond.save("image_resultante.png")


# Coordonnées (x, y) où vous souhaitez placer l'image du dessus
# position = (0, 0)
# img_after = "C:\\Users\\d\\dev\\projects\\gacha_blue_lock\\image_resultante.png"
# img_after_convert = Image.open(img_after).convert("RGBA")
superposer_images(image_fond, image_dessus, (0, 0))
# superposer_images(img_after_convert, image_dessus, (50, 50))
# superposer_images(img_after_convert, image_dessus, (100, 100))
