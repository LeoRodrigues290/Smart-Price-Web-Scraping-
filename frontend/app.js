
// app.js - Agora com Design Premium ✨

console.log("Smart Price Frontend Initialized 🚀");

const searchInput = document.getElementById('search');
const suggestionsBox = document.getElementById('suggestions');
const resultsArea = document.getElementById('results-area'); // Agora a grid principal
const loadingDiv = document.getElementById('loading');
const API_URL = 'http://localhost:8000/api';

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// === Sugestões (Mantida a lógica, visual levemente ajustado via CSS do index) ===
async function fetchSuggestions(term) {
    if (!term || term.length < 2) {
        hideSuggestions();
        return;
    }
    try {
        const response = await fetch(`${API_URL}/suggestions?q=${encodeURIComponent(term)}`);
        if (!response.ok) throw new Error('Api Error');
        const data = await response.json();
        renderSuggestions(data.suggestions);
    } catch (e) { console.error(e); }
}

function renderSuggestions(suggestions) {
    if (!suggestions?.length) { hideSuggestions(); return; }

    suggestionsBox.innerHTML = suggestions.map(item => `
        <div class="px-6 py-3.5 hover:bg-blue-50/50 cursor-pointer text-slate-600 transition-colors flex items-center gap-3 suggestion-item border-b border-gray-50 last:border-0">
            <span class="text-slate-400 text-sm">🔍</span>
            <span class="font-medium">${item}</span>
        </div>
    `).join('');

    suggestionsBox.classList.remove('hidden');

    document.querySelectorAll('.suggestion-item').forEach(el => {
        el.addEventListener('click', (e) => {
            searchInput.value = e.target.innerText.replace('🔍\n', '').trim(); // Limpa icone se pegar
            hideSuggestions();
            performSearch(searchInput.value);
        });
    });
}

function hideSuggestions() {
    suggestionsBox.classList.add('hidden');
    suggestionsBox.innerHTML = '';
}

// === Busca e Renderização ===

async function performSearch(term) {
    if (!term) return;

    // UI Cleanup
    hideSuggestions();
    resultsArea.innerHTML = '';
    loadingDiv.classList.remove('hidden'); // Show layout loading

    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(term)}`);
        const data = await response.json();
        renderResults(data.results);
    } catch (error) {
        console.error("Erro:", error);
        resultsArea.innerHTML = `
            <div class="col-span-full text-center py-12 bg-white/50 rounded-3xl border border-red-100">
                <p class="text-red-500 font-bold mb-2">Ops, algo deu errado.</p>
                <p class="text-slate-500">Tente novamente mais tarde.</p>
            </div>`;
    } finally {
        loadingDiv.classList.add('hidden');
    }
}

function renderResults(products) {
    if (!products?.length) {
        resultsArea.innerHTML = `
            <div class="col-span-full text-center py-12">
                <p class="text-2xl mb-2">🤷‍♂️</p>
                <p class="text-slate-500 text-lg">Nenhum produto encontrado para essa busca.</p>
            </div>`;
        return;
    }

    // Configuração visual das lojas (Logos/Cores)
    const storeConfig = {
        "Mercado Livre": {
            bg: "bg-[#FFF159]", // Amarelo ML
            text: "text-slate-900",
            label: "Mercado Livre",
            icon: "📦"
        },
        "Magazine Luiza": {
            bg: "bg-[#0086FF]", // Azul Magalu
            text: "text-white",
            label: "Magalu",
            icon: "🛍️"
        },
        "Amazon": {
            bg: "bg-[#FF9900]",
            text: "text-white",
            label: "Amazon",
            icon: "a"
        },
        "KaBuM!": {
            bg: "bg-[#FF5500]",
            text: "text-white",
            label: "KaBuM!",
            icon: "💥"
        }
    };

    resultsArea.innerHTML = products.map((p, index) => {
        // Fallback para loja desconhecida
        let store = storeConfig["Mercado Livre"];
        for (const key in storeConfig) {
            if (p.store.includes(key)) store = storeConfig[key];
        }

        // Stagger animation delay
        const delay = index * 100;

        return `
        <div class="group bg-white rounded-[2rem] p-4 shadow-sm hover:shadow-2xl hover:shadow-blue-900/10 border border-slate-100 transition-all duration-500 hover:-translate-y-2 flex flex-col justify-between animate-fade-in-up" style="animation-delay: ${delay}ms">
            
            <!-- Imagem -->
            <div class="relative w-full h-56 bg-slate-50 rounded-3xl overflow-hidden mb-4 p-6 flex items-center justify-center group-hover:bg-white transition-colors">
                <img src="${p.image}" alt="${p.title}" class="max-h-full max-w-full object-contain mix-blend-multiply group-hover:scale-110 transition-transform duration-500">
                
                <!-- Badge Loja -->
                <div class="absolute top-3 left-3 px-3 py-1.5 rounded-full text-xs font-bold shadow-sm flex items-center gap-1.5 ${store.bg} ${store.text}">
                    <span>${store.icon}</span> ${store.label}
                </div>
            </div>

            <!-- Conteúdo -->
            <div class="px-2 pb-2 flex-grow flex flex-col">
                <h3 class="font-medium text-slate-700 text-lg leading-snug line-clamp-2 mb-2 group-hover:text-blue-600 transition-colors" title="${p.title}">
                    ${p.title}
                </h3>
                
                <div class="mt-auto pt-4 border-t border-slate-50 flex items-end justify-between">
                    <div>
                        <p class="text-xs text-slate-400 font-medium uppercase tracking-wider mb-0.5">Melhor Preço</p>
                        <p class="text-2xl font-bold text-slate-900 tracking-tight">
                            R$ ${p.price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </p>
                    </div>
                    
                    <a href="${p.link}" target="_blank" class="h-10 w-10 flex items-center justify-center rounded-full bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-all transform group-hover:rotate-45">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                    </a>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

// Hooks de Evento
searchInput.addEventListener('input', debounce((e) => fetchSuggestions(e.target.value.trim()), 300));
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        hideSuggestions();
        performSearch(searchInput.value);
    }
});
document.getElementById('btn-search')?.addEventListener('click', () => performSearch(searchInput.value));

// Fecha ao clicar fora
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) hideSuggestions();
});
