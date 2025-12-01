const slides = document.querySelectorAll("#carruselMatriz .slide")
let idx = 0

function rotar() {
    slides.forEach(s => s.classList.remove("activa"))
    slides[idx].classList.add("activa")
    idx = (idx + 1) % slides.length
}

if (slides.length > 0) {
    slides[0].classList.add("activa")
    setInterval(rotar, 4000)
}

document.querySelectorAll("[data-carrusel]").forEach(carrusel => {
    const track = carrusel.querySelector(".car-track")
    const prev = carrusel.querySelector("[data-prev]")
    const next = carrusel.querySelector("[data-next]")

    prev.addEventListener("click", () => {
        track.scrollLeft -= 200
    })

    next.addEventListener("click", () => {
        track.scrollLeft += 200
    })
})
