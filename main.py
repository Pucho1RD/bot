import discord
import os
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask
from threading import Thread

# Configuración del servidor para que Render no duerma el bot
app = Flask('')
@app.route('/')
def home():
    return "El bot está activo 24/7"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Lógica del Bot ---
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ticket_idioma = {}

FAQ = {
    "es": {
        "login": "🔑 Si tienes problemas para iniciar sesión, puede que se te haya acabado la membresía.",
        "password": "🔒 Puedes restablecer tu contraseña desde la web.",
        "bug": "🐞 Gracias por reportarlo. Por favor, envía una captura de pantalla y explica cómo ocurrió.",
        "error": "⚠️ Describe el error con el mayor detalle posible e incluye una captura si es posible.",
        "gamma": "📈 La sección de Gamma recibe actualizaciones constantemente. Revisa <#1525310161537990666> para utilizar el heatmap y el gex con el /gex y /heatmap o compra <#1501337676576592052>.",
        "welcome": """👋 ¡Hola! 

¡Gracias por utilizar nuestros servicios y por contactar con el soporte!

Para poder ayudarte más rápido, por favor explica tu duda o problema con el mayor detalle posible.

### 🤖 Puedo ayudarte con preguntas como:
• 🔑 Login
• 🔒 Password
• 🐞 Bugs
• ⚠️ Errores
• 📈 Gamma

Simplemente escribe tu pregunta en este ticket.

Si no puedo resolver tu consulta automáticamente, un miembro del staff te responderá lo antes posible."""
    },
    "en": {
        "login": "🔑 If you are having trouble logging in, your membership may have expired.",
        "password": "🔒 You can reset your password from the website.",
        "bug": "🐞 Thanks for reporting. Please send a screenshot and explain what happened.",
        "error": "⚠️ Describe the error in as much detail as possible and include a screenshot if possible.",
        "gamma": "📈 The Gamma section is updated constantly. Check <#1525310161537990666> to use the heatmap and gex with /gex or /heatmap or buy <#1501337676576592052>.",
        "welcome": """👋 Hello! 

Thanks for using our services and for contacting support!

To help you faster, please explain your question or problem in as much detail as possible.

### 🤖 I can help you with questions like:
• 🔑 Login
• 🔒 Password
• 🐞 Bugs
• ⚠️ Errors
• 📈 Gamma

Simply write your question in this ticket.

If I cannot solve your query automatically, a staff member will reply as soon as possible."""
    }
}

class IdiomaView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    async def aplicar_idioma(self, interaction: discord.Interaction, lang: str):
        ticket_idioma[self.channel_id] = lang
        await interaction.response.edit_message(content=FAQ[lang]["welcome"], view=None)

    @discord.ui.button(label="Español 🇪🇸", style=discord.ButtonStyle.primary)
    async def spanish(self, interaction: discord.Interaction, button: Button):
        await self.aplicar_idioma(interaction, "es")

    @discord.ui.button(label="English 🇺🇸", style=discord.ButtonStyle.primary)
    async def english(self, interaction: discord.Interaction, button: Button):
        await self.aplicar_idioma(interaction, "en")

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or not isinstance(message.channel, discord.TextChannel):
        return

    if message.channel.name.startswith("ticket-"):
        if message.channel.id not in ticket_idioma:
            ticket_idioma[message.channel.id] = None
            await message.channel.send("👋 ¡Elige tu idioma / Please select your language:", view=IdiomaView(message.channel.id))
            return

        if ticket_idioma[message.channel.id] is None:
            return

        if not message.content.startswith(bot.command_prefix):
            lang = ticket_idioma[message.channel.id]
            for palabra, respuesta in FAQ[lang].items():
                if palabra != "welcome" and palabra in message.content.lower():
                    await message.reply(respuesta)
                    break

    await bot.process_commands(message)

# Iniciar servidor web y bot
keep_alive()
bot.run(TOKEN)
