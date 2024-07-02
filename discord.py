import os
import discord
from discord.ext import commands
from pymongo import MongoClient

# Configuração do bot
TOKEN = os.environ.get('DISCORD_TOKEN')
MONGO_URI = os.environ.get('MONGODB_URI')

# Conectar ao banco de dados MongoDB
client = MongoClient(MONGO_URI)
db = client['cardbot']
cards_collection = db['cards']

# Configuração do bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Evento de inicialização do bot
@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} está online.')

    # Verifica se as cartas já estão presentes no MongoDB
    if cards_collection.count_documents({}) == 0:
        # Adiciona as cartas iniciais apenas se o banco de dados estiver vazio
        initial_cards = [
            {"name": "Card 1", "image_url": "https://example.com/card1.jpg"},
            {"name": "Card 2", "image_url": "https://example.com/card2.jpg"},
            {"name": "Card 3", "image_url": "https://example.com/card3.jpg"},
            {"name": "Card 4", "image_url": "https://example.com/card4.jpg"},
            {"name": "Card 5", "image_url": "https://example.com/card5.jpg"}
        ]

        for card in initial_cards:
            card_document = {"card_name": card['name'], "image_url": card['image_url']}
            cards_collection.insert_one(card_document)
        print(f'{len(initial_cards)} cartas foram inicializadas no banco de dados.')
    else:
        print('Cartas já presentes no banco de dados.')

# Comando para mostrar cartas do usuário
@bot.command(name='mycards', help='Mostra todos os cards no seu inventário.')
async def mycards(ctx):
    user_id = ctx.author.id
    cards = cards_collection.find()
    embed = discord.Embed(title="Seu Inventário de Cartas")
    for card in cards:
        embed.add_field(name=card['card_name'], value=f"[Imagem]({card['image_url']})", inline=False)
    await ctx.send(embed=embed)

# Comando para adicionar uma nova carta
@bot.command(name='addcard', help='Adiciona um novo card ao seu inventário.')
async def addcard(ctx, card_name: str, image_url: str):
    card_document = {"card_name": card_name, "image_url": image_url}
    cards_collection.insert_one(card_document)
    await ctx.send(f'Card "{card_name}" adicionado ao seu inventário.')

# Comando para remover uma carta
@bot.command(name='removecard', help='Remove um card do seu inventário.')
async def removecard(ctx, card_name: str):
    result = cards_collection.delete_one({"card_name": card_name})
    if result.deleted_count:
        await ctx.send(f'Card "{card_name}" removido do seu inventário.')
    else:
        await ctx.send(f'Você não possui o card "{card_name}".')

# Comando para limpar todas as cartas do usuário
@bot.command(name='clearcards', help='Remove todas as cartas do seu inventário.')
async def clearcards(ctx):
    result = cards_collection.delete_many({})
    await ctx.send(f'Todas as cartas foram removidas do seu inventário.')

# Rodar o bot
bot.run(TOKEN)
