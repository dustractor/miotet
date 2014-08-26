miotet
---

#my io for tetgen

---

usage:
---

Press spacebar to open the operator search, and type `tet` should get it.  The whole name is   
**Miotet: Tetgen IO**  


Invoked with an actively selected mesh object with send that mesh object to tetgen and load tetgen's output as a new mesh.

Invoked without a mesh object for the actively selected object, a file-select dialog appears for you to browse to find a tetgen .node file. It is assumed that you also have .ele and .face files in same dir as the .node file.



  Change the command-line switches if you like.  Miotet's default switches are taken from an example given in tetgen --h(elp).

[tetgen 1.5 manual](http://wias-berlin.de/software/tetgen/1.5/doc/manual/index.html)

---

miotet has included a binary that was compiled for mac osx 10.7.5 ymmv ( [tetgen compilation](http://wias-berlin.de/software/tetgen/1.5/doc/manual/manual004.html#sec25)
)
**sorry I have not got a windows or linux to test on.**  for linux put (or symlink) a tetgen binary in this folder and it is expected to work.  for windows: you will have to edit the code to reflect ".exe" in the naming of the executable. )


