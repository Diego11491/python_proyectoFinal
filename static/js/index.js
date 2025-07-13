// Animación de contadores
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    updateCounter();
}

// Iniciar animaciones cuando sea visible
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Datos de ejemplo - reemplazar con datos reales del servidor
            animateCounter(document.getElementById('total-students'), 247);
            animateCounter(document.getElementById('avg-grade'), 16.8);
            animateCounter(document.getElementById('passed-students'), 189);
            animateCounter(document.getElementById('active-courses'), 12);
            
            observer.unobserve(entry.target);
        }
    });
});

observer.observe(document.querySelector('.stats-preview'));

// Efecto parallax suave para elementos flotantes
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const shapes = document.querySelectorAll('.floating-shape');
    
    shapes.forEach((shape, index) => {
        const speed = 0.5 * (index + 1);
        shape.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

// Animación de entrada para las tarjetas
const cards = document.querySelectorAll('.feature-card');
const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
});

cards.forEach(card => {
    cardObserver.observe(card);
});