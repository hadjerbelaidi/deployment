// Configuration de l'URL (automatique selon l'hébergement)
const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 Initialisation du système IDS...");
    checkHealth();
    loadHistory();
});

/**
 * Vérifie si le serveur Render est réveillé et opérationnel
 */
async function checkHealth() {
    const statusText = document.getElementById('status-text');
    const indicator = document.getElementById('indicator');

    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusText.textContent = '✅ Système Cloud Opérationnel';
            indicator.classList.add('online');
        }
    } catch (error) {
        statusText.textContent = '❌ Serveur en veille ou déconnecté';
        indicator.classList.remove('online');
        console.error("Erreur de connexion API:", error);
    }
}

/**
 * Gère l'affichage du nom du fichier sélectionné
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    const display = document.getElementById('file-name-display');
    const btn = document.getElementById('batch-btn');

    if (file) {
        display.textContent = `Fichier sélectionné : ${file.name}`;
        btn.disabled = false;
    } else {
        display.textContent = "";
        btn.disabled = true;
    }
}

/**
 * Envoie le fichier CSV au serveur pour analyse
 */
async function predictBatch() {
    const fileInput = document.getElementById('csv-file');
    const resultDiv = document.getElementById('batch-result');
    const btn = document.getElementById('batch-btn');

    if (!fileInput.files[0]) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // UI Feedback
    btn.disabled = true;
    const originalBtnText = btn.textContent;
    btn.textContent = "⏳ Analyse Cloud en cours...";
    resultDiv.style.display = "block";
    resultDiv.innerHTML = "<p>Transmission des données vers le modèle Deep Learning...</p>";

    try {
        const response = await fetch(`${API_BASE}/api/predict_batch`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error("Erreur serveur lors de l'analyse");

        const data = await response.json();

        // Affichage des résultats immédiats
        const attackDetected = data.attacks > 0;
        resultDiv.innerHTML = `
            <div style="text-align: left;">
                <h2 style="color: ${attackDetected ? 'var(--danger)' : 'var(--success)'}; margin-top:0;">
                    ${attackDetected ? '🚨 ALERTE : Intrusion Détectée' : '✅ Trafic Analysé comme Sain'}
                </h2>
                <hr style="border:0; border-top: 1px solid var(--border); margin: 15px 0;">
                <p>Analyse terminée pour : <b>${data.filename}</b></p>
                <div style="display: flex; gap: 20px; font-size: 1.1em;">
                    <span>📊 Total : <b>${data.total}</b></span>
                    <span style="color: var(--danger)">🚨 Attaques : <b>${data.attacks}</b></span>
                    <span style="color: var(--success)">🛡️ Normal : <b>${data.total - data.attacks}</b></span>
                </div>
            </div>
        `;

        // Rafraîchir l'historique car une nouvelle ligne a été ajoutée en DB
        loadHistory();

    } catch (error) {
        resultDiv.innerHTML = `<p style="color: var(--danger)">❌ Erreur : ${error.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.textContent = originalBtnText;
    }
}

/**
 * Récupère les 10 derniers scans depuis la base SQLite
 */
async function loadHistory() {
    const tbody = document.getElementById('history-body');

    try {
        const response = await fetch(`${API_BASE}/api/history`);
        const history = await response.json();
        
        if (!history || history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Aucune donnée historique.</td></tr>';
            return;
        }

        // Construction des lignes du tableau
        tbody.innerHTML = history.map(row => `
            <tr>
                <td>${row.date}</td>
                <td style="font-family: monospace;">${row.filename}</td>
                <td>${row.total}</td>
                <td>
                    <span class="${row.attacks > 0 ? 'badge-attack' : 'badge-benign'}">
                        ${row.attacks} ${row.attacks > 0 ? 'ATTACK(S)' : 'CLEAN'}
                    </span>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error("Erreur historique:", error);
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--danger);">Erreur de chargement.</td></tr>';
    }
}
