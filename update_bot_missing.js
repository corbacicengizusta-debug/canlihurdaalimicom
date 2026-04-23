import fs from 'fs';

const botFile = './public/bot.py';
let botText = fs.readFileSync(botFile, 'utf8');

const missingItems = `
    "Arayiş Bakır": 635.40,
    "Kalıp Bakır": 629.57,
    "Beyaz Bakır": 600.00,
    "Hurda Bakır": 617.68,
    "Kırkambar Bakır": 620.00,
    "310 Krom": 90.00,
    "201 - 202 Krom": 25.00,
    "4x 25": 551.65,
    "Alüminyum Kablo": 90.00,
    "Tesisat Kablo": 355.00,
    "Kıl Kablo": 201.00,
    "Enya": 581.65,
    "Karışık": 45.00,
`;

// Insert into base prices
botText = botText.replace(/("Soyulmuş Bakır Fiyatı": 552\.15,)/, `$1${missingItems}`);

// We also need to add them to PRICE_CATEGORIES so the bot sends them
const catUpdates = {
    '"BAKIR HURDASI", "items": \\[': '"Arayiş Bakır", "Kalıp Bakır", "Beyaz Bakır", "Hurda Bakır", "Kırkambar Bakır", ',
    '"KROM HURDASI", "items": \\[': '"310 Krom", "201 - 202 Krom", ',
    '"KABLO HURDASI", "items": \\[': '"4x 25", "Alüminyum Kablo", "Tesisat Kablo", "Kıl Kablo", "Enya", ',
    '"MOTOR VE SÖKÜLECEK HURDASI", "items": \\[': '"Karışık", '
};

for (const [key, val] of Object.entries(catUpdates)) {
    const rx = new RegExp(`(${key})`, 'g');
    botText = botText.replace(rx, `$1${val}`);
}

fs.writeFileSync(botFile, botText);
