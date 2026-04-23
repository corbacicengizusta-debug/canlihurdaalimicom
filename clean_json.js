import fs from 'fs';

const jsonPath = './public/fiyatlar.json';
let db = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

// Filter out 1.Grup and Teneke from DEMIR HURDASI
db.data = db.data.map(cat => {
    if (cat.t === "DEMİR HURDASI") {
        cat.i = cat.i.filter(item => item.n !== "1.Grup" && item.n !== "Teneke");
    }
    return cat;
});

fs.writeFileSync(jsonPath, JSON.stringify(db, null, 4), 'utf8');
console.log("fiyatlar.json cleaned");
