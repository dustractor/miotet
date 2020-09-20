miotet
---

#it aM an IO for TETgen

Broken for a long time because it depended on the ply export addon...

But now it works on windows and I am in the process of cross-platforming it.

The purpose is you have the bounding mesh and the tet mesh.  Soft body sim on the bounding mesh won't be as realistic versus a tetrahedralized mesh. Solve the soft-body sim with a tet mesh that is the target object for a mesh deform modifier applied to the bounding mesh. Don't render the tet mesh.  Also, if you make a node setup to replicate 'sticky coordinates', you can visualize the difference in between original and deformed as a heat map -- sort of a rudimentary stress-testing visualization.

