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

// Fecha sugestões ao clicar fora
document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        hideSuggestions();
    }
});
