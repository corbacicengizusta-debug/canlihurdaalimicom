import fs from 'fs';

const file = './public/fiyatlar.json';
const data = JSON.parse(fs.readFileSync(file, 'utf-8'));

data.updated_at = new Date().toLocaleString("tr-TR");

const cat = (name) => data.data.find(c => c.t === name);

// DEMIR HURDASI
const demir = cat("DEMİR HURDASI");
if (demir) {
  demir.i = demir.i.filter(item => !item.n.includes("1.Grup") && !item.n.includes("Teneke"));
}

// KROM HURDASI
const krom = cat("KROM HURDASI");
if (krom) {
  const k304 = krom.i.find(x => x.n.includes("304"));
  if (k304) k304.p = 110;
  
  if (!krom.i.find(x => x.n.includes("310"))) {
    krom.i.push({ n: "310 Krom", p: 90, change: "same", percent: 0 });
  }
  if (!krom.i.find(x => x.n.includes("201"))) {
    krom.i.push({ n: "201 - 202 Krom", p: 25, change: "same", percent: 0 });
  }
}

// SARI HURDASI
const sari = cat("SARI HURDASI");
if (sari) {
  const bat = sari.i.find(x => x.n.includes("Batarya"));
  if (bat) {
    bat.p = 345;
  } else {
    sari.i.push({ n: "Batarya", p: 345, change: "same", percent: 0 });
  }
}

// BAKIR HURDASI
const bakirItemsToUpdate = {
  "Arayiş Bakır": 635.40,
  "Kalıp Bakır": 629.57,
  "Beyaz Bakır": 600,
  "Hurda Bakır": 617.68,
  "Kırkambar Bakır": 620
};
const bakir = cat("BAKIR HURDASI");
if (bakir) {
  for (const [name, price] of Object.entries(bakirItemsToUpdate)) {
    const existing = bakir.i.find(x => x.n.toLowerCase() === name.toLowerCase());
    if (existing) {
      existing.p = price;
    } else {
      bakir.i.push({ n: name, p: price, change: "same", percent: 0 });
    }
  }
}

// KABLO HURDASI
const kabloItemsToUpdate = {
  "Tek Damar": 580,
  "4x 25": 551.65,
  "Alüminyum Kablo": 90,
  "Tesisat Kablo": 355,
  "Kıl Kablo": 201,
  "Enya": 581.65,
  "Ttr": 420
};
const kablo = cat("KABLO HURDASI");
if (kablo) {
  for (const [name, price] of Object.entries(kabloItemsToUpdate)) {
    const existing = kablo.i.find(x => x.n.toLowerCase().includes(name.toLowerCase()) || name.toLowerCase().includes(x.n.toLowerCase()) || 
        (name === "Enya" && x.n.toLowerCase().includes("nya")) || 
        (name === "Ttr" && x.n.toLowerCase().includes("ttr")) ||
        (name === "Tek Damar" && x.n.toLowerCase().includes("tekdamar")));
    if (existing) {
      existing.p = price;
      existing.n = name; // Update name to the cleaner one written in notes
    } else {
      kablo.i.push({ n: name, p: price, change: "same", percent: 0 });
    }
  }
}

// ALÜMINYUM HURDASI
const alItemsToUpdate = {
  "Arayiş Alüminyum": 151.65,
  "Beyaz Profil Alüminyum": 150,
  "Renkli Alüminyum": 131.65,
  "Sineklik Alüminyum": 131.65
};
const al = cat("ALÜMİNYUM HURDASI");
if (al) {
  for (const [name, price] of Object.entries(alItemsToUpdate)) {
    const existing = al.i.find(x => x.n.toLowerCase() === name.toLowerCase());
    if (existing) {
      existing.p = price;
    } else {
      al.i.push({ n: name, p: price, change: "same", percent: 0 });
    }
  }
}

// MOTOR VE SÖKÜLECEK HURDASI
const motorItemsToUpdate = {
  "Motor": 61.50,
  "Karışık": 45,
  "Buzdolabı Motor": 40,
  "Karışık Sökülecek": 50
};
const motor = cat("MOTOR VE SÖKÜLECEK HURDASI");
if (motor) {
  for (const [name, price] of Object.entries(motorItemsToUpdate)) {
    const existing = motor.i.find(x => x.n.toLowerCase() === name.toLowerCase() || (name.includes("Buzdolabı") && x.n.includes("Buzdolabı")));
    if (existing) {
      existing.p = price;
      existing.n = name;
    } else {
      motor.i.push({ n: name, p: price, change: "same", percent: 0 });
    }
  }
}

fs.writeFileSync(file, JSON.stringify(data, null, 4));
console.log("Updated fiyatlar.json");
