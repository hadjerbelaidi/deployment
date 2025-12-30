// Configuration de l'API
const API_BASE = window.location.origin;

// Vérifier l'état de l'API au chargement
window.addEventListener('DOMContentLoaded', async () => {
    await checkHealth();
    await loadStats();
});

// Vérifier l'état de l'API
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        
        const statusText = document.getElementById('status-text');
        const statusIndicator = document.querySelector('.status-indicator');
        
        if (data.status === 'healthy' && data.model_loaded) {
            if(statusText) statusText.textContent = '✅ Système opérationnel';
            if(statusIndicator) statusIndicator.classList.add('online');
        } else {
            if(statusText) statusText.textContent = '⚠️ Modèle non chargé';
        }
    } catch (error) {
        const statusText = document.getElementById('status-text');
        if(statusText) statusText.textContent = '❌ Erreur connexion';
        console.error('Erreur health check:', error);
    }
}

// Changer d'onglet
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Charger un exemple de données (CICIDS2017 a 78-79 features)
function loadExample() {
    const exampleFeatures = Array.from({length: 78}, () => Math.random());
    const exampleData = { features: exampleFeatures };
    document.getElementById('features-input').value = JSON.stringify(exampleData, null, 2);
}

// Prédiction unique
async function predictSingle() {
    const input = document.getElementById('features-input').value;
    const resultDiv = document.getElementById('single-result');
    
    if (!input.trim()) {
        showResult(resultDiv, 'Erreur', 'Veuillez entrer des données', 'info');
        return;
    }
    
    try {
        const data = JSON.parse(input);
        showLoading(resultDiv);
        
        const response = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (result.error) {
            showResult(resultDiv, 'Erreur', result.error, 'info');
            return;
        }
        
        displaySingleResult(resultDiv, result);
    } catch (error) {
        showResult(resultDiv, 'Erreur', 'Format JSON invalide ou erreur serveur', 'info');
    }
}

function displaySingleResult(div, result) {
    // Adaptation : 0 est normal, 1 est attaque dans ton modèle
    const isAttack = result.prediction !== 0; 
    const label = isAttack ? 'ATTACK' : 'BENIGN';
    const className = isAttack ? 'attack' : 'normal';
    const icon = isAttack ? '🚨' : '✅';
    
    div.className = `result-box ${className}`;
    div.style.display = 'block';
    div.innerHTML = `
        <div class="result-title">${icon} ${label}</div>
        <div class="result-detail"><strong>Classe détectée:</strong> ${result.prediction}</div>
        <div class="result-detail">Analyse effectuée par le modèle MLP dans le Cloud.</div>
    `;
}

// Gérer la sélection de fichier
function handleFileSelect(event) {
    const file = event.target.files[0];
    const fileName = document.getElementById('file-name');
    const batchBtn = document.getElementById('batch-btn');
    if (file) {
        fileName.textContent = `✓ ${file.name}`;
        batchBtn.disabled = false;
    }
}

// Prédiction batch (CSV)
async function predictBatch() {
    const fileInput = document.getElementById('csv-file');
    const resultDiv = document.getElementById('batch-result');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    showLoading(resultDiv);
    
    try {
        const response = await fetch(`${API_BASE}/api/predict_batch`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        // Calculer les stats pour l'affichage original
        const total = result.predictions.length;
        const attacks = result.predictions.filter(p => p !== 0).length;
        const normal = total - attacks;
        const percent = ((attacks / total) * 100).toFixed(2);

        displayBatchResult(resultDiv, {
            total_connections: total,
            attacks_detected: attacks,
            normal_detected: normal,
            attack_percentage: percent,
            predictions: result.predictions.map((p, i) => ({
                index: i + 1,
                prediction: p !== 0 ? 'ATTACK' : 'BENIGN'
            }))
        });
    } catch (error) {
        showResult(resultDiv, 'Erreur', 'Erreur lors de l\'analyse', 'info');
    }
}

function displayBatchResult(div, data) {
    const className = data.attacks_detected > 0 ? 'attack' : 'normal';
    div.className = `result-box ${className}`;
    div.style.display = 'block';
    
    let html = `
        <div class="result-title">📊 Rapport d'Analyse Cloud</div>
        <div class="result-detail"><strong>Total:</strong> ${data.total_connections}</div>
        <div class="result-detail">🚨 <strong>Attaques:</strong> ${data.attacks_detected} (${data.attack_percentage}%)</div>
        <div class="result-detail">✅ <strong>Normal:</strong> ${data.normal_detected}</div>
        <div style="margin-top:10px; max-height:150px; overflow-y:auto; font-size:0.8em;">
    `;
    
    data.predictions.slice(0, 50).forEach(p => {
        html += `<div>Ligne ${p.index}: ${p.prediction}</div>`;
    });
    
    html += `</div>`;
    div.innerHTML = html;
}

// Charger les statistiques depuis l'API
async function loadStats() {
    const statsContent = document.getElementById('stats-content');
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();
        
        statsContent.innerHTML = `
            <div class="stat-card"><h4>Architecture</h4><div class="value">${stats.model_architecture}</div></div>
            <div class="stat-card"><h4>Précision</h4><div class="value">${stats.accuracy}%</div></div>
            <div class="stat-card"><h4>Dataset</h4><div class="value">${stats.dataset}</div></div>
            <div class="stat-card"><h4>Cloud</h4><div class="value">${stats.cloud_platform}</div></div>
        `;
    } catch (e) {
        console.error("Erreur stats");
    }
}

function showLoading(div) {
    div.className = 'result-box info';
    div.style.display = 'block';
    div.innerHTML = '<div class="loading">⏳ Analyse Cloud en cours...</div>';
}

function showResult(div, title, message, type = 'info') {
    div.className = `result-box ${type}`;
    div.style.display = 'block';
    div.innerHTML = `<div class="result-title">${title}</div><div class="result-detail">${message}</div>`;
}
