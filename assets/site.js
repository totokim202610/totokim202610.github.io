// 갤러리 좌우 단추(마우스로 볼 때만 보여요). 없어도 가로 밀기로 다 볼 수 있어요.
document.documentElement.classList.add('js');
document.querySelectorAll('[data-rail]').forEach(function (nav) {
  var rail = document.getElementById(nav.getAttribute('data-rail'));
  if (!rail) return;
  var prev = nav.querySelector('[data-dir="-1"]');
  var next = nav.querySelector('[data-dir="1"]');
  function update() {
    var max = rail.scrollWidth - rail.clientWidth - 2;
    prev.disabled = rail.scrollLeft <= 2;
    next.disabled = rail.scrollLeft >= max;
  }
  nav.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    rail.scrollBy({ left: Number(b.getAttribute('data-dir')) * rail.clientWidth * 0.8, behavior: 'smooth' });
  });
  rail.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
});
