// navbar.js
const header = document.querySelector('.navbar');
const menuToggle = document.getElementById('menuToggle');
const cerrarMenu = document.getElementById('cerrarMenu');
const menuLateral = document.getElementById('menuLateral');
const overlay = document.getElementById('overlay');
const btnSearch = document.getElementById('btnSearch');
const searchSubnav = document.getElementById('searchSubnav');

let lastScrollY = window.scrollY;
let navHidden = false;

function abrirOverlay(contexto) {
    if (!overlay) return;
    overlay.classList.add('visible');
    overlay.dataset.contexto = contexto;
}

function cerrarOverlay() {
    if (!overlay) return;
    overlay.classList.remove('visible');
    delete overlay.dataset.contexto;
}

// Menú lateral
if (menuToggle && menuLateral) {
    menuToggle.addEventListener('click', () => {
        menuLateral.classList.add('abierto');
        abrirOverlay('menu');
    });
}

if (cerrarMenu && menuLateral) {
    cerrarMenu.addEventListener('click', () => {
        menuLateral.classList.remove('abierto');
        cerrarOverlay();
    });
}

// Búsqueda
if (btnSearch && searchSubnav) {
    btnSearch.addEventListener('click', () => {
        const visible = searchSubnav.classList.toggle('visible');
        if (visible) abrirOverlay('search');
        else cerrarOverlay();
    });
}

// Cerrar al clicar overlay
if (overlay) {
    overlay.addEventListener('click', () => {
        const ctx = overlay.dataset.contexto;
        if (ctx === 'menu' && menuLateral) {
            menuLateral.classList.remove('abierto');
        }
        if (ctx === 'search' && searchSubnav) {
            searchSubnav.classList.remove('visible');
        }
        cerrarOverlay();
    });
}

// Scroll: ocultar / mostrar nav + subnav + barra búsqueda
window.addEventListener('scroll', () => {
    const current = window.scrollY;
    const delta = current - lastScrollY;

    // margen mínimo para evitar parpadeo
    if (Math.abs(delta) < 10) return;

    if (current > 80 && delta > 0 && !navHidden) {
        document.body.classList.add('nav-hidden');
        navHidden = true;
    } else if (delta < 0 && navHidden) {
        document.body.classList.remove('nav-hidden');
        navHidden = false;
    }

    lastScrollY = current;
});

// Escape cierra todo
window.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;

    if (menuLateral && menuLateral.classList.contains('abierto')) {
        menuLateral.classList.remove('abierto');
    }
    if (searchSubnav && searchSubnav.classList.contains('visible')) {
        searchSubnav.classList.remove('visible');
    }
    cerrarOverlay();
});
