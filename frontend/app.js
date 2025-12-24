// app.js
// Aqui vai ficar a lógica do nosso front.

console.log("Smart Price Frontend Initialized 🚀");

// Vamos pegar os elementos do DOM
const searchInput = document.getElementById('search');
const suggestionsBox = document.getElementById('suggestions');

// TODO: Implementar Debounce e chamada de API na próxima fase.
searchInput.addEventListener('input', (e) => {
    const query = e.target.value;
    console.log(`Digitando... ${query}`);

    // Placeholder apenas para ver funcionando no console
});
