/**
 * Daterangepicker adapter.
 * https://www.daterangepicker.com/
 */
ckan.module("{{ project_shortname }}-datepicker", function ($) {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof $.fn.daterangepicker === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[{{ project_shortname }}-datepicker] daterangepicker library is not loaded",
        );
        return;
      }

      const options = this.sandbox["{{ project_shortname }}"].nestedOptions(
        this.options,
      );

      this.el.daterangepicker(options);
    },
  };
});
