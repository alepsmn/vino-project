/* === ELEMENTOS === */
const overlayCatalogo = document.getElementById('overlayCatalogo');
const panelCategorias = document.getElementById('panelCategorias');
const panelFiltros = document.getElementById('panelFiltros');

/* === FUNCIONES === */

function cerrarPaneles() {
    overlayCatalogo.classList.remove('visible');
    panelCategorias.style.transform = "translateX(-100%)";
    panelFiltros.style.transform = "translateX(100%)";
}

function abrirCategorias() {
    cerrarPaneles();
    overlayCatalogo.classList.add('visible');
    panelCategorias.style.transform = "translateX(0)";
}

function abrirFiltros() {
    cerrarPaneles();
    overlayCatalogo.classList.add('visible');
    panelFiltros.style.transform = "translateX(0)";
}

/* === LISTENERS === */

document.querySelector('[data-open="#panelCategorias"]')
    .addEventListener('click', abrirCategorias);

document.querySelector('[data-open="#panelFiltros"]')
    .addEventListener('click', abrirFiltros);

overlayCatalogo.addEventListener('click', cerrarPaneles);

window.addEventListener('keydown', e => {
    if (e.key === "Escape") cerrarPaneles();
});
