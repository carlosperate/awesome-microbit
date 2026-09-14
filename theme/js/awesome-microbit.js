// Loaded in the <head>: image load/error events don't bubble, but capturing listeners on the
// document see them all, including images that finish before the rest of the page is parsed.
function awesomeEntryOf(img) {
    var media = img.parentElement;
    return img.tagName === 'IMG' && media && media.classList.contains('awesome-entry__media')
        ? media.parentElement : null;
}

// The picture is the frame's blurred backdrop and the card's hover glow. Set once loaded, as a
// CSS background would make the browser download every lazy-loaded image up front.
document.addEventListener('load', function (event) {
    var img = event.target, entry = awesomeEntryOf(img);
    if (!entry || entry.dataset.image !== 'picture') return;
    var src = (img.currentSrc || img.src).replace(/["\\]/g, '\\$&');
    entry.style.setProperty('--awesome-image', 'url("' + src + '")');
}, true);

// Images can still fail in the browser (e.g. hotlink protection), show the favicon instead
document.addEventListener('error', function (event) {
    var entry = awesomeEntryOf(event.target);
    if (entry) entry.dataset.image = 'none';
}, true);

// Moves the hover glow with the pointer
document.addEventListener('pointermove', function (event) {
    var entry = event.target.closest && event.target.closest('.awesome-list--media .awesome-entry');
    if (!entry) return;
    var rect = entry.getBoundingClientRect();
    entry.style.setProperty('--awesome-x', (event.clientX - rect.left) + 'px');
    entry.style.setProperty('--awesome-y', (event.clientY - rect.top) + 'px');
}, {passive: true});

// The open menu pushes the page down, so close it before jumping to a table of contents entry
document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('.navbar-toc a');
    var menu = document.getElementById('navbar-collapse');
    var target = link && document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (!target || !menu.classList.contains('show')) return;
    event.preventDefault();
    menu.addEventListener('hidden.bs.collapse', function () {
        history.pushState(null, '', link.hash);
        target.scrollIntoView();
    }, {once: true});
    bootstrap.Collapse.getOrCreateInstance(menu).hide();
});
