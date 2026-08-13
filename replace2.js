const fs = require('fs');
let code = fs.readFileSync('frontend/index.html', 'utf8');
code = code.replace(/Job Hunt Console/g, 'Hire Huntt');
fs.writeFileSync('frontend/index.html', code);
