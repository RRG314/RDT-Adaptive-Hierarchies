# Definitions

This document defines the terms used in the repo without assuming prior RDT context.

## Point

A point is one row of the input array. For example, `[0.2, 0.7]` is a two-dimensional point.

## Cell

A cell is a subset of the input points. In the implementation, a cell stores point indices rather than copying the points.

Example: if a root cell contains 100 points, splitting it may create one child with points `0..49` and another child with points `50..99`.

## Recursive Hierarchy

A recursive hierarchy is a tree of cells. The root is the whole dataset. Each internal cell has two children. A leaf cell has no children.

## Depth

Depth is the distance from the root. The root has depth `0`. Its children have depth `1`.

## Shell

In this release, shell is the same as depth. The word is kept because earlier experiments used shell language, but no separate shell theory is claimed here.

## Ancestor And Descendant

An ancestor of a cell is any cell on the path from the root to that cell. A descendant is any cell below a given cell.

## Stable Label

A stable label is the bucket id assigned to a cell. Stable labels are designed to change as little as possible when the hierarchy is resized.

When a cell with label `3` splits, one child keeps label `3`. The other child receives a new label. This is ancestor-label inheritance.

## Movement Cost

Movement cost is the fraction of points whose label changes after resize.

If 1000 points are partitioned and 125 labels change, movement is `0.125`.

## Locality Cost

Locality cost measures how tightly points are grouped inside each label compared with the whole dataset. Lower means points sharing a label are closer together.

## Load Imbalance

Load imbalance measures bucket size unevenness. If every bucket has the same number of points, imbalance is `1.0`.

## Coverage Schedule

A coverage schedule is a deterministic recipe for generating test inputs. RDT-cover uses boundaries, midpoints, powers, corners, and shell-like points.

## Edge-Case Class

An edge-case class is a predeclared kind of input that may trigger numerical bugs. Examples in this repo include zero boundaries, cancellation, powers of ten, outer corners, and thin annuli.

