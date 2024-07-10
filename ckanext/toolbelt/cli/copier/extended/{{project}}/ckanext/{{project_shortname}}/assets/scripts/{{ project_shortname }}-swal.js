/**
 * SweetAlert2 adapter.
 * https://sweetalert2.github.io/
 */
ckan.module("{{ project_shortname }}-swal", function () {
  return {
    options: {},

    initialize() {
      // stop execution if dependency is missing.
      if (typeof Swal === "undefined") {
        // reporting the source of the problem is always a good idea.
        console.error(
          "[{{ project_shortname }}-swal] SweetAlert library is not loaded",
        );
        return;
      }

      const options = this.sandbox["{{ project_shortname }}"].nestedOptions(
        this.options,
      );
      this.el.on("click", () => Swal.fire(options));
    },
  };
});
