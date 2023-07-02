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
    def __init__(self, players, selected_player, match, score_message, img_result, field):
        super().__init__()
        self.players = players
        self.selected_player = selected_player
        self.ball = Ball(
            (self.selected_player.position[0] - 13, self.selected_player.position[1] + 15), "img/ball.png")
        self.match = match
        self.score_message = score_message
        self.img_result = img_result
        self.field = field

    def reposition_players(self):
        for player in self.players:
            player.reposition()

    def start_game(self):
        self.ball.position = (
            self.selected_player.position[0] - 13, self.selected_player.position[1] + 15)
        superposer_images(self.img_result, self.field, self.players)
        put_ball(self.img_result, self.ball.position)

    def restart_game(self):
        clear_field(self.field, self.img_result)
        self.reposition_players()
        self.ball.position = (
            self.selected_player.position[0] - 13, self.selected_player.position[1] + 15)
        superposer_images(self.img_result, self.field, self.players)
        put_ball(self.img_result, self.ball.position)

    @discord.ui.button(emoji="⬅️")
    async def button_left(self, interaction: Interaction, button: Button):

        self.selected_player.move("left")
        self.ball.move("left", self.selected_player)
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="➡️")
    async def button_right(self, interaction: Interaction, button: Button):
        self.selected_player.move("right")
        self.ball.move("right", self.selected_player)
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="⬆️")
    async def button_up(self, interaction: Interaction, button: Button):
        self.selected_player.move("up")
        self.ball.move("up", self.selected_player)

        superposer_images(img_result, field, (self.players))

        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(emoji="⬇️")
    async def button_down(self, interaction: Interaction, button: Button):
        self.selected_player.move("down")
        self.ball.move("down", self.selected_player)
        superposer_images(img_result, field, (self.players))
        put_ball(img_result,  (self.ball.position))
        await interaction.response.edit_message(attachments=[discord.File(img_result)])

    @discord.ui.button(label="Shoot ⚽", style=discord.ButtonStyle.primary, row=2)
    async def button_shoot(self, interaction: Interaction, button: Button):
        random_x = random.randint(240, 440)

        pixels = get_pixels_on_line(self.ball.position, (random_x, 14))
        intercepted = False

        # Check each pixel on the line between the ball position and the target position
        for i in pixels:
            shifted_center = (closest_player(
                self.players, i).position[0]-17, closest_player(self.players, i).position[1]-17)
            closest_enemy_player = closest_player(self.players, i)
            # Check if the closest player (excluding the selected player) is within the circle of radius 50 around the pixel
            if closest_enemy_player != self.selected_player and closest_enemy_player.team.name != self.selected_player.team.name and shifted_center in get_pixels_on_circle(i, 35):

                await interaction.channel.send(content="INTERCEPTION par " + closest_enemy_player.name.upper() + f"({closest_enemy_player.team.name})" + " !")
                intercepted = True

                break

        if intercepted == False:
            # Ball reaches the target position without interception (goal)
            put_ball(self.img_result,  (random_x, 14))
            self.match.team_blue.goal()
            self.restart_game()
            # await self.score_message.edit(content=f"{self.match.team_blue.score}to{self.match.team_red.score}")
            await interaction.channel.send(content=f"GOAL by {self.selected_player.name.upper()} ! {self.match.team_blue.score} to {self.match.team_red.score}")

        await interaction.response.edit_message(attachments=[discord.File(self.img_result)])

    @discord.ui.button(label="Pass ⚽", style=discord.ButtonStyle.green, row=2)
    async def button_pass(self, interaction: Interaction, button: Button):
        self.selected_player = closest_ally_player(
            self.players, self.selected_player)
        superposer_images(img_result, field, (self.players))
        self.ball.position = (
            self.selected_player.position[0]-13, self.selected_player.position[1]+15)
        put_ball(
            img_result, self.ball.position)

        await interaction.response.edit_message(attachments=[discord.File(img_result)])
