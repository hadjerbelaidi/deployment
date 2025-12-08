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
            statusText.textContent = '✅ Système opérationnel';
            statusIndicator.classList.add('online');
        } else {
            statusText.textContent = '⚠️ Modèle non chargé';
        }
    } catch (error) {
        const statusText = document.getElementById('status-text');
        statusText.textContent = '❌ Erreur connexion';
        console.error('Erreur health check:', error);
    }
}

// Changer d'onglet
function switchTab(tabName) {
    // Cacher tous les onglets
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Désactiver tous les boutons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Activer l'onglet sélectionné
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Charger un exemple de données
function loadExample() {
    // Créer un array de 78 valeurs aléatoires pour simuler des features
    const exampleFeatures = Array.from({length: 78}, () => Math.random() * 100);
    
    const exampleData = {
        features: exampleFeatures
    };
    
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
            headers: {
                'Content-Type': 'application/json'
            },
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
        console.error('Erreur:', error);
    }
}

// Afficher le résultat d'une prédiction unique
function displaySingleResult(div, result) {
    const isAttack = result.prediction === 'ATTACK';
    const className = isAttack ? 'attack' : 'normal';
    const icon = isAttack ? '🚨' : '✅';
    
    div.className = `result-box ${className}`;
    div.style.display = 'block';
    
    div.innerHTML = `
        <div class="result-title">${icon} ${result.prediction}</div>
        <div class="result-detail">
            <strong>Confiance:</strong> ${result.confidence}%
        </div>
        <div class="result-detail">
            <strong>Probabilité attaque:</strong> ${result.probability_attack}%
        </div>
        <div class="result-detail">
            <strong>Probabilité normal:</strong> ${result.probability_normal}%
        </div>
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
    } else {
        fileName.textContent = '';
        batchBtn.disabled = true;
    }
}

// Prédiction batch
async function predictBatch() {
    const fileInput = document.getElementById('csv-file');
    const resultDiv = document.getElementById('batch-result');
    
    if (!fileInput.files.length) {
        showResult(resultDiv, 'Erreur', 'Veuillez sélectionner un fichier', 'info');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    showLoading(resultDiv);
    
    try {
        const response = await fetch(`${API_BASE}/api/predict_batch`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.error) {
            showResult(resultDiv, 'Erreur', result.error, 'info');
            return;
        }
        
        displayBatchResult(resultDiv, result);
        
    } catch (error) {
        showResult(resultDiv, 'Erreur', 'Erreur lors de l\'analyse du fichier', 'info');
        console.error('Erreur:', error);
    }
}

// Afficher le résultat batch
function displayBatchResult(div, result) {
    const attackPercentage = result.attack_percentage;
    const className = attackPercentage > 50 ? 'attack' : 'normal';
    
    div.className = `result-box ${className}`;
    div.style.display = 'block';
    
    let html = `
        <div class="result-title">📊 Résultats de l'analyse</div>
        <div class="result-detail">
            <strong>Total connexions:</strong> ${result.total_connections}
        </div>
        <div class="result-detail">
            <strong>🚨 Attaques détectées:</strong> ${result.attacks_detected} (${result.attack_percentage}%)
        </div>
        <div class="result-detail">
            <strong>✅ Connexions normales:</strong> ${result.normal_detected}
        </div>
    `;
    
    if (result.accuracy) {
        html += `
            <div class="result-detail">
                <strong>Précision:</strong> ${result.accuracy}%
            </div>
        `;
    }
    
    if (result.note) {
        html += `<div class="result-detail" style="margin-top: 15px; font-style: italic;">${result.note}</div>`;
    }
    
    // Afficher les premières prédictions
    if (result.predictions && result.predictions.length > 0) {
        html += '<div style="margin-top: 20px;"><strong>Détails des premières prédictions:</strong></div>';
        html += '<div style="max-height: 300px; overflow-y: auto; margin-top: 10px;">';
        
        result.predictions.slice(0, 10).forEach(pred => {
            const icon = pred.prediction === 'ATTACK' ? '🚨' : '✅';
            html += `
                <div style="padding: 8px; margin: 5px 0; background: rgba(0,0,0,0.05); border-radius: 4px;">
                    ${icon} Ligne ${pred.index}: <strong>${pred.prediction}</strong> (${pred.confidence}%)
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    div.innerHTML = html;
}

// Charger les statistiques
async function loadStats() {
    const statsContent = document.getElementById('stats-content');
    
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();
        
        statsContent.innerHTML = `
            <div class="stat-card">
                <h4>Architecture</h4>
                <div class="value">${stats.model_architecture}</div>
            </div>
            <div class="stat-card">
                <h4>Couches</h4>
                <div class="value">${stats.layers.join(' → ')}</div>
            </div>
            <div class="stat-card">
                <h4>Précision</h4>
                <div class="value">${stats.accuracy}%</div>
            </div>
            <div class="stat-card">
                <h4>Dataset</h4>
                <div class="value">${stats.dataset}</div>
            </div>
            <div class="stat-card">
                <h4>Méthode d'entraînement</h4>
                <div class="value" style="font-size: 1.2em;">${stats.training_method}</div>
            </div>
            <div class="stat-card">
                <h4>Types d'attaques détectées</h4>
                <div class="value" style="font-size: 1em;">
                    ${stats.attack_types.join(', ')}
                </div>
            </div>
        `;
    } catch (error) {
        statsContent.innerHTML = '<div class="loading">Erreur de chargement des statistiques</div>';
        console.error('Erreur stats:', error);
    }
}

// Fonctions utilitaires
function showLoading(div) {
    div.className = 'result-box info';
    div.style.display = 'block';
    div.innerHTML = '<div class="loading">⏳ Analyse en cours...</div>';
}

function showResult(div, title, message, type = 'info') {
    div.className = `result-box ${type}`;
    div.style.display = 'block';
    div.innerHTML = `
        <div class="result-title">${title}</div>
        <div class="result-detail">${message}</div>
    `;
}