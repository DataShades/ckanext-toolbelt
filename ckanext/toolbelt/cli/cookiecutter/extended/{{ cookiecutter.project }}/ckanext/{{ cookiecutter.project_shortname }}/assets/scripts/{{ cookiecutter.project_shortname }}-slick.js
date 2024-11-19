/**
 * Slick adapter.
 * https://kenwheeler.github.io/slick/
 */
ckan.module("{{ cookiecutter.project_shortname }}-slick", function ($) {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof $.fn.slick === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[{{ cookiecutter.project_shortname }}-slick] slick library is not loaded",
        );
        return;
      }

      this.el.slick(this.options);
    },
  };
});
