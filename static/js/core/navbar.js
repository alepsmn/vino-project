console.log("navbar.js cargado");

const searchBtn = document.getElementById("btnSearch");
const searchSubnav = document.getElementById("searchSubnav");

if (searchBtn && searchSubnav) {

  // abrir / cerrar con la lupa
  searchBtn.addEventListener("click", e => {
    e.stopPropagation();
    const activo = searchSubnav.classList.toggle("activo");
    if (activo) {
      const input = searchSubnav.querySelector("input");
      input?.focus();
    }
  });

  // cerrar al hacer clic fuera
  document.addEventListener("click", e => {
    const clicFuera =
      searchSubnav.classList.contains("activo") &&
      !searchSubnav.contains(e.target) &&
      !searchBtn.contains(e.target);

    if (clicFuera) {
      searchSubnav.classList.remove("activo");
    }
  });
}

// === MENÚ LATERAL ===
console.log("menu lateral activo");

const menu = document.getElementById('menuLateral');
const overlay = document.getElementById('overlay');
const cerrar = document.getElementById('cerrarMenu');
const toggle = document.getElementById('menuToggle');

function toggleMenu(estado) {
  const activo = estado ?? !menu.classList.contains('activo');
  menu.classList.toggle('activo', activo);
  overlay.classList.toggle('visible', activo);
  document.body.style.overflow = activo ? 'hidden' : '';
}

toggle?.addEventListener('click', e => {
  e.stopPropagation();
  toggleMenu(true);
});

cerrar?.addEventListener('click', e => {
  e.stopPropagation();
  toggleMenu(false);
});

overlay?.addEventListener('click', e => {
  e.stopPropagation();
  toggleMenu(false);
});

// Evita cierre si haces clic dentro del propio menú
menu?.addEventListener('click', e => e.stopPropagation());

// --- Submenú lateral controlado por JS ---
// Submenú lateral simple y estable
document.querySelectorAll('.categoria').forEach(cat => {
  const sub = cat.querySelector('.subnivel');
  if (!sub) return;

  cat.addEventListener('mouseenter', () => {
    document.querySelectorAll('.subnivel.activo').forEach(s => s.classList.remove('activo'));
    sub.classList.add('activo');
  });

  cat.addEventListener('mouseleave', () => {
    setTimeout(() => {
      if (!cat.matches(':hover') && !sub.matches(':hover')) {
        sub.classList.remove('activo');
      }
    }, 150);
  });

  sub.addEventListener('mouseleave', () => sub.classList.remove('activo'));
});

