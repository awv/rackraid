// site-layout.js

document.addEventListener("DOMContentLoaded", function() {
    // 1. Inject Global Header
    const headerCanvas = document.getElementById('global-header');
    if (headerCanvas) {
        headerCanvas.innerHTML = `
            <div class="max-w-[1400px] mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-900 text-white rounded-xl mt-4 shadow-md">
                <a href="index.html" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
                    <div class="bg-emerald-500 p-2 rounded-lg text-slate-900 font-bold text-xl tracking-wider flex items-center justify-center h-10 w-10">RR</div>
                    <div class="flex flex-col justify-center">
                        <h1 class="font-black text-xl tracking-tight uppercase text-white m-0 p-0 leading-none">Rack Raid Archive</h1>
                        <p class="text-xs text-slate-400 font-medium mt-1 mb-0 p-0 leading-none">Historical Course Guide & Analytics</p>
                    </div>
                </a>
                <nav class="flex gap-1 bg-slate-800 p-1 rounded-lg text-sm font-semibold items-center h-max">
                    <a href="index.html" id="nav-home" class="px-3 py-1.5 rounded-md text-slate-300 hover:text-white transition-colors leading-none flex items-center">Home</a>
                    <a href="stages-overview.html" id="nav-stages" class="px-3 py-1.5 rounded-md text-slate-300 hover:text-white transition-colors leading-none flex items-center">Stages</a>
                    <a href="stats.html" id="nav-stats" class="px-3 py-1.5 rounded-md text-slate-300 hover:text-white transition-colors leading-none flex items-center">Leaderboards</a>
                </nav>
            </div>
        `;
        
        // Automated highlighting rules based on current page filename
        const currentPath = window.location.pathname;
        const activeClass = "px-3 py-1.5 rounded-md bg-emerald-500 text-slate-950 transition-colors leading-none flex items-center";

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