// Loaded in the <head>: image load/error events don't bubble, but capturing listeners on the
// document see them all, including images that finish before the rest of the page is parsed.
function awesomeEntryOf(img) {
    var media = img.parentElement;
    return img.tagName === 'IMG' && media && media.classList.contains('awesome-entry__media')
        ? media.parentElement : null;
}

// The picture is also the frame's blurred backdrop. Set once loaded, as a CSS background would
// make the browser download every lazy-loaded image up front.
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

// Moves the bright part of the hover shadow with the pointer, on cards and Contents tiles
document.addEventListener('pointermove', function (event) {
    var entry = event.target.closest && event.target.closest('.awesome-list--media .awesome-entry, .awesome-contents__tile');
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

// The hue of a section with lists, for elements outside it; the others keep the site's purple
function awesomeSectionHue(section) {
    return section && section.querySelector('.awesome-list')
        ? getComputedStyle(section).getPropertyValue('--awesome-section-hue') : '';
}

// Sidebar and phone menu entries take their section's colour, for the current section's style in extend.css
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('#toc-collapse .nav-link, .navbar-toc .nav-link').forEach(function (link) {
        var heading = document.getElementById(decodeURIComponent(link.hash.slice(1)));
        var hue = awesomeSectionHue(heading && heading.closest('.awesome-section'));
        if (hue) link.style.setProperty('--awesome-section-hue', hue);
    });
});

// The bar under the navbar (content.html) names the section the scrollspy (js/base.js) finds, and
// its line shows how far down the page that is
document.addEventListener('DOMContentLoaded', function () {
    var where = document.querySelector('.awesome-where');
    if (!where) return;
    var bar = where.firstElementChild, current = null;
    var menuLinks = document.querySelectorAll('.navbar-toc .nav-link');

    document.addEventListener('scrollspy', function (event) {
        var heading = event.detail ? document.getElementById(event.detail) : null;
        // Above the first section there's nothing to name
        var section = heading && heading.tagName === 'H2' ? heading.closest('.awesome-section') : null;
        var scrollable = document.documentElement.scrollHeight - window.innerHeight;
        where.classList.toggle('awesome-where--shown', !!section);
        bar.style.setProperty('--awesome-where-progress', scrollable > 0 ? window.scrollY / scrollable : 0);
        if (section === current) return;
        current = section;
        menuLinks.forEach(function (link) {
            link.classList.toggle('active', !!section && link.hash === '#' + heading.id);
        });
        // While it fades out, it keeps the last section
        if (!section) return;
        var count = section.querySelectorAll('.awesome-entry').length, hue = awesomeSectionHue(section);
        bar.href = '#' + heading.id;
        if (hue) bar.style.setProperty('--awesome-section-hue', hue);
        else bar.style.removeProperty('--awesome-section-hue');
        where.querySelector('.awesome-where__name').textContent = heading.textContent;
        where.querySelector('.awesome-where__count').textContent = count ? count + ' resource' + (count === 1 ? '' : 's') : '';
    });

    // Phones have no sidebar, so the bar opens the menu at the current section instead of jumping
    bar.addEventListener('click', function (event) {
        var toc = document.querySelector('.navbar-toc');
        var entry = toc && toc.querySelector('.nav-link.active');
        if (!entry || getComputedStyle(toc).display === 'none') return;
        event.preventDefault();
        var menu = document.getElementById('navbar-collapse');
        menu.addEventListener('shown.bs.collapse', function () {
            menu.scrollTop += entry.getBoundingClientRect().top - menu.getBoundingClientRect().top - menu.clientHeight / 3;
        }, {once: true});
        bootstrap.Collapse.getOrCreateInstance(menu).show();
    });
});
