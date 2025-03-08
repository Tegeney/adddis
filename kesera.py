require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });

const userState = {}; // To store user inputs temporarily

// Function to fetch student results
async function fetchResult(regNo, firstName) {
    const url = `https://sw.ministry.et/api/student/result`; // Replace with actual API endpoint
    try {
        const response = await axios.post(url, {
            registration_number: regNo,
            first_name: firstName
        });

        if (response.data && response.data.result) {
            return `📜 *Result for ${firstName} (Reg: ${regNo})*\n\n${response.data.result}`;
        } else {
            return "❌ No result found. Please check your registration number and first name.";
        }
    } catch (error) {
        console.error("Error fetching result:", error);
        return "⚠️ Unable to fetch the result. Please try again later.";
    }
}

// Handle incoming messages
bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text.trim();

    if (text.toLowerCase() === "/start") {
        bot.sendMessage(chatId, "👋 Welcome! Please enter your **Registration Number**:");
        userState[chatId] = { step: "waitingForRegNo" };
    } else if (userState[chatId]?.step === "waitingForRegNo") {
        userState[chatId].regNo = text;
        userState[chatId].step = "waitingForFirstName";
        bot.sendMessage(chatId, "✅ Now, enter your **First Name**:");
    } else if (userState[chatId]?.step === "waitingForFirstName") {
        userState[chatId].firstName = text;
        const { regNo, firstName } = userState[chatId];

        bot.sendMessage(chatId, "⏳ Fetching your result, please wait...");

        const result = await fetchResult(regNo, firstName);
        bot.sendMessage(chatId, result, { parse_mode: "Markdown" });

        delete userState[chatId]; // Clear user data after fetching the result
    } else {
        bot.sendMessage(chatId, "⚠️ Invalid command! Please type /start to begin.");
    }
});

console.log("Bot is running...");
