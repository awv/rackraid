// site-layout.js

document.addEventListener("DOMContentLoaded", function() {
    // 1. Inject Global Header
    const headerCanvas = document.getElementById('global-header');
    if (headerCanvas) {
        headerCanvas.innerHTML = `
            <div class="max-w-[1400px] mx-auto px-4 min-h-[70px] py-3 flex flex-wrap justify-between items-center gap-4 bg-slate-900 text-white shadow-md relative">
                
                <!-- Branding Cluster: Left Aligned -->
                <a href="index.html" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
                    <div class="flex items-center justify-center h-10 w-10 shrink-0">
                        <img src="assets/images/logo.png" class="h-full w-full object-contain" alt="Rack Raid Logo">
                    </div>
                    <div class="flex flex-col justify-center">
                        <h1 class="font-black text-lg sm:text-xl tracking-tight uppercase text-white m-0 p-0 leading-none">Rack Raid Archive</h1>
                        <p class="text-[10px] sm:text-xs text-slate-400 font-medium mt-1 mb-0 p-0 leading-none">Historical Course Guide & Analytics</p>
                    </div>
                </a>
                
                <!-- CSS-Driven Mobile Burger Trigger -->
                <label for="mobile-menu-toggle" class="sm:hidden flex flex-col justify-between w-6 h-4 cursor-pointer z-20 select-none">
                    <span class="w-full h-0.5 bg-slate-300 rounded-sm"></span>
                    <span class="w-full h-0.5 bg-slate-300 rounded-sm"></span>
                    <span class="w-full h-0.5 bg-slate-300 rounded-sm"></span>
                </label>
                <input type="checkbox" id="mobile-menu-toggle" class="peer hidden" />

                <!-- Navigation Matrix: Collapsed on Mobile, Flex on Desktop -->
                <nav class="hidden peer-checked:flex sm:flex flex-col sm:flex-row w-full sm:w-auto gap-2 sm:gap-1 bg-slate-800 p-2 sm:p-1 rounded-lg text-sm font-semibold items-stretch sm:items-center mt-2 sm:mt-0 transition-all duration-200">
                    <a href="index.html" id="nav-home" class="px-3 py-2 sm:py-1.5 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 sm:hover:bg-transparent transition-colors leading-none flex items-center justify-center sm:justify-start">Home</a>
                    <a href="stages-overview.html" id="nav-stages" class="px-3 py-2 sm:py-1.5 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 sm:hover:bg-transparent transition-colors leading-none flex items-center justify-center sm:justify-start">Stages</a>
                    <a href="stats.html" id="nav-stats" class="px-3 py-2 sm:py-1.5 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 sm:hover:bg-transparent transition-colors leading-none flex items-center justify-center sm:justify-start">Leaderboards</a>
                </nav>
            </div>
        `;
        
        // Automated highlighting rules based on current page filename
        const currentPath = window.location.pathname;
        const activeClass = "px-3 py-2 sm:py-1.5 rounded-md bg-emerald-500 text-slate-950 transition-colors leading-none flex items-center justify-center sm:justify-start font-bold";

        if (currentPath.includes('index.html') || currentPath.endsWith('/')) {
            const el = document.getElementById('nav-home');
            if (el) el.className = activeClass;
        } else if (currentPath.includes('stages-overview.html') || currentPath.includes('stage.html')) {
            const el = document.getElementById('nav-stages');
            if (el) el.className = activeClass;
        } else if (currentPath.includes('stats.html')) {
            const el = document.getElementById('nav-stats');
            if (el) el.className = activeClass;
        }
    }

    // 2. Inject Global Footer
    const footerCanvas = document.getElementById('global-footer');
    if (footerCanvas) {
        footerCanvas.innerHTML = `
            <div class="max-w-[1400px] mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4 text-center md:text-left">
                <p class="max-w-2xl leading-relaxed text-slate-500 m-0">
                    <strong>Archive Disclaimer:</strong> Raw dataset metrics are parsed programmatically from historical results documentation. If you discover an error, misaligned registration, or missing club tracking code, please file a correction patch via the workspace repository.
                </p>
                <p class="font-bold text-slate-600 m-0">© 2026 Rack Raid Hub</p>
            </div>
        `;
    }
});