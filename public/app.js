/**
 * Podcast Radar - Lógica de Aplicación
 * Vista Compacta de Lectura Rápida + Explorador por Canales
 */

const STORAGE_KEY = 'podcast_radar_seen_episodes';

// Estado
let allPodcasts = [];
let activeSection = 'feed'; // 'feed' | 'channels'
let selectedTheme = 'all';
let selectedChannel = null;
let searchQuery = '';
let viewMode = 'unseen'; // 'unseen' | 'seen'
let seenIds = new Set();

// Persistencia en LocalStorage
function loadSeenState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) seenIds = new Set(JSON.parse(raw));
  } catch (e) {
    seenIds = new Set();
  }
}

function saveSeenState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...seenIds]));
  } catch (e) {
    console.error('Error guardando en localStorage:', e);
  }
  updateCounters();
}

function toggleSeen(id, event) {
  if (event) event.stopPropagation();
  
  if (seenIds.has(id)) {
    seenIds.delete(id);
  } else {
    seenIds.add(id);
  }
  saveSeenState();
  renderApp();
}

function toggleViewMode() {
  viewMode = viewMode === 'unseen' ? 'seen' : 'unseen';
  
  const toggleBtn = document.getElementById('toggle-view-btn');
  const toggleLabel = document.getElementById('toggle-label');
  const viewBanner = document.getElementById('view-banner');
  
  if (viewMode === 'seen') {
    toggleBtn.classList.add('bg-emerald-500/20', 'border-emerald-500/40', 'text-emerald-300');
    toggleLabel.textContent = 'Pendientes';
    viewBanner.classList.remove('hidden');
    viewBanner.classList.add('flex');
  } else {
    toggleBtn.classList.remove('bg-emerald-500/20', 'border-emerald-500/40', 'text-emerald-300');
    toggleLabel.textContent = 'Vistos';
    viewBanner.classList.add('hidden');
    viewBanner.classList.remove('flex');
  }
  
  renderApp();
}

// Cambiar entre Pestaña Feed y Por Canal
function switchNavSection(section) {
  activeSection = section;
  
  const tabFeed = document.getElementById('nav-tab-feed');
  const tabChannels = document.getElementById('nav-tab-channels');
  const feedControls = document.getElementById('feed-controls');
  const feedSec = document.getElementById('feed-section');
  const channelsSec = document.getElementById('channels-section');
  
  if (section === 'feed') {
    tabFeed.className = 'py-1.5 text-xs font-semibold rounded-lg bg-slate-800 text-white shadow-sm flex items-center justify-center gap-1.5 transition-all';
    tabChannels.className = 'py-1.5 text-xs font-medium rounded-lg text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5 transition-all';
    feedControls.classList.remove('hidden');
    feedSec.classList.remove('hidden');
    channelsSec.classList.add('hidden');
  } else {
    tabChannels.className = 'py-1.5 text-xs font-semibold rounded-lg bg-slate-800 text-white shadow-sm flex items-center justify-center gap-1.5 transition-all';
    tabFeed.className = 'py-1.5 text-xs font-medium rounded-lg text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5 transition-all';
    feedControls.classList.add('hidden');
    feedSec.classList.add('hidden');
    channelsSec.classList.remove('hidden');
  }
  
  renderApp();
}

// Filtro por temática
function selectTheme(theme) {
  selectedTheme = theme;
  document.querySelectorAll('.theme-chip').forEach(chip => {
    const chipTheme = chip.getAttribute('data-theme');
    if (chipTheme === theme) {
      chip.className = 'theme-chip px-2.5 py-1 rounded-md text-xs font-semibold shrink-0 bg-emerald-500 text-slate-950 transition-all';
    } else {
      chip.className = 'theme-chip px-2.5 py-1 rounded-md text-xs font-medium shrink-0 bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800 transition-all';
    }
  });
  renderApp();
}

// Búsqueda
function handleSearch(val) {
  searchQuery = val.trim().toLowerCase();
  const clearBtn = document.getElementById('clear-search');
  if (clearBtn) {
    if (searchQuery.length > 0) clearBtn.classList.remove('hidden');
    else clearBtn.classList.add('hidden');
  }
  renderApp();
}

function clearSearch() {
  const input = document.getElementById('search-input');
  if (input) input.value = '';
  searchQuery = '';
  document.getElementById('clear-search').classList.add('hidden');
  renderApp();
}

function resetFilters() {
  searchQuery = '';
  const input = document.getElementById('search-input');
  if (input) input.value = '';
  document.getElementById('clear-search').classList.add('hidden');
  selectTheme('all');
  selectedChannel = null;
  if (viewMode === 'seen') toggleViewMode();
}

