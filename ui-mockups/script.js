// Navigation between mockup sections
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.mockup-section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                // Scroll to top of mockup container
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    });
    
    // Initialize first section as active
    if (sections.length > 0) {
        sections[0].classList.add('active');
    }
    
    // Add interactivity to table rows
    const tableRows = document.querySelectorAll('.anomalies-table tbody tr, .related-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on checkbox or button
            if (e.target.type !== 'checkbox' && e.target.tagName !== 'BUTTON') {
                const viewButton = this.querySelector('.btn-link');
                if (viewButton) {
                    viewButton.click();
                }
            }
        });
        
        row.style.cursor = 'pointer';
    });
    
    // Add hover effects to summary cards
    const summaryCards = document.querySelectorAll('.summary-card');
    summaryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        });
    });
    
    // Simulate chart interactions
    const chartPlaceholders = document.querySelectorAll('.chart-placeholder');
    chartPlaceholders.forEach(chart => {
        chart.addEventListener('click', function() {
            console.log('Chart clicked - would show interactive chart in production');
        });
    });
    
    // Add tooltip functionality (basic)
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.position = 'absolute';
            tooltip.style.background = '#333';
            tooltip.style.color = 'white';
            tooltip.style.padding = '5px 10px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '12px';
            tooltip.style.zIndex = '1000';
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - 30) + 'px';
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
    
    // Pagination handlers
    const pageButtons = document.querySelectorAll('.page-btn');
    pageButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            pageButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Filter panel interactions
    const applyButton = document.querySelector('.filters-panel .btn-primary');
    if (applyButton) {
        applyButton.addEventListener('click', function() {
            console.log('Filters applied - would update table/charts in production');
            alert('In production, this would filter the anomalies table and update charts.');
        });
    }
    
    const exportButton = document.querySelector('.filters-panel .btn-secondary:last-child');
    if (exportButton && exportButton.textContent.includes('Export')) {
        exportButton.addEventListener('click', function() {
            console.log('Export clicked - would download CSV in production');
            alert('In production, this would download a CSV file with filtered results.');
        });
    }
    
    // Store selector change handler
    const storeSelect = document.querySelector('.store-select');
    if (storeSelect) {
        storeSelect.addEventListener('change', function() {
            console.log('Store changed:', this.value);
            alert('In production, this would update all charts and metrics for the selected store.');
        });
    }
    
    // View Details button handlers
    const viewDetailsButtons = document.querySelectorAll('.btn-link');
    viewDetailsButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            console.log('View Details clicked - would navigate to detail view');
            // In production, this would navigate to the anomaly detail page
            const detailSection = document.getElementById('anomaly-detail');
            if (detailSection) {
                // Switch to detail view
                document.querySelectorAll('.mockup-section').forEach(s => s.classList.remove('active'));
                detailSection.classList.add('active');
                
                // Update nav
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                document.querySelector('a[href="#anomaly-detail"]').classList.add('active');
                
                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    });
});
