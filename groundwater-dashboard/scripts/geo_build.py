"""Export published Hunt (2023) geology and approximate thesis Figure 2 sites.

Run with pyogrio, pyproj, shapely, numpy importable. Source archives and temporary
libraries stay in scratch; original thesis and workbooks are read only.
"""
from pathlib import Path
import json, math
import numpy as np
from pyogrio.raw import read
from shapely import from_wkb, force_2d, to_geojson, make_valid, set_precision
from shapely.ops import transform, unary_union
from pyproj import Transformer
BASE=Path(__file__).resolve().parents[1]
DATA=BASE/'data'
DOI='https://doi.org/10.18738/T8/SF0BXT'
# Coordinates transcribed from Hunt (2023), Table 2, printed pp.85–87.
# Pixel coordinates are independently matched well symbols in thesis Figure 2B,
# embedded image2.png at its native 955 x 1053 pixels. x right, y down.
controls=[
 {'label':'Farm Well 5747607','x':495,'y':691,'lat':30.331362,'lon':-98.138787},
 {'label':'Johanson Monitor Well 1 5747313','x':580,'y':616,'lat':30.337408,'lon':-98.132265},
 {'label':'Johanson 2 5747314','x':577,'y':650,'lat':30.334475,'lon':-98.132572},
 {'label':"Buddy RV 5747316",'x':594,'y':656,'lat':30.334283,'lon':-98.130992},
 {'label':'Hegemier 5747602','x':643,'y':996,'lat':30.306662,'lon':-98.127214}
]
A=np.array([[s['x'],s['y'],1]for s in controls])
coeff=np.linalg.lstsq(A,np.array([[s['lon'],s['lat']]for s in controls]),rcond=None)[0]
for s, pred in zip(controls,A@coeff):
 s['fitResidualMeters']=round(math.hypot((pred[0]-s['lon'])*111320*math.cos(math.radians(s['lat'])),(pred[1]-s['lat'])*111320),1)
def point(x,y):
 lon,lat=np.array([x,y,1])@coeff
 return round(float(lat),6),round(float(lon),6)
# Named marker centroids only. Some pairs share one label/symbol in Figure 2B.
local=[
 ('ec-cp','Elder Creek convergence pool',479,672,'Surface water','CS & CP share a marker in Figure 2B; sublocations not separated.'),
 ('ec-cs','Elder Creek convergence stream',479,672,'Surface water','CS & CP share a marker in Figure 2B; sublocations not separated.'),
 ('ec-head','Elder Creek head',492,689,'Spring / surface water','S1 & Head are closely spaced in Figure 2B; individual assignment is approximate.'),
 ('ec-s1','Elder Creek Spring 1',484,685,'Spring','S1 & Head are closely spaced in Figure 2B; individual assignment is approximate.'),
 ('ec-s2','Elder Creek Spring 2',477,695,'Spring','Named marker in thesis Figure 2B.'),
 ('ps','Pig Spring',463,670,'Spring','Named marker in thesis Figure 2B.'),
 ('rcn-cs1','Roy Creek North Comma Spring 1',395,709,'Spring','Named marker in thesis Figure 2B.'),
 ('rcn-cs2','Roy Creek North Comma Spring 2',393,720,'Spring','Named marker in thesis Figure 2B.'),
 ('rcn-w3','Roy Creek North Waterfall 3',390,774,'Surface water','Named marker in thesis Figure 2B.'),
 ('rcn-w1','Roy Creek North Waterfall 1',389,808,'Surface water','Named marker in thesis Figure 2B.'),
 ('rcn-bath','Roy Creek North Bath',393,831,'Surface water','Named marker in thesis Figure 2B.'),
 ('rcs-resurgence','Roy Creek South Resurgence 1',330,888,'Spring / surface water','Named marker in thesis Figure 2B.'),
 ('rcs-road','Roy Creek South Road',344,889,'Surface water','Named marker in thesis Figure 2B.'),
 ('rcs-tb','Roy Creek South TB',334,998,'Spring / surface water','Named marker in thesis Figure 2B; precise spring/surface-water classification unresolved.'),
 ('rcs-top','Roy Creek South Top',371,1015,'Spring / surface water','Named marker in thesis Figure 2B; precise spring/surface-water classification unresolved.'),
 ('rcs-lds','Roy Creek South LDS',378,1019,'Spring','Named marker in thesis Figure 2B; described as upstream spring in thesis text.'),
]
sites=[]
for id,label,x,y,typ,desc in local:
 lat,lon=point(x,y)
 sites.append(dict(id=id,label=label,lat=lat,lon=lon,type=typ,coordinateBasis='Approximate marker digitized from thesis Figure 2B, affine fit to five Hunt (2023) Table 2 wells',coordinateConfidence='approximate',uncertaintyMeters=150,description=desc,source='Vivian thesis draft3 JB_DR, Figure 2B; control coordinates Hunt (2023), Table 2',sourceUrl=DOI,pixel=[x,y]))
