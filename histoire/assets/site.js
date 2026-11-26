/* Filter the timeline by person (period pages only). No dependencies. */
(function () {
  var bar = document.querySelector('.filter');
  if (!bar) return;
  bar.hidden = false;
  var evs = document.querySelectorAll('.ev');
  bar.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    var p = b.getAttribute('data-p');
    bar.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    evs.forEach(function (ev) {
      ev.hidden = !!p && (' ' + ev.getAttribute('data-people') + ' ').indexOf(' ' + p + ' ') < 0;
    });
    document.querySelectorAll('.decade').forEach(function (h) {
      var n = h.nextElementSibling, any = false;
      while (n && !n.classList.contains('decade')) { if (n.classList.contains('ev') && !n.hidden) any = true; n = n.nextElementSibling; }
      h.hidden = !any;
    });
  });
})();