// Filtrar canal directamente desde una tarjeta o sección
function openChannelDetail(channelName) {
  selectedChannel = channelName;
  switchNavSection('channels');
  
  const container = document.getElementById('channel-episodes-container');
  const title = document.getElementById('selected-channel-title');
  if (container && title) {
    container.classList.remove('hidden');
    title.innerHTML = `<i data-lucide="tv" class="w-4 h-4 text-emerald-400"></i> ${escapeHtml(channelName)}`;
  }
  renderApp();
  
  // Desplazar suavemente hacia la lista del canal
  if (container) {
    container.scrollIntoView({ behavior: 'smooth' });
  }
}

function closeChannelDetail() {
  selectedChannel = null;
  const container = document.getElementById('channel-episodes-container');
  if (container) container.classList.add('hidden');
  renderChannelsGrid();
}

// Renderizado de Tarjeta Compacta (Sin Imagen, Enfoque Lectura de Contenido)
function renderCard(podcast) {
  const isSeen = seenIds.has(podcast.id);
  
  // Categoría compacta
  let themeBadge = 'bg-slate-800/80 text-slate-300 border-slate-700/80';
  if (podcast.theme.includes('Inteligencia')) {
    themeBadge = 'bg-purple-950/40 text-purple-300 border-purple-800/40';
  } else if (podcast.theme.includes('Ciencia')) {
    themeBadge = 'bg-cyan-950/40 text-cyan-300 border-cyan-800/40';
  } else if (podcast.theme.includes('Negocios')) {
    themeBadge = 'bg-amber-950/40 text-amber-300 border-amber-800/40';
  }

  return `
    <article id="card-${podcast.id}" class="bg-slate-900 border border-slate-800/90 rounded-xl p-3.5 space-y-2.5 transition-all hover:border-slate-700">
      <!-- Fila Superior: Canal (Clickeable), Duración, Categoría y Fecha -->
      <div class="flex items-center justify-between gap-2 text-[11px] flex-wrap">
        <div class="flex items-center gap-1.5 flex-wrap">
          <!-- Canal con botón directo para ver más de este canal -->
          <button 
            onclick="openChannelDetail('${escapeHtml(podcast.channel)}')" 
            class="font-semibold text-emerald-400 hover:text-emerald-300 hover:underline flex items-center gap-1 transition-colors"
            title="Ver más videos de ${escapeHtml(podcast.channel)}"
          >
            <i data-lucide="tv" class="w-3 h-3"></i>
            <span>${escapeHtml(podcast.channel)}</span>
          </button>
          
          <span class="text-slate-600">•</span>
          
          <!-- Badge de Duración -->
          <span class="font-bold text-white bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60 flex items-center gap-1">
            <i data-lucide="clock" class="w-3 h-3 text-emerald-400"></i>
            ${podcast.duration}
          </span>
          
          <!-- Categoría -->
          <span class="px-2 py-0.5 rounded border text-[10px] ${themeBadge}">
            ${escapeHtml(podcast.theme)}
          </span>
        </div>

        <!-- Fecha -->
        <span class="text-[10px] text-slate-500 font-medium">
          ${podcast.published_at}
        </span>
      </div>

      <!-- Título Conciso -->
      <h3 class="text-sm font-bold text-white leading-snug">
        ${escapeHtml(podcast.title)}
      </h3>

      <!-- Resumen Real del Contenido (Qué se habla y conclusiones) -->
      <p class="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/50">
        ${escapeHtml(podcast.summary)}
      </p>

      <!-- Fila de Acciones: Link Directo a YouTube + Botón Visto -->
      <div class="pt-1 flex items-center justify-between gap-2 border-t border-slate-800/60">
        <a 
          href="${podcast.url}" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 hover:text-emerald-300 hover:underline py-1"
        >
          <span>Abrir en YouTube</span>
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
        </a>

        <button 
          onclick="toggleSeen('${podcast.id}', event)" 
          class="px-2.5 py-1 text-xs rounded-lg border transition-all flex items-center gap-1 ${
            isSeen 
              ? 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white' 
              : 'bg-slate-800/90 text-slate-200 border-slate-700 hover:bg-slate-700'
          }"
        >
          <i data-lucide="${isSeen ? 'rotate-ccw' : 'check'}" class="w-3.5 h-3.5 ${isSeen ? 'text-slate-400' : 'text-emerald-400'}"></i>
          <span>${isSeen ? 'Desmarcar' : 'Marcar visto'}</span>
        </button>
      </div>
    </article>
  `;
}