# Shared group centroid: the source map does not unambiguously distinguish the
# three Deadmans sublocations. Same coordinate avoids fabricated distinctions.
for id,label in [('deadmans-creek','Deadmans Creek'),('deadmans-hole-pool','Deadmans Hole pool'),('deadmans-hole-upper','Deadmans Hole upper')]:
 lat,lon=point(58,873)
 sites.append(dict(id=id,label=label,lat=lat,lon=lon,type='Surface water / spring',coordinateBasis='Approximate Deadmans Hole group centroid in thesis Figure 2B; individual sublocation unresolved',coordinateConfidence='group location only',uncertaintyMeters=300,description='The three chemistry labels share the displayed group location; the map does not establish which brown marker corresponds to each sublocation.',source='Vivian thesis draft3 JB_DR, Figure 2B',sourceUrl=DOI,pixel=[58,873]))
for id,label,lat,lon,aquifer in [
 ('farm-well','Mirasol Farm Well (5747607)',30.331362,-98.138787,'Cow Creek'),
 ('well-5747313','Johanson Monitor Well 1 (5747313)',30.337408,-98.132265,'Middle Trinity'),
 ('well-5747314','Johanson 2 (5747314)',30.334475,-98.132572,'Middle Trinity'),
 ('well-5747316',"Buddy RV (5747316)",30.334283,-98.130992,'Cow Creek'),
 ('well-5747602','Hegemier (5747602)',30.306662,-98.127214,'Middle Trinity'),
 ('well-5748505','Murphy TWDB (5748505)',30.296467,-98.072067,'Lower Glen Rose')]:
 sites.append(dict(id=id,label=label,lat=lat,lon=lon,type='Well',aquifer=aquifer,coordinateBasis='Published decimal-degree coordinates, Hunt (2023), Table 2, printed pp.85–87; exact identifier match',coordinateConfidence='published coordinates',uncertaintyMeters=None,description='Coordinate accuracy was not specified in the source table; decimal precision is not survey accuracy.',source='Hunt (2023), Table 2',sourceUrl=DOI))
# Figure2A-to-Figure2B affine relation based on common well symbols. This avoids
# relying on the image scale bars, which differ in x/y scale after embedding.
controlsA=[(173,225,495,691),(200,201,580,616),(199,212,577,650),(205,213,594,656),(219,324,643,996)]
aA=np.array([[x,y,1]for x,y,*_ in controlsA]); cA=np.linalg.lstsq(aA,np.array([[xb,yb]for _,_,xb,yb in controlsA]),rcond=None)[0]
dividePixels=[(400,27),(415,65),(428,111),(421,135),(408,162),(399,181),(383,204),(365,220),(338,239),(311,253),(278,269),(247,285),(222,301),(203,324),(185,345),(168,370),(152,393),(132,420),(108,449),(83,477)]
line=[]
for x,y in dividePixels:
 xb,yb=np.array([x,y,1])@cA
 lat,lon=point(xb,yb);line.append([lon,lat])
