/**
 * iziToast adapter.
 * https://izitoast.marcelodolza.com
 */
ckan.module("{{ cookiecutter.project_shortname }}-izi-toast", function ($) {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof iziToast === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[{{ cookiecutter.project_shortname }}-izi-toast] iziToast library is not loaded",
        );
        return;
      }

      this.el.on("click", () => iziToast.show(this.options));
    },
  };
});
