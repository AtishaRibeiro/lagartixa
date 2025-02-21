# Turning the globe into a 3D mesh

I was working on a video where needed to show different locations on earth. 
The requirements were pretty straightforward:
* Country borders
* Region borders (states, provinces, ...)
* Looks nice when zoomed in
* No distortion
* Be able to give countries different colours
* No satellite imagery

The simplest way one might achieve this is by drawing the country borders to some texture, and wrapping that texture around a 3d mesh.
It turns out that projecting a 2d object (our texture) onto a sphere or vice versa is not possible without having some distortion somewhere, which violates our "no distortion" rule.
Additionally, since a texture has a finite resolution, zooming into far means you start seeing the pixels which violates our "looks nice when zoomed in" rule.

Although I can't think of any concrete examples, I have seen nice globe animations that undoubtedly use some kind of software made specifically for this purpose. But I don't know what they are, and I have no idea how they work on a technicaly level.
What to do in that case except come up with your own crazy convoluted solution?

The approach I decided to go with was to turn the globe and all of the countries on it into separate 3d meshes.
It became a small obsessions during the 2 months that I worked on this, to the point that I don't care if there are better methods.

## Getting the data

All country data was obtained from [Natural Earth](https://www.naturalearthdata.com/) which provides tons of geography data.
This includes the country and region borders that we need.

The data comes in the form of [.shp files](https://en.wikipedia.org/wiki/Shapefile), which we can interpet using `geopandas`.

EX: Reading Portugal's border from the 1:50M country border dataset:
```py
import geopandas as gpd

data = gpd.read_file("ne_50m_admin_0_countries.shp")
geo_data = data.loc[data["SOVEREIGNT"] == "Portugal"]["geometry"]
# List of list since  countries can consist of multiple borders: main land, islands, enclaves, ...
portugal: list[list[tuple]] = []
if isinstance(geo_data, shapely.MultiPolygon):
    for geom in geo_data.geoms:
        portugal.append(geom.exterior.coords)
else:
    portugal.append(geo_data.exterior.coords)
```

The result is a list of (lat, lon) coordinates that describe the border of the country/region.
As an example, Luxembourg in 1:110M scale consists of only 6 coordinates (points).
<IMG luxembourg>

In Natural Earth's dataset all borders/shapes are described in a clock-wise order, which is something that will come in handy later on!

## Placing coordinates in 3D space

Coordinates describe points on a sphere, but we want points in 3D.
The following function transforms a coordinate into a point in 3D space on a sphere of radius 1.

```py
def coord_on_sphere(x, y) -> np.ndarray:
    """Translate (lon,lat) point to a point on a 3D sphere"""
    radian_ratio = math.pi / 180
    x1 = math.cos(y * radian_ratio)
    y1 = 0
    z1 = math.sin(y * radian_ratio)

    # rotate around z axis
    cos_theta = math.cos(x * radian_ratio)
    sin_theta = math.sin(x * radian_ratio)
    x2 = cos_theta * x1
    y2 = sin_theta * x1

    return np.array((x2, y2, z1))
```

If we then write all of these 3D points to an [.OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file) file and connect them using [lines](https://en.wikipedia.org/wiki/Wavefront_.obj_file#Line_elements) we get the following result:

<IMG>

From a distance this looks good, but if we overlay this on a spherical object we see some strange artefacts.

<IMG>

It looks like our lines are going straight through the sphere! While our points do lie on the surface, the lines are just that: straight lines, meaning they don't follow the sphere's surface.
We will need to come up with a solution to make the lines live on the surface.


## Journey to the center of the Earth

So far we've been working with a perfect sphere. 3D meshes however are made up of flat triangles and non-curved lines and spheres are famous for being very round and not having any flat surfaces; not a great combination.
This means that any spherical mesh is just an approximation of the real thing. The more triangles we use, the closer we get to an actual sphere.
<IMG: icosahedron>

In order to connect our points with straight lines that seemingly lie on a sphere we will have to use one of these approximations as our "base" and so our points need to lie on this base.
The easiest is to project all our points towards the center of the sphere, and create the projected point on the intersection with our base. This is the method I ended up using.

The general implementation looks something like this:
* Draw a line `l` from `p` to the origin (0, 0, 0) (which is the center of our sphere) 
* Go over every triangle in the base mesh and verify whether `l` intersects this triangle.
* If it does this intersection is our new point.
* If not, continue looking

<IMG>

Now all our points live on this spherical approximation, consisting of triangles. We will continue for now with a low res icosahedron as it's easier to visualise what is going on. You'll see later that we can use all sorts of shapes as a base!

## Connecting the dots

If we connect all our points again we'll see some countries look correct, and others don't. 
<IMG: comparison>

Whenever all points lie on a single triangle there is no issue, but when they cross triangles we have the same problem as before where the line goes through the surface.
We will need to split up our line `AB` into 2 lines: `AE` and `EB`, where `E` is a point on the edge `e` that the 2 triangles have in common.
Sounds easy enough, but where does `E` lie exactly? In the middle of the edge or closer to one of its points?
The exact position of `E` is defined in such a way that the sum both lines is as as small as possible, meaning `min(|AE| + |EB|)`.
There might be a cool formula for this, but I went with an iterative approach where:
* Divide `e` in 3 equally spaced points `X`, `Y`, `Z`
* Calculate `|AX| + |XB|` and `|AZ| + |ZB|`
  * If `X` gives the shorter path, make `e = eY` 
  * If `Z` gives the shorter path, make `e = Ye` 
* Repeat

<IMG: algorithm visually> 

We can repeat this as many times as we like, I chose 15 as it seemed to give accurate enough results.

### Crossing multiple triangles

Some connected points lie on triangles that don't border each other. In that case we will have to do the above algorithm a few times for each triangle inbetween.
To decide what triangles lie in the middle we do the following:

<IMG: algorithm visually>

* Put a point `P` in the middle of `AB`
* Scale this point so it it lies outside of our sphere
* Draw a line from `P` to the origin
* Create a new point `C` at the intersection of this line with a triangle of our base
* Replace `AB` with 2 lines: `AC` and `CB`

We repeat this as many times as necessary until neighbouring points lie on neighbouring triangles, so we can apply algorithm one.

<IMG: result>

That looks pretty good already! In fact it satisfies all of our requrements except 1.
* We can add region borders the same way as we did country borders.
* Since the borders are not defined by pixels, but are drawn dynamically, they will always appear clear no matter how far zoomed in we are or where they are located on the globe.

But since these are just outlines, we can't actually colour in the countries. What we need is a surface to draw on; aka a mesh. 
If I had known what work was ahead of me at this point, I would have compromised and stopped here.
But I didn't so let's continue!

## Nation triangulation

Up until now we've only created outlines of countries, but meshes consist of triangles, not lines.
Luckily there already exist some triangulation algorithms that are not that hard to implement, like the [ear clipping algorithm](https://nils-olovsson.se/articles/ear_clipping_triangulation/).
This will allow us to divide our shapes (countries) into individual triangles that describe our mesh.

Although the algorithm is very simple, there are 2 caveats that complicate things. To start with, the algorithm works in 2D but we are operating in 3D.
Since all our points lie on triangles, all points that share a triangle lie on the same plane and as such we can treat them as if they live in 2D space.
The second caveat is that as we've seen before, countries can span various triangles, so we will need a way to split up our country into pieces so each piece lies on a single triangle.

### Redraw the borders

<IMG: different examples>



### Chop up the pieces

## Conclusion
## Gallery
