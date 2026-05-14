ckan.module("resumable-resource-upload", function ($) {
  return {
    options: {
      idField: `[name="file_id"]`,
      packageId: null,
      resourceId: null,
      progressBar: "#resource-upload-progressbar",
    },
    _uploadKey: "ckanext.resumable.incompleteUpload",

    initialize() {
      this._idField = $(this.options.idField);
      this._bar = $(this.options.progressBar);

      this.$(".btn-remove-url").on("click", () => {
        this.$("#field-clear-upload").prop("checked", true);
        this.$("#field-resource-upload").focus();
      });
      this._uploadField = this.$("#field-resource-upload");

      this._uploadField.on("change", (event) => {
        // this module exects a single file in field. All files but first will
        // be ignored
        const file = event.target.files[0];
        this._processFile(file);
      });

      this.uploader = this.sandbox.files.makeUploader("Multipart", {
        uploadAction: "files_resource_upload",
      });

      this._setupUploadListeners();

      const incomplete = this._getIncompleteUpload();
      if (incomplete) {
        const contentNode = document.createElement("div");
        const nameNode = document.createElement("strong");
        nameNode.append(incomplete.name);
        const sizeNode = document.createElement("em");
        sizeNode.append(this.formatFileSize(incomplete.size));

        contentNode.append(
          "Previous upload is not completed. To resume, select a file with the same name and size: ",
          nameNode,
          " (",
          sizeNode,
          ")",
          ". Selecting a different file will discard the incomplete upload and start a new one.",
        );

        this.sandbox.ui
          .notification(contentNode, "Incomplete upload detected", {
            dismissible: true,
            style: "warning",
          })
          .show();

        this._setProgress(incomplete.uploaded, incomplete.size);
      }
    },

    formatFileSize(bytes) {
      const units = ["B", "KiB", "MiB", "GiB", "TiB"];
      let unitIndex = 0;

      while (bytes >= 1024 && unitIndex < units.length - 1) {
        bytes /= 1024;
        unitIndex++;
      }

      return `${bytes.toFixed(2)} ${units[unitIndex]}`;
    },

    _setProgress(uploaded, size) {
      this._bar.css("width", `${((uploaded / size) * 100).toFixed(0)}%`);
    },

    _setupUploadListeners() {
      this.uploader.addEventListener(
        "multipartid",
        ({ detail: { file, id } }) => {
          this._commitUpload({
            created: new Date(),
            size: file.size,
            name: file.name,
            id,
            uploaded: 0,
          });
          this._switchSubmit(false);

          this._bar.css("width", "0%");
        },
      );

      this.uploader.addEventListener(
        "progress",
        ({ detail: { loaded, total } }) => {
          this._commitUpload({ uploaded: loaded });
          this._setProgress(loaded, total);
        },
      );

      this.uploader.addEventListener("finish", ({ detail: { result } }) => {
        this._resetUpload();
        this._switchSubmit(true);
        this._idField.val(result.id);
      });

      this.uploader.addEventListener("fail", ({ detail: { reasons } }) => {
        this.sandbox.ui
          .notification(Object.values(reasons), "Upload error", {
            dismissible: true,
            style: "danger",
          })
          .show();
        this._resetUpload();
      });

      this.uploader.addEventListener("error", ({ detail: { message } }) => {
        this.sandbox.ui
          .notification(message, "Upload error", {
            dismissible: true,
            style: "danger",
          })
          .show();
      });
    },

    /**
     * Process the uploaded file.
     *
     * @param {File} file - The uploaded file to process.
     */
    _processFile(file) {
      if (!file) {
        this._idField.val("");
        return;
      }

      const incomplete = this._getIncompleteUpload();
      if (
        incomplete &&
        incomplete.size === file.size &&
        incomplete.name === file.name
      ) {
        this.uploader.resume(file, incomplete.id);
      } else {
        this.uploader.upload(file, {
          resource_id: this.options.resourceId,
          package_id: this.options.packageId,
          multipart: true,
        });
      }
    },

    _getIncompleteUpload() {
      const value = localStorage.getItem(this._uploadKey);
      if (value) {
        const data = JSON.parse(value);
        const age = new Date() - new Date(data.created);
        // S3 multipart uploads are expired in 7 days. To be sure that upload
        // will not expire in the middle of request, ignore uploads older than 6
        // days.
        if (age / 1000 / 3600 / 24 < 6) {
          return data;
        }
      }
    },

    _commitUpload(data) {
      const value = this._getIncompleteUpload() || {};
      Object.assign(value, data);
      localStorage.setItem(this._uploadKey, JSON.stringify(value));
    },

    _resetUpload(data) {
      localStorage.removeItem(this._uploadKey);
    },

    _switchSubmit(enabled) {
      this.el
        .closest("form")
        .find(`[type="submit"]`)
        .prop("disabled", !enabled);
    },
  };
});
