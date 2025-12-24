// app.js

console.log("Smart Price Frontend Initialized 🚀");

const searchInput = document.getElementById('search');
const suggestionsBox = document.getElementById('suggestions');
const API_URL = 'http://localhost:8000/api';

/**
 * Função de Debounce
 * Evita que a função seja chamada repetidamente em um curto período de tempo.
 * Ótimo para inputs de pesquisa.
 */
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * Busca sugestões na API
 */
async function fetchSuggestions(term) {
    if (!term || term.length < 2) {
        hideSuggestions();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/suggestions?q=${encodeURIComponent(term)}`);
        if (!response.ok) throw new Error('Erro na API');

        const data = await response.json();
        renderSuggestions(data.suggestions);
    } catch (error) {
        console.error("Erro ao buscar sugestões:", error);
    }
}

/**
 * Renderiza a lista de sugestões no DOM
 */
function renderSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        hideSuggestions();
        return;
    }

    const html = suggestions.map(item => `
        <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer text-gray-700 suggestion-item">
            ${item}
        </div>
    `).join('');

    suggestionsBox.innerHTML = html;
    suggestionsBox.classList.remove('hidden');

    // Adiciona evento de click em cada item
    document.querySelectorAll('.suggestion-item').forEach(el => {
        el.addEventListener('click', (e) => {
            searchInput.value = e.target.innerText;
            hideSuggestions();
            // Aqui poderíamos disparar a busca completa automaticamente
            console.log(`Selecionado: ${e.target.innerText}`);
        });
    });
}

function hideSuggestions() {
    suggestionsBox.classList.add('hidden');
    suggestionsBox.innerHTML = '';
}

// Evento de input com Debounce de 300ms
searchInput.addEventListener('input', debounce((e) => {
    const query = e.target.value.trim();
    fetchSuggestions(query);
}, 300));

// Evento para realizar a busca (Enter ou Click)
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        hideSuggestions();
        performSearch(searchInput.value);
    }
});

// Busca ao clicar no botão de lupa (se houver, mas o HTML tem o botão dentro do input group)
const searchBtn = document.querySelector('button'); // Pega o primeiro botão (lupa)
if (searchBtn) {
    searchBtn.addEventListener('click', () => {
        performSearch(searchInput.value);
    });
}

// Fecha sugestões ao clicar fora
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        hideSuggestions();
    }
});

async function performSearch(term) {
    if (!term) return;

    console.log(`Buscando por: ${term}`);

    // Mostra loading "simples" com animação de pulso
    const resultsContainer = document.getElementById('results-area') || createResultsContainer();
    resultsContainer.innerHTML = `
        <div class="col-span-full flex flex-col items-center justify-center py-12 animate-pulse">
            <div class="h-8 w-8 bg-blue-600 rounded-full mb-4 animate-bounce"></div>
            <p class="text-gray-500 font-medium">Pesquisando melhores ofertas...</p>
            <p class="text-xs text-gray-400 mt-2">Isso pode levar alguns segundos (Web Scraping em ação 🤖)</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(term)}`);
        const data = await response.json();
        renderResults(data.results);
    } catch (error) {
        console.error("Erro na busca:", error);
        resultsContainer.innerHTML = '<div class="text-center p-8 text-red-500">Erro ao buscar produtos. Tente novamente.</div>';
    }
}

function createResultsContainer() {
    const main = document.querySelector('main');
    const container = document.createElement('div');
    container.id = 'results-area';
    container.className = 'mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full';
    main.appendChild(container);
    return container;
}

function renderResults(products) {
    const container = document.getElementById('results-area');
    if (!products || products.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-500 py-10">Nenhum produto encontrado. Tente outro termo. 😕</div>';
        return;
    }

    // Mapa de cores para as lojas
    const storeColors = {
        "Mercado Livre": "bg-yellow-100 text-yellow-800 border-yellow-200",
        "Mercado Livre (Mock)": "bg-yellow-50 text-yellow-600 border-yellow-100", // Diferencia o mock levemente
        "Magazine Luiza": "bg-blue-100 text-blue-800 border-blue-200",
        "Magazine Luiza (Mock)": "bg-blue-50 text-blue-600 border-blue-100"
    };

    const html = products.map(p => {
        // Define a cor baseada na loja, fallback para cinza
        const colorClass = storeColors[p.store] || "bg-gray-100 text-gray-800 border-gray-200";

        return `
        <div class="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 flex flex-col group">
            <div class="h-48 bg-white flex items-center justify-center p-6 relative overflow-hidden">
                <img src="${p.image}" alt="${p.title}" class="max-h-full max-w-full object-contain transform group-hover:scale-105 transition-transform duration-300">
            </div>
            <div class="p-5 flex flex-col flex-grow border-t border-gray-50">
                <span class="text-xs font-bold px-2 py-1 rounded-full w-fit mb-3 border ${colorClass}">
                    ${p.store}
                </span>
                <h3 class="font-medium text-gray-800 line-clamp-2 mb-2 flex-grow text-sm leading-relaxed" title="${p.title}">
                    ${p.title}
                </h3>
                <div class="mt-4 pt-4 border-t border-gray-50">
                    <p class="text-xs text-gray-400 mb-1">A partir de</p>
                    <div class="flex items-end justify-between">
                        <p class="text-2xl font-bold text-gray-900">
                            R$ ${p.price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </p>
                    </div>
                    <a href="${p.link}" target="_blank" class="block mt-4 w-full text-center bg-blue-600 text-white font-medium py-2.5 rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-blue-200 shadow-md">
                        Ver na Loja
                    </a>
                </div>
            </div>
        </div>
    `}).join('');

    container.innerHTML = html;
}

