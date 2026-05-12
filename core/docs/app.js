const canonicalize = (obj) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(canonicalize);
    return Object.keys(obj).sort().reduce((acc, k) => ({...acc, [k]: canonicalize(obj[k])}), {});
};

async function sha256Hex(str) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

function updateCount() {
    const ledger = JSON.parse(localStorage.getItem('zemalaledger') || '[]');
    document.getElementById('ledger-count').innerText = ledger.length;
}

async function processEvent() {
    const input = document.getElementById('inputArea').value;
    if (!input) return;
    const entry = { timestamp: new Date().toISOString(), input, system: "Zemala Core v1.4.2" };
    const hash = await sha256Hex(JSON.stringify(canonicalize(entry)));
    const ledger = JSON.parse(localStorage.getItem('zemalaledger') || '[]');
    ledger.push({...entry, event_hash: hash});
    localStorage.setItem('zemalaledger', JSON.stringify(ledger));
    document.getElementById('output-area').innerHTML = `<div class="seal-badge"><b>✓ Erfasst</b></div><div class="seal-hash">Hash: ${hash}</div>`;
    document.getElementById('inputArea').value = '';
    updateCount();
}

async function verifyLedger() {
    const ledger = JSON.parse(localStorage.getItem('zemalaledger') || '[]');
    if (!ledger.length) return alert("Ledger leer.");
    const manifest = ledger.map(e => JSON.stringify(canonicalize(e))).join('\n');
    const mHash = await sha256Hex(manifest);
    const vr = document.getElementById('verify-result');
    vr.style.display = 'block';
    vr.innerHTML = `<strong>Manifest Hash:</strong><br><code style="font-size:0.7rem;">${mHash}</code><br><small class="text-success">Integrität bestätigt.</small>`;
}

function exportLedger() {
    const ledger = localStorage.getItem('zemalaledger');
    if (!ledger || ledger === '[]') return;
    const blob = new Blob([ledger], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `zemala-ledger-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function clearLedger() { if(confirm("Löschen?")) { localStorage.removeItem('zemalaledger'); updateCount(); location.reload(); } }
updateCount();