// Renderizar Sección Por Canales (Agrupador)
function renderChannelsGrid() {
  const grid = document.getElementById('channels-grid');
  if (!grid) return;
  
  // Agrupar canales y contar episodios
  const channelMap = {};
  allPodcasts.forEach(p => {
    const ch = p.channel;
    if (!channelMap[ch]) {
      channelMap[ch] = {
        name: ch,
        theme: p.theme,
        total: 0,
        unseen: 0
      };
    }
    channelMap[ch].total++;
    if (!seenIds.has(p.id)) channelMap[ch].unseen++;
  });

  const channelsList = Object.values(channelMap).sort((a, b) => b.total - a.total);
  
  const countLabel = document.getElementById('channels-count-label');
  if (countLabel) countLabel.textContent = `${channelsList.length} canales disponibles`;

  grid.innerHTML = channelsList.map(ch => {
    const isSelected = selectedChannel === ch.name;
    return `
      <div 
        onclick="openChannelDetail('${escapeHtml(ch.name)}')" 
        class="cursor-pointer p-3 rounded-xl border transition-all ${
          isSelected 
            ? 'bg-slate-800 border-emerald-500 shadow-md' 
            : 'bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
        }"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <i data-lucide="tv" class="w-3.5 h-3.5"></i>
            </div>
            <div>
              <h4 class="text-xs font-bold text-white">${escapeHtml(ch.name)}</h4>
              <p class="text-[10px] text-slate-400">${escapeHtml(ch.theme)}</p>
            </div>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-800 text-emerald-400 border border-slate-700">
            ${ch.unseen} / ${ch.total}
          </span>
        </div>
      </div>
    `;
  }).join('');
}

// Renderizar Feed Principal y Vistas
function renderApp() {
  const container = document.getElementById('podcasts-container');
  const emptyState = document.getElementById('empty-state');
  
  updateCounters();
  
  // 1. Filtrar para el Feed
  const filteredFeed = allPodcasts.filter(podcast => {
    const isSeen = seenIds.has(podcast.id);
    if (viewMode === 'unseen' && isSeen) return false;
    if (viewMode === 'seen' && !isSeen) return false;
    
    if (selectedTheme !== 'all' && podcast.theme !== selectedTheme) return false;
    
    if (searchQuery) {
      const matchTitle = podcast.title.toLowerCase().includes(searchQuery);
      const matchChannel = podcast.channel.toLowerCase().includes(searchQuery);
      const matchSummary = podcast.summary.toLowerCase().includes(searchQuery);
      if (!matchTitle && !matchChannel && !matchSummary) return false;
    }
    
    return true;
  });

  if (container) {
    if (filteredFeed.length === 0) {
      container.innerHTML = '';
      if (activeSection === 'feed') emptyState.classList.remove('hidden');
    } else {
      emptyState.classList.add('hidden');
      container.innerHTML = filteredFeed.map(renderCard).join('');
    }
  }

  // 2. Renderizar Canales
  renderChannelsGrid();

  // 3. Renderizar Detalle de Canal Seleccionado
  const channelListEl = document.getElementById('channel-episodes-list');
  const channelContainerEl = document.getElementById('channel-episodes-container');
  if (selectedChannel && channelListEl && channelContainerEl) {
    channelContainerEl.classList.remove('hidden');
    const channelEps = allPodcasts.filter(p => {
      const isSeen = seenIds.has(p.id);
      if (viewMode === 'unseen' && isSeen) return false;
      if (viewMode === 'seen' && !isSeen) return false;
      return p.channel.toLowerCase() === selectedChannel.toLowerCase();
    });

    if (channelEps.length === 0) {
      channelListEl.innerHTML = `
        <p class="text-xs text-slate-500 py-4 text-center">
          No hay episodios pendientes para ${escapeHtml(selectedChannel)} en este modo.
        </p>
      `;
    } else {
      channelListEl.innerHTML = channelEps.map(renderCard).join('');
    }
  }

  // Refrescar íconos Lucide
  if (window.lucide) window.lucide.createIcons();
}

function updateCounters() {
  const seenCount = seenIds.size;
  const totalCount = allPodcasts.length;
  const pendingCount = totalCount - seenCount;
  
  const badge = document.getElementById('seen-count-badge');
  if (badge) badge.textContent = seenCount;
  
  const totalFeed = document.getElementById('total-feed-count');
  if (totalFeed) totalFeed.textContent = `(${pendingCount})`;

  const channelsCount = document.getElementById('total-channels-count');
  const uniqueChannels = new Set(allPodcasts.map(p => p.channel)).size;
  if (channelsCount) channelsCount.textContent = `(${uniqueChannels})`;
  
  const statusEl = document.getElementById('footer-summary-status');
  if (statusEl) statusEl.textContent = `${pendingCount} episodios disponibles`;
  
  const seenStatsEl = document.getElementById('footer-seen-stats');
  if (seenStatsEl) seenStatsEl.textContent = `${seenCount} vistos`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

async function init() {
  loadSeenState();
  try {
    let res = await fetch('data/podcasts.json');
    if (!res.ok) res = await fetch('../data/podcasts.json');
    if (res.ok) {
      allPodcasts = await res.json();
    }
  } catch (e) {
    console.error('Error cargando podcasts:', e);
  }
  renderApp();
}

document.addEventListener('DOMContentLoaded', init);
