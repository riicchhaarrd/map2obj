# map2obj

Converts .MAP file brushes to .OBJ<br />
Tested with CoD2/CoD4 map files

![1](preview/2.png?raw=true)

# Issues:
scipy.spatial.ConvexHull doesn't like to sort some faces and I don't know why, so it may bug out sometimes.<br />
![1](preview/1.png?raw=true)
Prefab orientation needs to be fixed<br />
Patches aren't converted<br />
Models aren't converted<br />

# References
.MAP files file format description, algorithms, and code [^1]<br />
Math for Game Programmers: Interaction With 3D Geometry [^2]
[^1]: https://github.com/stefanha/map-files/blob/master/MAPFiles.pdf
[^2]: https://youtu.be/GpsKrAipXm8?t=430
