import express from "express";
import path from "path";

const app = express();
const PORT = 3000;

const publicPath = path.join(process.cwd(), 'public');
app.use(express.static(publicPath));

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});
