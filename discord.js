const Discord = require('discord.js');
const { MongoClient } = require('mongodb');

// Configurações do bot
const client = new Discord.Client();
const prefix = '!'; // Prefixo dos comandos
const MONGO_URI = process.env.MONGODB_URI; // URI do MongoDB

// Conectar ao MongoDB
const mongoClient = new MongoClient(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true });

// Evento de inicialização do bot
client.once('ready', async () => {
    console.log(`Bot ${client.user.tag} está online.`);
    
    // Conectar ao banco de dados
    try {
        await mongoClient.connect();
        console.log('Conectado ao MongoDB.');

        const db = mongoClient.db('cardbot'); // Nome da database
        const cardsCollection = db.collection('cards'); // Nome da coleção

        // Verificar se as cartas já estão presentes no MongoDB
        const count = await cardsCollection.countDocuments({});
        if (count === 0) {
            // Adicionar as cartas iniciais se o banco de dados estiver vazio
            const initialCards = [
                { name: 'Card 1', image_url: 'https://example.com/card1.jpg' },
                { name: 'Card 2', image_url: 'https://example.com/card2.jpg' },
                { name: 'Card 3', image_url: 'https://example.com/card3.jpg' },
                { name: 'Card 4', image_url: 'https://example.com/card4.jpg' },
                { name: 'Card 5', image_url: 'https://example.com/card5.jpg' }
            ];

            const result = await cardsCollection.insertMany(initialCards);
            console.log(`${result.insertedCount} cartas foram inicializadas no banco de dados.`);
        } else {
            console.log('Cartas já presentes no banco de dados.');
        }
    } catch (error) {
        console.error('Erro ao conectar ao MongoDB:', error);
    }
});

// Comando para mostrar cartas do usuário
client.on('message', async message => {
    if (message.content.startsWith(`${prefix}mycards`)) {
        try {
            const db = mongoClient.db('cardbot'); // Nome da database
            const cardsCollection = db.collection('cards'); // Nome da coleção

            const cards = await cardsCollection.find({}).toArray();
            const embed = new Discord.MessageEmbed()
                .setTitle('Seu Inventário de Cartas');

            cards.forEach(card => {
                embed.addField(card.name, `[Imagem](${card.image_url})`, false);
            });

            message.channel.send(embed);
        } catch (error) {
            console.error('Erro ao buscar cartas:', error);
            message.channel.send('Ocorreu um erro ao buscar suas cartas.');
        }
    }
});

// Outros comandos (adicionar, remover, limpar cartas) podem ser adicionados aqui

// Iniciar o bot
client.login(process.env.DISCORD_TOKEN); // Token do bot
