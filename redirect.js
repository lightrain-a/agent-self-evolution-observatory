(() => {
  const target = document.body.dataset.redirect;
  if (!target) return;
  const page = location.pathname.split("/").pop() || "";
  const hashMaps = {
    "domains.html": {
      "#group-visual-multimodal":"mechanisms.html#field-multimodal",
      "#group-gui-web":"mechanisms.html#field-gui-web",
      "#group-embodied-world":"mechanisms.html#field-embodied",
    },
    "evaluation.html": {
      "#group-evaluation-safety":"mechanisms.html#field-evaluation-safety",
      "#group-datasets-benchmarks":"mechanisms.html#field-datasets-benchmarks",
      "#group-repositories":"mechanisms.html#field-repositories",
    },
  };
  const mapped = hashMaps[page]?.[location.hash] || target;
  const destination = new URL(mapped, location.href);
  if (location.search) destination.search = location.search;
  location.replace(destination.toString());
})();
