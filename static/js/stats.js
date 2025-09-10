function showStats() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach((counter, index) => {
        const target = parseInt(counter.getAttribute('data-target'));
        
        if (target > 0) {
            counter.textContent = target;
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    showStats();
});

window.addEventListener('load', function() {
    showStats();
});
