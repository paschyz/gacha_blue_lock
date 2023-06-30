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
        self.ball.move_left(self.selected_player)
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="➡️")
    async def button_right(self, interaction: Interaction, button: Button):
        self.selected_player.move_right()
        self.ball.move_right(self.selected_player)
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="⬆️")
    async def button_up(self, interaction: Interaction, button: Button):
        self.selected_player.move_up()
        self.ball.move_up(self.selected_player)

        superposer_images(img_result, field, (self.players))

        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="⬇️")
    async def button_down(self, interaction: Interaction, button: Button):
        self.selected_player.move_down()
        self.ball.move_down(self.selected_player)
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(label="Shoot ⚽", style=discord.ButtonStyle.primary, row=2)
    async def button_shoot(self, interaction: Interaction, button: Button):
        random_x = random.randint(240, 440)

        put_ball(img_result,  (random_x, 14))
        pixels = get_pixels_on_line(self.ball.position, (random_x, 14))
        intercepted = False

        # Check each pixel on the line between the ball position and the target position
        for i in pixels:
            shifted_center = (closest_player(
                self.players, i).position[0]-17, closest_player(self.players, i).position[1]-17)

            # Check if the closest player (excluding the selected player) is within the circle of radius 50 around the pixel
            if closest_player(self.players, i) != self.selected_player and shifted_center in get_pixels_on_circle(i, 35):
                # Player intercepts the ball
                print("intercepted by: ", closest_player(self.players, i).name)
                print("ballon position: " + str(i))
                print("closest: " + str(closest_player(self.players, i).position))
                await interaction.channel.send(content="INTERCEPTION par " + closest_player(self.players, i).name + " !")
                intercepted = True
                break

        if intercepted == False:
            # Ball reaches the target position without interception (goal)
            await interaction.channel.send(content="GOAL !")

        # # Add code to make player hitbox appear
        # img_result_with_hitboxes = Image.open(img_result).convert("RGBA")
        # for player in self.players:
        #     hitbox_radius = 50 // 2
        #     hitbox_diameter = 50
        #     hitbox_img = Image.open(
        #         "img/red_circle.png").convert("RGBA").resize((hitbox_diameter, hitbox_diameter))
        #     player_hitbox_position = (
        #         player.position[0] - hitbox_radius, player.position[1] - hitbox_radius)
        #     img_result_with_hitboxes.paste(
        #         hitbox_img, player_hitbox_position, hitbox_img)
        # img_result_with_hitboxes.save(img_result)

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
