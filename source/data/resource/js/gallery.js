document.addEventListener('DOMContentLoaded', () => {
    const photoGrid = document.querySelector('.photo-grid');
    const genreFilter = document.getElementById('genre-filter');
    const yearFilter = document.getElementById('year-filter');
    const monthFilter = document.getElementById('month-filter');
    const photoCards = document.querySelectorAll('.photo-card');
    
    // Initialize Intersection Observer for infinite scrolling
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.1
    });

    // Observe all images
    document.querySelectorAll('.photo-image img').forEach(img => {
        observer.observe(img);
    });

    // Filter photos based on selected criteria
    function filterPhotos() {
        const selectedGenre = genreFilter.value;
        const selectedYear = yearFilter.value;
        const selectedMonth = monthFilter.value;

        photoCards.forEach(card => {
            const cardGenre = card.dataset.genre;
            const cardYear = card.dataset.year;
            const cardMonth = card.dataset.month;

            const genreMatch = !selectedGenre || cardGenre.includes(selectedGenre);
            const yearMatch = !selectedYear || cardYear === selectedYear;
            
            // Handle month matching with YYYY-MM format
            let monthMatch = true;
            if (selectedMonth) {
                const [selectedYear, selectedMonthNum] = selectedMonth.split('-');
                monthMatch = cardYear === selectedYear && cardMonth === selectedMonthNum;
            }

            card.style.display = genreMatch && yearMatch && monthMatch ? 'block' : 'none';
        });
    }

    // Update month options based on selected year
    function updateMonthOptions() {
        const selectedYear = yearFilter.value;
        const monthOptions = monthFilter.querySelectorAll('option:not([value=""])');
        
        monthOptions.forEach(option => {
            const [year] = option.value.split('-');
            option.style.display = !selectedYear || year === selectedYear ? 'block' : 'none';
        });
    }

    // Add event listeners
    genreFilter.addEventListener('change', filterPhotos);
    yearFilter.addEventListener('change', () => {
        updateMonthOptions();
        filterPhotos();
    });
    monthFilter.addEventListener('change', filterPhotos);

    // Initialize month options
    updateMonthOptions();
}); 