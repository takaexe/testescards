const { Client, Intents, MessageEmbed } = require('discord.js');
const { MongoClient } = require('mongodb');

// Configuração do bot
const TOKEN = process.env.DISCORD_TOKEN;
const MONGO_URI = process.env.MONGODB_URI;

// Conectar ao banco de dados MongoDB
const client = new MongoClient(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true });
let db, cardsCollection;

async function connectToMongo() {
    try {
        await client.connect();
        console.log('Conectado ao banco de dados MongoDB');
        db = client.db('cardbot');
        cardsCollection = db.collection('cards');

        // Verifica se as cartas já estão presentes no MongoDB
        const count = await cardsCollection.countDocuments({});
        if (count === 0) {
            // Adiciona as cartas iniciais apenas se o banco de dados estiver vazio
            const initialCards = [
                { name: 'Card 1', image_url: 'https://example.com/card1.jpg' },
                { name: 'Card 2', image_url: 'https://example.com/card2.jpg' },
                { name: 'Card 3', image_url: 'https://example.com/card3.jpg' },
                { name: 'Card 4', image_url: 'https://example.com/card4.jpg' },
                { name: 'Card 5', image_url: 'https://example.com/card5.jpg' }
            ];

            await cardsCollection.insertMany(initialCards);
            console.log(`${initialCards.length} cartas foram inicializadas no banco de dados.`);
        } else {
            console.log('Cartas já presentes no banco de dados.');
        }
    } catch (error) {
        console.error('Erro ao conectar ao banco de dados MongoDB:', error);
    }
}

connectToMongo();

// Configuração do bot Discord
const intents = new Intents(Intents.ALL);
const bot = new Client({ intents });

bot.once('ready', () => {
    console.log(`Bot ${bot.user.tag} está online.`);
});

bot.on('message', async (message) => {
    if (message.content.toLowerCase() === '!mycards') {
        const cards = await cardsCollection.find({}).toArray();
        const embed = new MessageEmbed().setTitle('Seu Inventário de Cartas');
        
        cards.forEach(card => {
            embed.addField(card.card_name, `[Imagem](${card.image_url})`, false);
        });

        message.channel.send(embed);
    } else if (message.content.toLowerCase().startsWith('!addcard')) {
        const args = message.content.split(' ').slice(1);
        const cardName = args[0];
        const imageUrl = args[1];

        const cardDocument = { card_name: cardName, image_url: imageUrl };
        await cardsCollection.insertOne(cardDocument);
        message.channel.send(`Card "${cardName}" adicionado ao seu inventário.`);
    } else if (message.content.toLowerCase().startsWith('!removecard')) {
        const args = message.content.split(' ').slice(1);
        const cardName = args[0];

        const result = await cardsCollection.deleteOne({ card_name: cardName });
        if (result.deletedCount) {
            message.channel.send(`Card "${cardName}" removido do seu inventário.`);
        } else {
            message.channel.send(`Você não possui o card "${cardName}".`);
        }
    } else if (message.content.toLowerCase() === '!clearcards') {
        await cardsCollection.deleteMany({});
        message.channel.send('Todas as cartas foram removidas do seu inventário.');
    }
});

// Rodar o bot
bot.login(TOKEN);
