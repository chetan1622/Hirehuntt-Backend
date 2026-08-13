const fs = require('fs');
let code = fs.readFileSync('frontend/src/App.jsx', 'utf8');
code = code.replace(/🎯 Job Hunt Console/g, '<div style={{display:\\"flex\\", alignItems:\\"center\\", justifyContent:\\"center\\", gap: 10}}><img src=\\"/h_logo.jpg\\" alt=\\"Logo\\" style={{height: 32, borderRadius: 6}}/> Hire Huntt</div>');
code = code.replace(/<div className="logo-sm">🎯 Job Hunt<\/div>/g, '<div className=\\"logo-sm\\" style={{display:\\"flex\\", alignItems:\\"center\\", gap: 8}}><img src=\\"/h_logo.jpg\\" alt=\\"Logo\\" style={{height: 24, borderRadius: 4}}/> Hire Huntt</div>');
code = code.replace(/HireHuntt/g, 'Hire Huntt');
code = code.replace(/Job Hunt Console/g, 'Hire Huntt');
fs.writeFileSync('frontend/src/App.jsx', code);
