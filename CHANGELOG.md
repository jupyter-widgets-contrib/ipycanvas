# ipycanvas Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

## 0.14.0

([Full Changelog](https://github.com/jupyter-widgets-contrib/ipycanvas/compare/v0.13.3...727d33c0478600e8797a0c13b07510e3eef549b3))

### Enhancements made

- Add offscreen-canvas support for the jupyterlite-xeus case [#365](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/365) ([@DerThorsten](https://github.com/DerThorsten))

### Maintenance and upkeep improvements

- Fix ui-tests [#366](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/366) ([@martinRenou](https://github.com/martinRenou))

### Documentation improvements

- Update jupyterlite-xeus in docs [#367](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/367) ([@martinRenou](https://github.com/martinRenou))

### Other merged PRs

- Update docs build [#362](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/362) ([@martinRenou](https://github.com/martinRenou))
- Update docs to use latest ipywidgets + jupyterlite-xeus [#359](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/359) ([@martinRenou](https://github.com/martinRenou))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-widgets-contrib/ipycanvas/graphs/contributors?from=2024-09-06&to=2025-08-01&type=c))

[@DerThorsten](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3ADerThorsten+updated%3A2024-09-06..2025-08-01&type=Issues) | [@github-actions](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3Agithub-actions+updated%3A2024-09-06..2025-08-01&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3AmartinRenou+updated%3A2024-09-06..2025-08-01&type=Issues)

<!-- <END NEW CHANGELOG ENTRY> -->

## 0.13.3

([Full Changelog](https://github.com/jupyter-widgets-contrib/ipycanvas/compare/0.13.2...8540dc19f2fff16aa64c0a2d1aa34536b7f43e37))

### New features

- Added grayscale image support in put_image_data and exposed image_smoothing_enabled attribute [#353](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/353) ([@AnyaPorter](https://github.com/AnyaPorter))
- Add stroke path to Path2D interface per html canvas spec  [#350](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/350) ([@cleemesser](https://github.com/cleemesser))
- Added mouse wheel events support [#321](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/321) ([@VladislavZavadskyy](https://github.com/VladislavZavadskyy))

### Bug fixes

- Fix pattern from image in JupyterLab [#345](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/345) ([@martinRenou](https://github.com/martinRenou))

### Maintenance

- Add jupyter-releaser [#354](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/354) ([@martinRenou](https://github.com/martinRenou))
- Fix CI [#352](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/352) ([@martinRenou](https://github.com/martinRenou))
- Fix security issue [#351](https://github.com/jupyter-widgets-contrib/ipycanvas/pull/351) ([@martinRenou](https://github.com/martinRenou))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-widgets-contrib/ipycanvas/graphs/contributors?from=2024-04-25&to=2024-09-06&type=c))

[@AnyaPorter](https://github.com/AnyaPorter) | [@cleemesser](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3Acleemesser+updated%3A2024-04-25..2024-09-06&type=Issues) | [@github-actions](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3Agithub-actions+updated%3A2024-04-25..2024-09-06&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3AmartinRenou+updated%3A2024-04-25..2024-09-06&type=Issues) | [@VladislavZavadskyy](https://github.com/search?q=repo%3Ajupyter-widgets-contrib%2Fipycanvas+involves%3AVladislavZavadskyy+updated%3A2024-04-25..2024-09-06&type=Issues)

## Release 0.13.2

### Maintenance

* Hatch migration by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/298
* Exclude map file from distribution by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/299
* Update yarn.lock by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/300
* Update links by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/335
* Update galata bot for using Lab 4 by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/337
* Build against JupyterLab 4 by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/336
* Build docs against the latest jupyterlite-xeus-python by @martinRenou in https://github.com/jupyter-widgets-contrib/ipycanvas/pull/338

**Full Changelog**: https://github.com/jupyter-widgets-contrib/ipycanvas/compare/0.13.1...0.13.2

## 0.13.1

### What's Changed
* Update the requested frontend version to ^0.13.0 by @jasongrout-db in https://github.com/martinRenou/ipycanvas/pull/291

### New Contributors
* @jasongrout-db made their first contribution in https://github.com/martinRenou/ipycanvas/pull/291

**Full Changelog**: https://github.com/martinRenou/ipycanvas/compare/0.13.0...0.13.1

## Release 0.13.0

### Bug fix

* Give each canvas an explicit reference to the canvas manager it uses. Fixes a compatibility issue with Databricks Notebook and Google Colab. by @jasongrout in https://github.com/martinRenou/ipycanvas/pull/290

### Maintenance

* Modernize js output. by @jasongrout in https://github.com/martinRenou/ipycanvas/pull/289

### Documentation

* Make touch example work by @haesleinhuepf in https://github.com/martinRenou/ipycanvas/pull/281

### New Contributors

* @jasongrout made their first contribution in https://github.com/martinRenou/ipycanvas/pull/289
* @haesleinhuepf made their first contribution in https://github.com/martinRenou/ipycanvas/pull/281

**Full Changelog**: https://github.com/martinRenou/ipycanvas/compare/0.12.1...0.13.0

## Release 0.12.1

### What's Changed

#### Bug fixes
* Fix drawing rgba image by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/284

#### Improvements
* ipywidgets 8 support by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/288

#### Documentation
* Blacken docs by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/269
* Adding ipyevents to environment.yaml by @AyrtonB in https://github.com/martinRenou/ipycanvas/pull/172
* Use xeus-python in docs by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/275
* Improve docs by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/278
* Fix JupyterLite badge in the README by @jtpio in https://github.com/martinRenou/ipycanvas/pull/279

#### Maintenance
* Pin nodejs 16 for node-canvas issues by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/285
* Bump moment from 2.29.3 to 2.29.4 by @dependabot in https://github.com/martinRenou/ipycanvas/pull/286
* Bump moment from 2.29.3 to 2.29.4 in /ui-tests by @dependabot in https://github.com/martinRenou/ipycanvas/pull/287

### New Contributors
* @AyrtonB made their first contribution in https://github.com/martinRenou/ipycanvas/pull/172
* @jtpio made their first contribution in https://github.com/martinRenou/ipycanvas/pull/279

**Full Changelog**: https://github.com/martinRenou/ipycanvas/compare/0.12.0...0.12.1

## Release 0.12.0

### What's Changed

* Fix sync issues between canvases by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/263
* Remove deprecated `size` property @martinRenou in https://github.com/martinRenou/ipycanvas/pull/263
* Improve put_image_data performances by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/251

### Maintenance

* Add galata update bot by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/264
* Add ui tests by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/266
* Add a test for multicanvas by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/267
* Update yarn dependencies by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/268

**Full Changelog**: https://github.com/martinRenou/ipycanvas/compare/0.11.0...0.12.0

## Release 0.11.0

### What's Changed
* Fix docs typo by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/241
* Fix CI by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/248
* Fix MultiCanvas events by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/247
* Add keyboard events by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/249
* Add filter property by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/244
* Fix CI and remove Python 3.6 by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/250
* Add jupyterlite-sphinx in the docs by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/256
* README: Grammar fix @0xflotus in https://github.com/martinRenou/ipycanvas/pull/257
* Update docs by @martinRenou in https://github.com/martinRenou/ipycanvas/pull/258

### New Contributors
* @0xflotus made their first contribution in https://github.com/martinRenou/ipycanvas/pull/257

**Full Changelog**: https://github.com/martinRenou/ipycanvas/compare/0.10.2...0.11.0

## 0.10.2

## Release 0.10.0

Improvements
-------------------

- Add `fill_styled_*` and `stroke_styled_*` methods by @DerThorsten #225 #227

## Release 0.9.1

## Release 0.9.0

Improvements
---------------------

- Add support for JupyterLite! By making the orjson dependency optional

## Release 0.8.2

Bug fixes
------------

- Fix JupyterLab 2 support
- Replace npm with yarn

## Release 0.8.1

New features:
------------------

- JupyterLab 3 support #165

Bug fixes:
------------

- Fix issue with circle radius in RoughCanvas #162

## Release 0.8.0

New features:
------------------

- Add support for color gradients #142
- Add support for patterns #143
- Add `fill_polygon` and `stroke_polygon` methods #151
- Add `stroke_lines` method #152

## Release 0.7.0

Improvements:
--------------------

- Reduce messages size #129
- Improve communication speed by using binary buffers only #132
- Implement sleep method #126

## Release 0.6.0

Improvements
- Added `ellipse` method for adding an ellipse to the current path
- Added `Path2D` class for drawing SVG paths
- Added `stroke_line` method for directly drawing a line without using a path
- Added `fill_circle` and `stroke_circle`, shorthands for full `fill_arc` and `stroke_arc`
- Added `RoughCanvas` for hand-drawn style

## Release 0.5.1

Big fixes
-----------

- Fix mouse events for the MutliCanvas

## Release 0.5.0

### Improvements

- Refactor sizing logic. The web canvas has two sizes, the colorbuffer size and the display size (actual size on the screen). We used to only expose the colorbuffer size and force the display size to be the same. The user can now control the display size through the `layout` property. #111 #113

## Release 0.4.7

### Improvements

- Ship `.d.ts` files with the JavaScript package #97
- Change `getCoordinates` and `resizeCanvas` from private to protected #98

## Release 0.4.6

### Improvements

- Add support for int8 int16, float16 float32 float64 buffer arrays #88

## Release 0.4.5

### Bug fixes

- Fix JupyterLab 2 support #86

## Release 0.4.4

## Improvements
- Add JupyterLab 2 support #78
- Documentation improvements #74 #72

## Release 0.4.3

Changes:
 - Deprecate the `size` attribute in favor of `width` and `height` #69
 - Layout improvements #68
 - Fix `MutliCanvas`'s `sync_image_data` attribute, and dynamically react to this attribute #70
 - Documentation improvements

## Release 0.4.2

Changes:

- Add support for touch events: https://github.com/martinRenou/ipycanvas/pull/66
- Redraw Canvas state on page refresh: https://github.com/martinRenou/ipycanvas/pull/65

## Release 0.4.1

## Release 0.4.0

## Release 0.3.4

## Release 0.3.3

## Release 0.3.2

## Release 0.3.1

## Release 0.3.0
