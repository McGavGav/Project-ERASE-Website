(function () {
    const buttons = document.querySelectorAll('.tab-btn');
    const panes   = document.querySelectorAll('.tab-content');

    function activateTab(tabId) {
        buttons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabId));
        panes.forEach(pane => pane.classList.toggle('active', pane.id === 'tab-' + tabId));
    }

    buttons.forEach(btn => {
        btn.addEventListener('click', () => activateTab(btn.dataset.tab));
    });

    // Initial tab: prefer context set active_tab (handles form errors), then URL param
    const serverTab = "{{ active_tab }}";
    const urlTab    = new URLSearchParams(window.location.search).get('tab');
    activateTab(urlTab || serverTab || 'fundraising');
})();