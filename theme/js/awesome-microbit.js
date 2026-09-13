// Loaded in the <head>: image load/error events don't bubble, but capturing listeners on the
// document see them all, including images that finish before the rest of the page is parsed.
function awesomeEntryOf(img) {
    var media = img.parentElement;
    return img.tagName === 'IMG' && media && media.classList.contains('awesome-entry__media')
        ? media.parentElement : null;
}

// Uses the picture as its own blurred backdrop. Set once loaded, as a CSS background would
// make the browser download every lazy-loaded image up front.
document.addEventListener('load', function (event) {
    var img = event.target, entry = awesomeEntryOf(img);
    if (!entry || entry.dataset.image !== 'picture') return;
    var src = (img.currentSrc || img.src).replace(/["\\]/g, '\\$&');
    img.parentElement.style.setProperty('--awesome-image', 'url("' + src + '")');
}, true);

// Images can still fail in the browser (e.g. hotlink protection), show the favicon instead
document.addEventListener('error', function (event) {
    var entry = awesomeEntryOf(event.target);
    if (entry) entry.dataset.image = 'none';
}, true);