divide={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'label':'Approximate Middle Trinity groundwater divide','source':'Thesis Figure 2A, attributed there to Hunt (2023b); digitized approximation, not original divide GIS','sourceUrl':DOI,'uncertaintyMeters':300,'uncertaintyNote':'300 m is a conservative display tolerance chosen for this digitization, not a measured confidence interval. The source divide is itself approximate and may move with groundwater conditions.','method':'Manual line tracing; Figure 2A affine registration through Figure 2B to five Table 2 well coordinates.'},'geometry':{'type':'LineString','coordinates':line}}]}
legend=[('Ked','Edwards Limestone','#c7c8b7'),('Kwal','Walnut Clay','#d7d76c'),('Kgrud','Glen Rose undivided','#cfebdf'),('Kgru','Upper Glen Rose Limestone','#b1d6b0'),('Kgrl','Lower Glen Rose Limestone','#93bdb0'),('Khe','Hensel Sandstone','#f4e8d5'),('Kcc','Cow Creek Limestone','#c7d8dc'),('Kha','Hammett Shale','#b4b4b4'),('Ksy','Sycamore Sandstone','#f5caa0'),('Unknown','Unclassified polygon','#dedede')]
lu={u:(label,color)for u,label,color in legend}
# Export exact published GIS features, simplify 3 m in native UTM for a light
# browser layer, transform NAD83/UTM14N to WGS84, remove unused height ordinate.
meta,_,geoms,columns=read(BASE/'scratch/p20/hamiltonreimersstudy.gdb',layer='Geology_bedrock_units_2023')
project=Transformer.from_crs(meta['crs'],'EPSG:4326',always_xy=True).transform
features=[]
for i,wkb in enumerate(geoms):
 unit=str(columns[0][i] or 'Unknown').rstrip('\\')
 label,color=lu.get(unit,lu['Unknown'])
 geom=force_2d(from_wkb(wkb))
 if not geom.is_valid:
  geom=make_valid(geom)
  if geom.geom_type=='GeometryCollection':geom=unary_union([part for part in geom.geoms if part.geom_type in ('Polygon','MultiPolygon')])
 geom=geom.simplify(3,preserve_topology=True)
 geom=make_valid(transform(project,geom))
 if geom.geom_type=='GeometryCollection':geom=unary_union([part for part in geom.geoms if part.geom_type in ('Polygon','MultiPolygon')])
 g=json.loads(to_geojson(set_precision(geom,0.000001)))
 features.append({'type':'Feature','properties':{'unit':unit,'label':label,'color':color,'source':'Hunt (2023), Geology_bedrock_units_2023; simplified 3 m for display','sourceUrl':DOI},'geometry':g})
geo={'type':'FeatureCollection','name':'Hunt 2023 bedrock geology','features':features}
(DATA/'geology.geojson').write_text(json.dumps(geo,separators=(',',':')))
output={
 'meta':{'title':'Hill Country Field Station and surrounding Middle Trinity','crs':'EPSG:4326','mappedSites':len(sites),'coordinateNote':'Local markers are digitized approximations; published well coordinates have unspecified positional accuracy. Unmapped chemical site labels remain available in the data table.','divideNote':'Approximate, manually traced groundwater divide; not a surveyed boundary or current groundwater surface.','georeference':{'sourceFigure':'Thesis Figure 2B, embedded image2.png native 955 x 1053 pixels','controls':controls,'coefficientsLonLat':coeff.tolist(),'maxControlResidualMeters':max(s['fitResidualMeters']for s in controls),'displayUncertaintyMeters':150},'unmappedNotes':['RCN W2 and NWW are not explicitly located in the thesis Figure 2B; no inferred alias was used.','Pedernales subsite names Hamilton/LT/unspecified could not be matched unambiguously to individual square symbols.','5747318 is Edge Spring in Hunt Table 2 while the chemistry export classifies a numeric label as a well; it remains unmapped pending identity review.','Other regional laboratory labels lack defensible coordinates in the available source set.']},
 'sites':sites,'divide':divide,
 'geology':{'type':'geojson','url':'data/geology.geojson','label':'Bedrock geology · Hunt 2023','attribution':'Hunt (2023), UT Austin Bureau of Economic Geology; Texas Data Repository (CC0)','sourceUrl':DOI,'description':'Original published bedrock GIS polygons; 3 m simplification for browser display. Mapped contacts describe surface bedrock, not necessarily a well’s screened aquifer. No extrapolation beyond source coverage.','geometryRepairNote':'Two published source polygons had self intersecting rings; standard make_valid repair was applied before simplification.','featureCount':len(features),'legend':[{'unit':u,'label':l,'color':c}for u,l,c in legend]},
 'sources':[{'id':'hunt2023','title':'Hunt (2023) Hydrogeology of Hamilton Pool and Reimers Ranch, Phase 2','url':DOI,'license':'CC0 1.0 (Texas Data Repository v7.1 metadata, accessed 2026-11-13)','usedFor':'Published Table 2 well coordinates and original bedrock GIS layer Geology_bedrock_units_2023 from Geology_v3_2023.tar (file296411).'}, {'id':'thesis','title':'Vivian thesis draft3 JB_DR, Figure 2','url':None,'usedFor':'Named local site marker locations and approximate groundwater divide traced from the user supplied map; not the instructions/comments in the draft.'}]
}
(DATA/'geography.json').write_text(json.dumps(output,indent=2))
print('Mapped sites',len(sites),'geology polygons',len(features),'bytes',(DATA/'geology.geojson').stat().st_size,'control residuals',[x['fitResidualMeters']for x in controls])
