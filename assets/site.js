// Progressive enhancement: the complete list remains readable without JavaScript.
(() => {
  const search = document.querySelector('#search');
  if (!search) return;
  const method = document.querySelector('#method');
  const cards = [...document.querySelectorAll('article[data-kind]')];
  const count = document.querySelector('#count');
  const empty = document.querySelector('#empty');
  const terms = cards.map(card => ({card, text:card.textContent.toLocaleLowerCase()}));
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  if (['dry','wet','mixed'].includes(params.get('kind'))) method.value = params.get('kind');
  function render(updateURL = false) {
    const q = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const {card, text} of terms) {
      const show = (!q || text.includes(q)) && (!method.value || card.dataset.kind === method.value);
      card.hidden = !show;
      if (show) visible++;
    }
    count.textContent = `${visible} / ${cards.length} 位 · 按建议联系顺序`;
    empty.hidden = visible !== 0;
    if (updateURL) {
      const url = new URL(location.href);
      for (const [key, value] of [['q', search.value.trim()], ['kind', method.value]]) {
        if (value) url.searchParams.set(key, value); else url.searchParams.delete(key);
      }
      // Some local-file browsers disallow history updates; filtering still works.
      try { history.replaceState(null, '', url); } catch (_) { /* no-op */ }
    }
  }
  search.addEventListener('input', () => render(true));
  method.addEventListener('change', () => render(true));
  document.querySelector('.tools').hidden = false;
  render();
})();
