/* 通用交互：移动端侧栏 */
(function () {
  var btn = document.querySelector('.topbar .nt');
  var side = document.querySelector('.side');
  var mask = document.querySelector('.mask');
  if (!btn || !side) return;
  function toggle(on) {
    side.classList.toggle('open', on);
    if (mask) mask.classList.toggle('on', on);
  }
  btn.addEventListener('click', function () { toggle(!side.classList.contains('open')); });
  if (mask) mask.addEventListener('click', function () { toggle(false); });
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape') toggle(false); });
})();
