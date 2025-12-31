const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadHistory();
});

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        if (response.ok) {
            document.getElementById('status-text').textContent = "✅ Système Connecté";
            document.getElementById('indicator').classList.add('online');
        }
    } catch (e) { document.getElementById('status-text').textContent = "❌ Mode Hors-ligne"; }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    document.getElementById('file-name-display').textContent = file ? `Prêt : ${file.name}` : "";
    document.getElementById('batch-btn').disabled = !file;
}

async function predictBatch() {
    const fileInput = document.getElementById('csv-file');
    const resultDiv = document.getElementById('batch-result');
    const btn = document.getElementById('batch-btn');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    btn.disabled = true;
    btn.textContent = "⏳ Analyse en cours...";
    resultDiv.style.display = "block";
    resultDiv.innerHTML = "Traitement par l'IA...";

    try {
        const response = await fetch(`${API_BASE}/api/predict_batch`, { method: 'POST', body: formData });
        const data = await response.json();

        // Création du tableau de détails
        let rowsHtml = "";
        data.predictions.forEach((res, i) => {
            const isAttack = res === 1;
            rowsHtml += `<tr>
                <td>Ligne ${i + 1}</td>
                <td style="color: ${isAttack ? 'red' : 'green'}; font-weight: bold;">
                    ${isAttack ? '🚨 ATTACK' : '✅ BENIGN'}
                </td>
            </tr>`;
        });

        resultDiv.innerHTML = `
            <h3>Rapport : ${data.filename}</h3>
            <p>Total : ${data.total} | Attaques : <b style="color:red">${data.attacks}</b></p>
            <div class="scroll-table">
                <table>
                    <thead><tr><th>Flux</th><th>Verdict IA</th></tr></thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
        `;
        loadHistory();
    } catch (e) { resultDiv.innerHTML = "❌ Erreur de communication avec l'API."; }
    finally { btn.disabled = false; btn.textContent = "Lancer l'Analyse"; }
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history`);
        const history = await response.json();
        document.getElementById('history-body').innerHTML = history.map(h => `
            <tr>
                <td>${h.date}</td>
                <td>${h.filename}</td>
                <td>${h.total}</td>
                <td><b style="color:${h.attacks > 0 ? 'red' : 'green'}">${h.attacks}</b></td>
            </tr>
        `).join('');
    } catch (e) { console.error("Erreur historique"); }
}
