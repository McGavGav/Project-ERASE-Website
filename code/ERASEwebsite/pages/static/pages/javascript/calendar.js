const config = JSON.parse(document.getElementById('calendar-config').textContent);
const rsvpedIds = new Set(JSON.parse(document.getElementById('rsvped-ids-data').textContent));

function openModal() {
    document.getElementById('event-modal-overlay').classList.add('open');
}

function closeModal() {
    document.getElementById('event-modal-overlay').classList.remove('open');
}

document.getElementById('event-modal-overlay')?.addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

function openEventDetailModal(pill) {
    const eventId = pill.dataset.eventId;
    const title = pill.dataset.title;
    const time = pill.dataset.time;
    const desc = pill.dataset.description;
    const hasRsvp = pill.dataset.hasRsvp === 'true';

    document.getElementById('detail-title').textContent = title;
    document.getElementById('detail-time').textContent = time;
    document.getElementById('detail-description').textContent = desc;

    const rsvpForm = document.getElementById('rsvp-form');
    const rsvpBtn = document.getElementById('rsvp-btn');

    if (hasRsvp && config.isAuthenticated) {
        rsvpForm.action = config.rsvpUrlTemplate.replace('/0/', `/${eventId}/`);
        rsvpForm.style.display = 'block';

        if (rsvpedIds.has(parseInt(eventId))) {
            rsvpBtn.textContent = config.labelCancelRsvp;
            rsvpBtn.classList.add('rsvped');
        } else {
            rsvpBtn.textContent = config.labelRsvp;
            rsvpBtn.classList.remove('rsvped');
        }
    } else {
        rsvpForm.style.display = 'none';
    }

    document.getElementById('event-detail-overlay').classList.add('open');
}

function closeEventDetailModal() {
    document.getElementById('event-detail-overlay').classList.remove('open');
}

document.getElementById('event-detail-overlay')?.addEventListener('click', function(e) {
    if (e.target === this) closeEventDetailModal();
});