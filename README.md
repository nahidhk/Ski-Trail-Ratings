# Ski-Trail-Ratings

The plan for this program is to create a system to feed the topograpy of a ski trail in, and get a standarized rating out. What a rating means depends on the ski area, and this would provide a way to standardize between areas.

## Current Status

### GPX files

As the program currently stands, it accepts a gpx file and will output a graph of the gpx track where yellow is the steepest point on the trail and purple is the flattest. 

The next steps are to create a more informative visual display of the data, and creating the rating system to classify trails.

### OSM files

It will take an osm file, and output a map of all ski trails. Slope calculations do exist, but due to the quality of the data, a smoothing function will need to be added.

## What's next?

The next steps are to create a more informative visual display of the data, and creating the rating system to classify trails. For osm files in particular, the next
step is adding feature parity with gpx files by adding smoothing to the elevation data.