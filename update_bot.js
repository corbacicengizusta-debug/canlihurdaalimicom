import fs from 'fs';

const botFile = './public/bot.py';
let botText = fs.readFileSync(botFile, 'utf8');

const updates = {
  "Arayiş Bakır": 635.40,
  "Kalıp Bakır": 629.57,
  "Beyaz Bakır": 600.00,
  "Hurda Bakır": 617.68,
  "Kırkambar Bakır": 620.00,
  "Batarya Vana Su Saati": 345.00,
  "304 Paslanmaz Krom Hurda": 110.00,
  "310 Krom": 90.00,
  "201 - 202 Krom": 25.00,
  "Tekdamar Kalın": 580.00,
  "4x 25": 551.65,
  "Alüminyum Kablo": 90.00,
  "Tesisat Kablo": 355.00,
  "Kıl Kablo": 201.00,
  "Enya": 581.65,
  "Ttr Hurda Kablo Fiyatları": 420.00,
  "Arayiş Alüminyum": 151.65,
  "Beyaz Profil Alüminyum": 150.00,
  "Renkli Alüminyum": 131.65,
  "Sineklik Alüminyum": 131.65,
  "Motor": 61.50,
  "Karışık": 45.00,
  "Buzdolabı Motor": 40.00,
  "Karışık Sökülecek": 50.00
};

// Replace prices in BASE_PRICES
for (const [key, val] of Object.entries(updates)) {
    const rx = new RegExp(`("${key}":\\s*)[\\d\\.]+`, 'g');
    if (rx.test(botText)) {
      botText = botText.replace(rx, `$1${val.toFixed(2)}`);
    } else {
        // If it doesn't exist, we'll manually insert it below later if needed.
    }
}

// remove 1.grup and teneke from base prices and lists
botText = botText.replace(/,\s*"1\.Grup"[^,]+,/g, ',');
botText = botText.replace(/,\s*"Teneke"[^,]+,/g, ',');
botText = botText.replace(/"1\.Grup":\s*[\d\.]+,/g, '');
botText = botText.replace(/"Teneke":\s*[\d\.]+,/g, '');

fs.writeFileSync(botFile, botText);
console.log('bot.py updated');
