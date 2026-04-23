import fs from 'fs';
import https from 'https';

https.get('https://canlihurdafiyatlari.com/fiyatlar.json', (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    fs.writeFileSync('./public/fiyatlar.json', data);
    console.log('Done!');
  });
});
