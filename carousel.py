import discord
from discord import Interaction
from discord.ui import Button, View
from utils import *


class Carousel(View):
    def __init__(self, items):
        super().__init__()
        self.items = items
        self.current_index = 0

    @discord.ui.button(emoji="⬅️")
    async def button_left(self, interaction: Interaction, button: Button):
        self.current_index = (self.current_index - 1) % len(self.items)
        self.items[self.current_index].set_footer(
            text=f"{self.current_index + 1}/{len(self.items)}")
        await interaction.response.edit_message(embed=self.items[self.current_index])

    @discord.ui.button(emoji="➡️")
    async def button_right(self, interaction: Interaction, button: Button):
        self.current_index = (self.current_index + 1) % len(self.items)
        self.items[self.current_index].set_footer(
            text=f"{self.current_index + 1}/{len(self.items)}")
        await interaction.response.edit_message(embed=self.items[self.current_index])


class Game(View):
    def __init__(self,  players, selected_player, ball):
        super().__init__()
        self.players = players
        self.selected_player = selected_player
        self.ball = ball

    @discord.ui.button(emoji="⬅️")
    async def button_left(self, interaction: Interaction, button: Button):

        self.selected_player.move_left()
        self.ball.move_left()
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="➡️")
    async def button_right(self, interaction: Interaction, button: Button):
        self.selected_player.move_right()
        self.ball.move_right()
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="⬆️")
    async def button_up(self, interaction: Interaction, button: Button):
        self.selected_player.move_up()
        self.ball.move_up()

        superposer_images(img_result, field, (self.players))

        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="⬇️")
    async def button_down(self, interaction: Interaction, button: Button):
        self.selected_player.move_down()
        self.ball.move_down()
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(label="Shoot ⚽", style=discord.ButtonStyle.primary, row=2)
    async def button_shoot(self, interaction: Interaction, button: Button):
        random_x = random.randint(240, 440)

        put_ball(img_result,  (random_x, 14))
        pixels = get_pixels_on_line(self.ball.position, (random_x, 14))
        intercepted = False
        for i in pixels:
            if closest_player(self.players, i) != self.selected_player and closest_player(self.players, i).position in get_pixels_on_circle(i, 15):
                print("intercepted by : ", closest_player(self.players, i).name)
                intercepted = True
                break
        if (intercepted == False):
            print("GOAL !")
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(label="Pass ⚽", style=discord.ButtonStyle.green, row=2)
    async def button_pass(self, interaction: Interaction, button: Button):
        self.selected_player = closest_player(
            self.players, self.selected_player.position)
        superposer_images(img_result, field, (self.players))
        self.ball.position = (
            self.selected_player.position[0]-13, self.selected_player.position[1]+15)
        put_ball(
            img_result, self.ball.position)

        await interaction.response.edit_message(attachments=[discord.File(img_result)])
