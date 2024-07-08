const { resolve } = require("path");
const { src, dest, watch } = require("gulp");

const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const sass = require("gulp-sass")(require("sass"));
const postcss = require("gulp-postcss");
const touch = require("gulp-touch-fd");
const cleanCSS = require("gulp-clean-css");

const isDev = () => !!process.env.DEBUG;

const assetsDir = resolve(__dirname, "ckanext/{{ project_shortname }}/assets");
const srcDir = resolve(assetsDir, "scss");
const destDir = resolve(assetsDir, "styles");

const build = () =>
  src(resolve(srcDir, "{{ project_shortname }}.scss"))
    .pipe(if_(isDev, sourcemaps.init()))
    .pipe(sass().on("error", sass.logError))
    .pipe(postcss([require("postcss-combine-media-query")]))
    .pipe(if_(isDev, sourcemaps.write(), cleanCSS({ level: 2 })))
    .pipe(dest(destDir))
    .pipe(touch());

const watchStyles = () =>
  watch(resolve(srcDir, "*.scss"), { ignoreInitial: false }, build);

exports.watch = watchStyles;
exports.build = build;
