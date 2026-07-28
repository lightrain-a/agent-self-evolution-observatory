(() => {
  const target = document.body.dataset.redirect;
  if (!target) return;
  const destination = new URL(target, location.href);
  if (location.search) destination.search = location.search;
  location.replace(destination.toString());
})();
