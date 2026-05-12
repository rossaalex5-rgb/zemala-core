const fs = require('fs');
const path = require('path');
const { hash } = require('./canonical.js');
const mode = process.argv[2];
const filePath = process.argv[3];
try {
    const content = fs.readFileSync(filePath, 'utf8').trim();
    const lines = content.split('\n');
    const lastLine = lines[lines.length - 1];
    const data = JSON.parse(lastLine);
    if (mode === 'verify') {
        const expected = data.event_hash;
        delete data.event_hash;
        const actual = hash(data);
        process.stdout.write(actual === expected ? "OK\n" : "FAIL\n");
    } else {
        process.stdout.write(hash(data) + "\n");
    }
} catch (e) {
    process.stderr.write("Fehler: " + e.message + "\n");
    process.exit(1);
}
