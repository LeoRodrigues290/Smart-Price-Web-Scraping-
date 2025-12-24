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

    // Mostra loading "simples"
    const resultsContainer = document.getElementById('results-area') || createResultsContainer();
    resultsContainer.innerHTML = '<div class="text-center p-8 text-gray-500">Buscando melhores preços... ⏳</div>';

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
        container.innerHTML = '<div class="col-span-full text-center text-gray-500">Nenhum produto encontrado.</div>';
        return;
    }

    const html = products.map(p => `
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow border border-gray-100 flex flex-col">
            <div class="h-48 bg-gray-50 flex items-center justify-center p-4">
                <img src="${p.image}" alt="${p.title}" class="max-h-full object-contain">
            </div>
            <div class="p-4 flex flex-col flex-grow">
                <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded w-fit mb-2">${p.store}</span>
                <h3 class="font-medium text-gray-800 line-clamp-2 mb-2 flex-grow" title="${p.title}">${p.title}</h3>
                <div class="mt-auto">
                    <p class="text-2xl font-bold text-gray-900">R$ ${p.price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                    <a href="${p.link}" target="_blank" class="block mt-3 w-full text-center bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors">
                        Ver na Loja
                    </a>
                </div>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}
