/* ============================================================
   ELEMENTOS
   ============================================================ */

const menuToggle = document.getElementById("menuToggle");
const menuLateral = document.getElementById("menuLateral");
const cerrarMenu = document.getElementById("cerrarMenu");

const btnSearch = document.getElementById("btnSearch");
const searchSubnav = document.getElementById("searchSubnav");

const panelCategorias = document.getElementById("panelCategorias");
const panelFiltros = document.getElementById("panelFiltros");

const overlayGlobal = document.getElementById("overlayGlobal");
const overlayCatalogo = document.getElementById("overlayCatalogo");


/* ============================================================
   SCROLL LOCK
   ============================================================ */
let scrollPos = 0;

function bloquearScroll() {
    scrollPos = window.scrollY;

    // Evita scroll anchoring
    document.documentElement.style.overflowAnchor = "none";

    // Marca bloqueo (sin repintar nada antes)
    document.documentElement.classList.add("bloqueado");
    document.body.classList.add("bloqueado");

    // Mantiene el scroll fijo sin saltos
    document.documentElement.scrollTop = scrollPos;
    document.body.scrollTop = scrollPos;
}


function desbloquearScroll() {
    document.documentElement.classList.remove("bloqueado");
    document.body.classList.remove("bloqueado");

    // Restablece scroll anchoring
    document.documentElement.style.overflowAnchor = "";

    window.scrollTo(0, scrollPos);
}

/* ============================================================
   TOOLS: TOP DINÁMICO DEL OVERLAY
   ============================================================ */
function syncOverlayTop(overlayEl) {
    const cs = getComputedStyle(document.documentElement);
    const navH = cs.getPropertyValue("--navbar-altura").trim();
    const subnavH = cs.getPropertyValue("--subnav-altura").trim();

    if (document.body.classList.contains("tiene-subnav")) {
        overlayEl.style.top = `calc(${navH} + ${subnavH})`;
    } else {
        overlayEl.style.top = navH;
    }
}

/* ============================================================
   CIERRES
   ============================================================ */

function cerrarMenuLateral() {
    menuLateral?.classList.remove("abierto");
}
function cerrarSearch() {
    searchSubnav?.classList.remove("visible");
    document.body.classList.remove("search-abierta");
}


function cerrarPanelesCatalogo() {
    panelCategorias?.classList.remove("abierto");
    panelFiltros?.classList.remove("abierto");
    overlayCatalogo?.classList.remove("visible");
}

function cerrarTodoGlobal() {
    cerrarMenuLateral();
    cerrarSearch();
    cerrarPanelesCatalogo();
    overlayGlobal.classList.remove("visible");
    document.body.classList.remove("search-abierta");
    desbloquearScroll();
}

/* ============================================================
   MENÚ HAMBURGUESA
   ============================================================ */

menuToggle?.addEventListener("click", () => {
    cerrarSearch();
    cerrarPanelesCatalogo();

    syncOverlayTop(overlayGlobal);
    overlayGlobal.classList.add("visible");

    menuLateral.classList.add("abierto");
    bloquearScroll();
});

cerrarMenu?.addEventListener("click", cerrarTodoGlobal);
overlayGlobal?.addEventListener("click", cerrarTodoGlobal);


/* ============================================================
   SEARCH SUBNAV (LUPA)
   ============================================================ */

btnSearch?.addEventListener("click", () => {
    cerrarMenuLateral();
    cerrarPanelesCatalogo();

    const visible = searchSubnav.classList.toggle("visible");

    if (visible) {
        // 1. Marca búsqueda abierta
        document.body.classList.add("search-abierta");

        // 2. IMPORTANTE: fuerza que la navbar vuelva ANTES de bloquear scroll
        document.body.classList.remove("nav-hidden");

        // 3. Fuerza repaint para que sticky y transform se apliquen YA
        void document.body.offsetHeight;

        // 4. Ahora calcula correctamente el overlay
        syncOverlayTop(overlayGlobal);

        // 5. Muestra overlay
        overlayGlobal.classList.add("visible");

        // 6. Ahora sí se puede bloquear scroll (con navbar en el sitio)
        bloquearScroll();
    } else {
        document.body.classList.remove("search-abierta");
        overlayGlobal.classList.remove("visible");
        desbloquearScroll();
    }
});


document.addEventListener("click", e => {
    if (!searchSubnav?.classList.contains("visible")) return;

    const insideSearch = searchSubnav.contains(e.target);
    const onBtn = btnSearch.contains(e.target);

    if (!insideSearch && !onBtn) {
        cerrarSearch();
        overlayGlobal.classList.remove("visible");
        desbloquearScroll();
    }
});

/* ============================================================
   PANEL CATEGORÍAS / FILTROS
   ============================================================ */

function abrirPanel(panel) {
    cerrarSearch();
    cerrarMenuLateral();

    syncOverlayTop(overlayCatalogo);
    overlayCatalogo.classList.add("visible");

    panel.classList.add("abierto");
    bloquearScroll();
}

overlayCatalogo?.addEventListener("click", () => {
    cerrarPanelesCatalogo();
    desbloquearScroll();
});

document.querySelectorAll("[data-open]").forEach(btn => {
    btn.addEventListener("click", () => {
        const panel = document.querySelector(btn.dataset.open);
        abrirPanel(panel);
    });
});


/* ============================================================
   NAVBAR: OCULTAR EN SCROLL
   ============================================================ */

let ultimaPos = 0;
let acumulado = 0;

window.addEventListener("scroll", () => {
    if (document.body.classList.contains("bloqueado")) return;

    const pos = window.scrollY;
    const delta = pos - ultimaPos;

    acumulado += delta;

    if (acumulado > 50) {
        document.body.classList.add("nav-hidden");
        acumulado = 0;
    }

    if (acumulado < -25) {
        document.body.classList.remove("nav-hidden");
        acumulado = 0;
    }

    ultimaPos = pos;
});
