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



Change the command-line switches if you like.  Miotet's default switches are taken from an example given in ``tetgen --help``.

http://wias-berlin.de/software/tetgen/switches.html

[tetgen 1.5 manual](http://wias-berlin.de/software/tetgen/1.5/doc/manual/index.html)

---

miotet has included a binary that was compiled (long-ago) for mac osx 10.7.5 ymmv.  I don't have a mac anymore so...

[tetgen compilation](http://wias-berlin.de/software/tetgen/1.5/doc/manual/manual004.html#sec25)



#for linux:

if tetgen is installed, it will probably be at:

    /usr/bin/tetgen


so you would have to expand the preferences for this addon and enter that path, then it should work.

Simple shapes, guys.  Simple and small.  Cubes, icospheres, simple extrusions a la box-modeling...

And one more thing: attempting to subdivide on the output is an instant crash no doubt about it.

