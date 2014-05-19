# Minnpost Twin Cities Metro County Parcels

A (map) look at Twin Cities Metro county parcels.

You can see this project in action here.

*Unless otherwise noted, MinnPost projects on [Github](https://github.com/minnpost) are story-driven and meant for transparency sake and not focused on re-use.  For a list of our more reusable projects, go to [code.minnpost.com](http://code.minnpost.com).*

## Data

Several metro counties are passing Open GIS Data policies, and only some have started releasing up to date parcel data.

* Hennepin
    * [Hennepin County GIS data portal](http://www.hennepin.us/your-government/open-government/gis-open-data)
    * [PDF about parcels](http://www.hennepin.us/~/media/hennepinus/your-government/open-government/taxable-parcels.pdf)
    * We use some [already converted files](http://data.dbspatial.com/hennepin/) provided by David Bitner as the files comes in ESRI Geodatabase files which very proprietary and hard to work with. The process for converting is described on [Github](https://github.com/dbSpatial/opentwincities/blob/master/fetch_hennepin.sh).
* Anoka
    * Provided through the [MetroGIS DataFinder](http://www.datafinder.org/metadata/ParcelsCurrent.html)
* Dakota
    * In the MetroGIS Datafinder but the polygon data does not have any valid attributes, though the point data does.
* Ramsey
    * [Ramsey County GIS](http://www.co.ramsey.mn.us/is/gisdata.htm) provides a large archive of all their GIS data sets.
* Carver
    * Passed policy but no data downloads.
* Washington
    * No policy passed.
* Scott
    * No policy passed.

### Get data

Download the data with the following commands.  These will be linked and processed and are too big to commit to the repo:

1. Ensure data directory is there: `mkdir -p data;`
1. Hennepin: `cd data && wget http://gis-stage.co.hennepin.mn.us/publicgisdata/hennepin_county_tax_property_base.zip && unzip hennepin_county_tax_property_base.zip -d hennepin-gdb; cd -;`
1. MetroGIS: `cd data && wget ftp://gisftp.metc.state.mn.us/ParcelsCurrent.zip && unzip ParcelsCurrent.zip -d metrogis-shp; cd -;`
1. Ramsey: `cd data && wget ftp://ftp.co.ramsey.mn.us/gisdata/publicdata.zip && unzip publicdata.zip -d ramsey-shp-gdb; cd -;

## Data processing

### Reproject and convert the data

1. `mkdir -p data/reprojected_4326-shps;`
1. `ogr2ogr -f "ESRI Shapefile" data/reprojected_4326-shps/anoka-parcels.shp data/metrogis-shp/ParcelsAnoka.shp -s_srs EPSG:26915 -t_srs EPSG:4326;`
1. `ogr2ogr data/reprojected_4326-shps/hennepin-parcels.shp data/hennepin-gdb/Hennepin_County_Tax_Property_Base.gdb -t_srs EPSG:4326;`
1. `ogr2ogr data/reprojected_4326-shps/ramsey-parcels.shp data/ramsey-shp-gdb/Shapefiles/CDSTL_AttributedParcelPoly.shp -t_srs EPSG:4326;`

### Process the data

We need to combine the shapefiles and adjust some data.

1. Run: `python data-processing/process-shapefiles.py`

### Setup TileMill project

1. Use variable for Mapbox path just in case yours is different: `export MAPBOX_PATH=~/Documents/MapBox/`
1. Link data into Mapbox directory: `ln -s "$(pwd)/data/combined-shp" $MAPBOX_PATH/data/minnpost-combined-metro-shp`
1. Link the Tilemill project into Mapbox directory: `ln -s "$(pwd)/data-processing/map-metro-parcels" $MAPBOX_PATH/project/map-metro-parcels`
1. Open up TileMill

### Exporting tiles

Use TileMill to export to `.mbtiles`.  Then upload to Mapbox.

## Development and running locally

### Prerequisites

All commands are assumed to be on the [command line](http://en.wikipedia.org/wiki/Command-line_interface), often called the Terminal, unless otherwise noted.  The following will install technologies needed for the other steps and will only needed to be run once on your computer so there is a good chance you already have these technologies on your computer.

1. Install [Git](http://git-scm.com/).
   * On a Mac, install [Homebrew](http://brew.sh/), then do: `brew install git`
1. Install [NodeJS](http://nodejs.org/).
   * On a Mac, do: `brew install node`
1. Install [Grunt](http://gruntjs.com/): `npm install -g grunt-cli`
1. Install [Bower](http://bower.io/): `npm install -g bower`
1. Install [Sass](http://sass-lang.com/): `gem install sass`
   * On a Mac do: `sudo gem install sass`
1. Install [Compass](http://compass-style.org/): `gem install compass`
   * On a Mac do: `sudo gem install compass`
1. Install [Python](https://www.python.org/download/).  This is probably already installed on your system.
   * On a Mac, it is suggested to install with Homebrew and will probably require doing more than just installing: `brew install python`
1. Install [pip](https://pypi.python.org/pypi/pip): `easy_install pip`
1. Install GDAL (with FileGDB support)

#### Install GDAL with FileGDB support

The ESRI Geodatabase (FileGDB) format is proprietary and not yet well support in open source applications.  GDAL 1.11+ has limited support for it or we build GDAL with the specific libraries provided by ESRI.  These instructions are for Mac only

1. Download file from ESRI, specifically the "File Geodatabase API 1.3 version for Mac 64-bit" version.  This requires making a free account on ESRI.
    * http://www.esri.com/apps/products/download/index.cfm?fuseaction=#File_Geodatabase_API_1.3
1. Copy the file to Homebrew cache: `cp FileGDB_API_1_3-64.zip $(brew --cache)/FileGDB_API_1_3-64.zip
1. Install [custom OSGeo tap](https://github.com/OSGeo/homebrew-osgeo4mac) (ensure that old version of tap is removed): `brew untap dakcarto/osgeo4mac && brew tap osgeo/osgeo4mac && brew tap --repair;`
1. `brew install osgeo/osgeo4mac/gdal-filegdb`
1. `brew install osgeo/osgeo4mac/gdal --complete --enable-unsupported`
1. Tell GDAL about the plugins: `export GDAL_DRIVER_PATH=$(brew --prefix)/lib/gdalplugins`
    * This should go in your `.bash_profile` so that it is consistently available.

### Get code and install packages

Get the code for this project and install the necessary dependency libraries and packages.

1. Check out this code with [Git](http://git-scm.com/): `git clone https://github.com/MinnPost/minnpost-hennepin-county-parcels.git`
1. Go into the template directory: `cd minnpost-hennepin-county-parcels`
1. Install NodeJS packages: `npm install`
1. Install Bower components: `bower install`
1. Because Mapbox comes unbuilt, we need to build it: `cd bower_components/mapbox.js/ && npm install && make; cd -;`
1. Install Python packages: `pip install -r requirements.txt`

### Running locally

1. Run: `grunt server`
    * This will run a local webserver for development and you can view the application in your web browser at [http://localhost:8804](http://localhost:8804).
1. By default, running a local server will show you the local development version.  But there are other builds that you can view by changing the query parameters.  Do note that you may have to run the build and deploy things for things to work normally.
    * Local build: http://localhost:8804/?mpDeployment=build
    * Build deployed on S3: http://localhost:8804/?mpDeployment=deploy
    * Embedded version with local build: http://localhost:8804/?mpDeployment=build&mpEmbed=true
    * Embedded version with S3 build: http://localhost:8804/?mpDeployment=deploy&mpEmbed=true

### Developing

Development will depend on what libraries are used.  But here are a few common parts.

* `js/app.js` is the main application and will contain the top logic.

Adding libraries is not difficult, but there are a few steps.

1. User bower to install the appropriate library: `bower install library --save`
1. Add the appropriate reference in `js/config.js` so that RequireJS knows about it.
1. Add an entry in the `dependencyMap` object in `bower.json`.  This is used to automatically collect resources in the build process.  It is possible, like with `minnpost-styles` that multiple entries will need to be made, one ber `.js` file.  Here is an example:

```
// Should be bower identifier.  Order matters for build, meaning that any dependencies should come first.
"library": {
  // Name used for reference in RequireJS (some modules expect dependencies with specific case, otherwise its arbitrary and you can just use the library name from above).
  // If this is not a JS library, do not include.
  "rname": "library",
  // (optional) Path to un-minified JS files within bower_components excluding .js suffix.
  "js": ["library/dist/library"],
  // (optional) Path to un-minified CSS files within bower_components excluding .css suffix.
  "css": ["library/dist/css/library"],
  // (optional) Path to un-minified IE-specific CSS files within bower_components excluding .css suffix.
  "ie": ["library/dist/css/library.ie"],
  // What is expected to be returned when using as a RequireJS dependency.  Some specific libraries, like jQuery use $, or backbone returns the Backbone class.
  // If this is not a JS library, do not include.
  "returns": "Library"
}
```

### Testing

Unfortunately there are no tests at the moment.

### Build

To build or compile all the assets together for easy and efficient deployment, do the following.  It will create all the files in the `dist/` folder.

1. Run: `grunt`

### Deploy

Deploying will push the relevant files up to Amazon's AWS S3 so that they can be easily referenced on the MinnPost site.  This is specific to MinnPost, and your deployment might be different.

1. Run: `grunt deploy`
    * This will output a bit of HTML to if you want to use the project as an embed.

There are to main ways to include the necessary HTML in a page in order to run the project.

1. Copy the relevant parts from `index.html`.
    * This has the benefit of showing messages to users that have older browsers or have Javascript turned off.  This also uses the build that separates out the third-party libraries that are used and are less likely to change; this gains a bit of performance for users.
1. Copy the embed output from `grunt deploy`.

## Hacks

*List any hacks used in this project, such as forked repos.  Link to pull request or repo and issue.*

## About Us

MinnData, the MinnPost data team, is Alan, Tom, and Kaeti and all the awesome contributors to open source projects we utilize.  See our work at [minnpost.com/data](http://minnpost.com/data).

```

                                                   .--.
                                                   `.  \
                                                     \  \
                                                      .  \
                                                      :   .
                                                      |    .
                                                      |    :
                                                      |    |
      ..._  ___                                       |    |
     `."".`''''""--..___                              |    |
     ,-\  \             ""-...__         _____________/    |
     / ` " '                    `""""""""                  .
     \                                                      L
     (>                                                      \
    /                                                         \
    \_    ___..---.                                            L
      `--'         '.                                           \
                     .                                           \_
                    _/`.                                           `.._
                 .'     -.                                             `.
                /     __.-Y     /''''''-...___,...--------.._            |
               /   _."    |    /                ' .      \   '---..._    |
              /   /      /    /                _,. '    ,/           |   |
              \_,'     _.'   /              /''     _,-'            _|   |
                      '     /               `-----''               /     |
                      `...-'                                       `...-'

```
