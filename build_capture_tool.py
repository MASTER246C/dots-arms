"""Positive-support capture gripper candidate; no validated payload rating."""
from pathlib import Path
import sys,json,math
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
P=Path(__file__).resolve().parent;V=A.Vector;d=A.newDocument('Capture_Tool_R4');parts=[]
def box(w,l,h,x,y,z):return Part.makeBox(w,l,h,V(x,y,z))
def cyl(r,h,x,y,z,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def add(n,s,role,fn,limit='Candidate geometry; requires fit, load retention and physical proof testing'):
 assert s.isValid(),n
 o=d.addObject('Part::Feature',n);o.Shape=s
 for k,v in [('MaterialRole',role),('Function',fn),('Qualification',limit)]:o.addProperty('App::PropertyString',k);setattr(o,k,v)
 parts.append(o)
base=box(220,180,10,-110,-40,0).fuse(box(110,10,100,-55,-40,-10))
flange=cyl(50,10,0,-50,40,V(0,1,0)).cut(cyl(12,12,0,-51,40,V(0,1,0)))
for angle in [45,135,225,315]:
 a=math.radians(angle);x=35*math.cos(a);z=40+35*math.sin(a);cut=cyl(3.3,23,x,-51,z,V(0,1,0));base=base.cut(cut);flange=flange.cut(cut)
for x in [-25,25]:
 cut=cyl(3,23,x,-51,40,V(0,1,0));base=base.cut(cut);flange=flange.cut(cut)
add('G01_base_and_rear_web',base,'metal','Machined aluminium chassis carries jaw loads to wrist interface')
add('G02_tool_flange',flange,'metal','Common four-M6/two-dowel wrist interface','Manual unloaded exchange; no automatic latch')
for y in [20,110]:
 add('G03_guide_rail_'+str(y),cyl(6,220,-110,y,25,V(1,0,0)),'metal','12mm hardened steel rail supports carriage motion')
 for x in [-110,95]:
  block=box(15,30,30,x,y-15,10).cut(cyl(6,17,x-1,y,25,V(1,0,0)))
  add('G04_rail_support_'+str(x)+'_'+str(y),block,'metal','Bolted support carries rail reaction into chassis','Clamping screws and bore tolerances require drawing')
# Stationary left jaw, moving right jaw. Lower ledges support compatible workpiece geometry.
for tag,x in [('fixed',-60),('moving',40)]:
 for y in [20,110]:
  sleeve=cyl(10.5,30,x-15,y,25,V(1,0,0)).cut(cyl(6,32,x-16,y,25,V(1,0,0)))
  add('G05_'+tag+'_bearing_'+str(y),sleeve,'metal','Linear bearing envelope guides jaw carriage','Exact LM12-size bearing selection and load life remain to verify')
  block=box(34,30,28,x-17,y-15,11).cut(cyl(10.5,36,x-18,y,25,V(1,0,0)))
  add('G06_'+tag+'_bearing_block_'+str(y),block,'metal','Metal bearing housing transfers jaw moments into paired rails')
 web=box(10,110,60,x-5,10,39)
 direction=1 if tag=='fixed' else -1
 ledge=box(25,100,8,x if direction==1 else x-25,15,39)
 add('G07_'+tag+'_jaw',web.fuse(ledge),'metal','Jaw closes around object; bottom ledge provides positive vertical support','30lb target applies only after qualification of a compatible captured object and orientation')
 add('G08_'+tag+'_pad',box(2,100,40,x+5 if direction==1 else x-7,15,49),'pad','Replaceable soft liner protects object and supplements retention','No assumed universal coefficient of friction')
# P16 linear actuator pulls movable carriage; short selected operating travel within100mm actuator stroke.
body=box(70,36,20,-105.5,-48,40).fuse(box(65,12,20,-35.5,-36,40))
add('G09_P16_drive_envelope',body,'motor','P16-100-256-12-P provides controlled jaw positioning','147mm closed pin span; use LAC position controller and current/force limiting')
add('G10_drive_rod',cyl(4,12,25,-30,50,V(1,0,0)),'metal','Rod connects actuator to movable jaw carriage')
add('G11_carriage_link',box(10,50,16,35,-30,39),'metal','Rigid link transfers axial actuator force to movable jaw')
add('G12_rear_pivot_support',box(20,28,45,-120,-44,10).cut(cyl(2.125,47,-110,-30,9)),'metal','M4 rear pivot anchors actuator while allowing alignment')
add('G13_open_limit_target',box(8,20,8,90,-35,10),'sensor','Target for independent end-of-travel sensing','Specific switch and stop details must be finalized')
# A transparent-looking block is strictly an example object, excluded from material quantities.
add('G14_example_captured_object',box(70,70,45,-40,30,47),'guard','Illustrates compatible supported block geometry','Illustration only; no physical object or tested load')
d.recompute();d.saveAs(str(P/'cad/Capture_Tool_R4.FCStd'));Part.export(parts,str(P/'cad/Capture_Tool_R4.step'))
rows=[];mesh=[]
for o in parts:
 rows.append({'part':o.Name,'role':o.MaterialRole,'function':o.Function,'qualification':o.Qualification,'valid':o.Shape.isValid(),'volume_mm3':o.Shape.Volume})
 vv,ff=o.Shape.tessellate(.5);mesh.append({'name':o.Name,'role':o.MaterialRole,'vertices':[[v.x,v.y,v.z] for v in vv],'faces':ff})
(P/'qa/CAPTURE_COMPONENTS.json').write_text(json.dumps(rows,indent=2));(P/'cad/capture_mesh.json').write_text(json.dumps(mesh));print('CAPTURE_GEOMETRY_VALID',len(parts));A.closeDocument(d.Name)
