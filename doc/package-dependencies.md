# Inter-package dependencies

This cross-reference should help keep track of package-level dependencies,
hopefully in order to avoid creating circular ones.

Packages are ordered as a "food chain". Packages should only consume other
packages that precede them in the list.

## utility

(no dependencies)

## drivers

* utility

## events

* drivers
* utility

## screen

* drivers
* events
* utility

## panels

* events
* screen
* utility

## controller

* drivers
* events
* panels
* screens
* utility
