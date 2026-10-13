"""R4 metal-frame tendon hand candidates; no physical grip rating."""
import sys,json,math
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
P=Path(__file__).resolve().parent;V=A.Vector;d=A.newDocument('Patch_Hands_R4');parts=[]
def box(w,l,h,x,y,z):return Part.makeBox(w,l,h,V(x,y,z))
def cyl(r,h,x,y,z,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def rod(a,b,r):
 v=b-a;return Part.makeCylinder(r,v.Length,a,v.normalize())
def add(n,s,role,fn,limit):
 assert s.isValid(),n
 o=d.addObject('Part::Feature',n);o.Shape=s
 for k,v in [('MaterialRole',role),('Function',fn),('Qualification',limit)]:o.addProperty('App::PropertyString',k);setattr(o,k,v)
 parts.append(o)
def stop_slot(y,z,limit,positive=False):
 angles=[math.radians((1 if positive else -1)*limit*k/24) for k in range(25)]
 pts=[V(-10,y+9.7*math.cos(t),z+9.7*math.sin(t)) for t in angles]
 pts +=[V(-10,y+6.3*math.cos(t),z+6.3*math.sin(t)) for t in reversed(angles)];pts.append(pts[0])
 slot=Part.Face(Part.makePolygon(pts)).extrude(V(20,0,0))
 for t in [angles[0],angles[-1]]:slot=slot.fuse(cyl(1.7,20,-10,y+8*math.cos(t),z+8*math.sin(t),V(1,0,0)))
 return slot
def phalanx(L,terminal=False,next_limit=50):
 # Machined links and fork cheeks, M3 hinge pins. Large integrated guide sectors are placeholders for replaceable liners.
 s=box(14,L-20.2,12,-7,12.2,-6).fuse(box(6,13,12,-3,0,-6)).fuse(cyl(8,6,-3,0,0,V(1,0,0)))
 if not terminal:
  s=s.cut(box(8,12,16,-4,L-10,-8))
  for x in [-7,4]:s=s.fuse(cyl(12,3,x,L,0,V(1,0,0)))
  s=s.cut(cyl(1.6,18,-9,L,0,V(1,0,0))).cut(stop_slot(L,0,next_limit))
 s=s.cut(cyl(1.6,18,-9,0,0,V(1,0,0))).cut(cyl(1.6,18,-9,8,0,V(1,0,0))).cut(cyl(1.2,L+16,0,-8,-8,V(0,1,0)))
 return s
for side,off,mirror in [('Left',-190,False),('Right',190,True)]:
 def put(n,s,role='metal',fn='Structural hand component',lim='Prototype geometry; physical force, fit and endurance tests required'):
  if mirror:
   m=A.Matrix();m.A11=-1;s.transformShape(m,True)
  s.translate(V(off,0,0));add(side+'_'+n,s,role,fn,lim)
 palm=box(204,205,6,-102,-135,0).fuse(box(36,35,6,-88,60,0))
 for x in [-50,50]:
  for y in [-120,55]:palm=palm.cut(cyl(3.3,8,x,y,-1))
 for bx in [-35,35]:
  for by in [-120,-90]:palm=palm.cut(cyl(3.3,8,bx,by,-1))
 put('H01_palm',palm,fn='Aluminium palm carries the drive mounts, finger bases and wrist load path')
 for x in [-102,94]:put('H02_side_rail_'+str(x),box(8,205,20,x,-135,6),fn='Metal side rail stiffens palm and anchors removable guards')
 # Six actuator cartridges arranged in two height levels. Mount holes are manufacturer-documented4.25mm.
 for i in range(6):
  x=[-60,-20,20,60,-20,20][i];z=40 if i<4 else 72;y=-118
  body=box(36,70,20,x-25.5,y+4.5,z-10).fuse(box(12,60,20,x-6,y+74.5,z-10))
  body=body.fuse(cyl(4.5,8,x,y,z-4)).cut(cyl(2.125,12,x,y,z-6))
  put(f'H03_drive_{i+1}',body,'motor','P16-100-256-12-P envelope; linear pull replaces small rotary spool','147mm closed pin span; body envelope only, current actuator drawing governs manufacture')
  put(f'H04_drive_rod_{i+1}',cyl(4,8,x,y+134.5,z,V(0,1,0)).fuse(cyl(4.5,8,x,y+147,z-4)).cut(cyl(2.125,10,x,y+147,z-5)),'metal','Axial rod pulls tendon tensioner','Only axial loading; no side-loaded rod')
  if i<4:
   tower=box(18,8,(74 if x in [-20,20] else 42),x-9,y-16,6)
   for level in ([40,72] if x in [-20,20] else [40]):
    for zz in [level-7,level+4]:
     ear=box(18,20,3,x-9,y-16,zz).cut(cyl(2.125,5,x,y,zz-1));tower=tower.fuse(ear)
   put(f'H05_rear_tower_{i+1}',tower,fn='One metal tower supports both stacked actuator rear pivots')
  put(f'H05_rear_pin_{i+1}',cyl(2,20,x,y,z-10),fn='M4 retained rear pivot pin')
  for gx in [x-9,x+9]:
   put(f'H05_carriage_guide_{i+1}_{gx}',cyl(2,41,gx,y+140,z,V(0,1,0)),fn='Guide aligns tendon carriage; motor rod carries axial pull',lim='Cantilever guide support and carriage fit need physical qualification')
  anchor=box(28,16,14,x-14,y+142,z-7).cut(box(14,10.5,8.4,x-7,y+141.5,z-4.2)).cut(cyl(2.125,16,x,y+147,z-8))
  for gx in [x-9,x+9]:anchor=anchor.cut(cyl(2.1,18,gx,y+141,z,V(0,1,0)))
  put(f'H06_tendon_anchor_{i+1}',anchor,fn='Guided clevis links actuator eye to tendon termination',lim='Use20mm operating travel; splice and termination proof test required')
  put(f'H06_output_pin_{i+1}',cyl(2,20,x,y+147,z-10),fn='M4 pin connects moving actuator eye to tendon carriage')
 # Four fingers, fixed spread; intended joint limits enforced by replaceable stop inserts, not claimed complete here.
 lengths=[[36,32,28],[40,34,28],[36,32,26],[30,28,24]]
 for f,ls in enumerate(lengths):
  x=(f-1.5)*19.05;y=82;z=40
  for xx in [x-7,x+4]:
   fork=box(3,18,42,xx,64,6).fuse(cyl(12,3,xx,y,z,V(1,0,0))).cut(cyl(1.6,5,xx-1,y,z,V(1,0,0)))
   slot=stop_slot(y,z,45);slot.translate(V(x,0,0));fork=fork.cut(slot)
   put(f'H07_finger{f+1}_base_{xx}',fork,fn='Finger knuckle transfers loads into palm')
  for j,L in enumerate(ls):
   s=phalanx(L,j==2,50 if j==0 else 30);s.translate(V(x,y,z));put(f'H08_finger{f+1}_link{j+1}',s,'finger','Machined aluminium phalanx carries contact load to hinge and tendon')
   put(f'H09_finger{f+1}_pin{j+1}',cyl(1.5,18,x-9,y,z,V(1,0,0)),fn='M3 shoulder pin provides hinge axis; mechanically retained ends required')
   put(f'H09_finger{f+1}_stop_pin{j+1}',cyl(1.5,18,x-9,y+8,z,V(1,0,0)),fn='Follower pin contacts machined travel-stop slot')
   put(f'H10_finger{f+1}_tendon{j+1}',rod(V(x,y,z-8),V(x,y+L-(9 if j==2 else 0),z-8),1),'tendon','2mm HMPE routing witness','Not a qualified continuous tendon route; bend guides and terminations remain to validate')
   y+=L
  put(f'H11_finger{f+1}_pad',cyl(3,4,x,y-4,z-10),'pad','Replaceable narrow soft pad contacts keys and small parts')
 # Opposed thumb: bearing-supported yaw carrier with a dropped fork in front of palm.
 yaw=-60;origin=V(-65+30*math.sin(math.radians(60)),95,-12)
 # Thumb extension is integral with H01 palm, avoiding overlapping separate stock.
 housing=cyl(12,14,-65,80,6).fuse(cyl(20,4,-65,80,16)).cut(cyl(8.1,16,-65,80,5))
 # Stationary yaw stop plate, -60 to -40degrees; independent of software endpoints.
 pts=[V(-65+17.7*math.cos(math.radians(t)),80+17.7*math.sin(math.radians(t)),15) for t in range(-60,-39)]
 pts +=[V(-65+14.3*math.cos(math.radians(t)),80+14.3*math.sin(math.radians(t)),15) for t in range(-40,-61,-1)];pts.append(pts[0]);slot=Part.Face(Part.makePolygon(pts)).extrude(V(0,0,6))
 for t in [-60,-40]:slot=slot.fuse(cyl(1.7,6,-65+16*math.cos(math.radians(t)),80+16*math.sin(math.radians(t)),15))
 housing=housing.cut(slot);put('H13_thumb_yaw_housing',housing,fn='Housing locates paired8mm-bore thumb bearings')
 for zz in [6,13]:put('H13_thumb_bearing_'+str(zz),cyl(8,5,-65,80,zz).cut(cyl(4,7,-65,80,zz-1)),fn='688-size bearing envelope supports8mm thumb yaw shaft')
 put('H13_thumb_shaft',cyl(4,20,-65,80,6),fn='Retained8mm steel shaft carries opposition rotation')
 put('H13_thumb_hub',cyl(20,4,-65,80,20).cut(cyl(4,6,-65,80,19)).cut(cyl(1.6,6,-57,80-16*math.sin(math.radians(60)),19)),fn='Clamping hub joins shaft to dropped thumb fork',lim='Clamp preload and anti-slip torque require qualification')
 put('H13_thumb_yaw_stop_pin',cyl(1.5,8,-57,80-16*math.sin(math.radians(60)),16),fn='M3 follower pin limits opposition to the checked20degree range')
 carrier=box(18,40,4,-9,-10,0).cut(cyl(4.1,6,0,0,-1))
 for xx in [-7,4]:
  fork=box(3,8,36,xx,22,-36).fuse(cyl(12,3,xx,30,-36,V(1,0,0))).cut(cyl(1.6,5,xx-1,30,-36,V(1,0,0)))
  fork=fork.cut(stop_slot(30,-36,45,True));carrier=carrier.fuse(fork)
 carrier.rotate(V(),V(0,0,1),yaw);carrier.translate(V(-65,80,24));put('H13_thumb_dropped_fork',carrier,fn='Offset fork places thumb beneath opposing fingers')
 def thumb_shape(s):
  s.rotate(V(),V(0,1,0),180);s.rotate(V(),V(0,0,1),yaw);s.translate(origin);return s
 ty=0
 for j,L in enumerate([36,30]):
  s=phalanx(L,j==1);s.translate(V(0,ty,0));put(f'H14_thumb_link{j+1}',thumb_shape(s),'finger','Opposed thumb flexes toward fingers',lim='Full yaw/flexion collision sweep and tendon coupling remain required')
  put(f'H14_thumb_pin{j+1}',thumb_shape(cyl(1.5,18,-9,ty,0,V(1,0,0))),fn='RetainedM3 hinge pin supports thumb flexion')
  put(f'H14_thumb_stop_pin{j+1}',thumb_shape(cyl(1.5,18,-9,ty+8,0,V(1,0,0))),fn='Thumb follower pin limits flexion')
  ty+=L
 put('H14_thumb_pad',thumb_shape(cyl(3,4,0,ty-4,-10)),'pad','Replaceable thumb contact pad')
 # Bolted, unloaded-only tool exchange interface with dowel registration.
 flange=cyl(50,10,0,-157,10,V(0,1,0)).cut(cyl(12,12,0,-158,10,V(0,1,0)))
 for ang in [45,135,225,315]:
  a=math.radians(ang);flange=flange.cut(cyl(3.3,12,35*math.cos(a),-158,10+35*math.sin(a),V(0,1,0)))
 for xx in [-25,25]:flange=flange.cut(cyl(3,12,xx,-158,10,V(0,1,0)))
 put('H15_wrist_flange',flange,fn='Four M6 bolts and two locating dowels join tool to wrist',lim='Manual tool exchange only while unloaded and mechanically supported')
 bracket=box(100,12,100,-50,-147,-40).fuse(box(100,50,10,-50,-135,-10))
 for ang in [45,135,225,315]:
  ar=math.radians(ang);bracket=bracket.cut(cyl(3.3,14,35*math.cos(ar),-148,10+35*math.sin(ar),V(0,1,0)))
 for bx in [-25,25]:bracket=bracket.cut(cyl(3,14,bx,-148,10,V(0,1,0)))
 for bx in [-35,35]:
  for by in [-120,-90]:bracket=bracket.cut(cyl(3.3,12,bx,by,-11))
 put('H16_wrist_angle',bracket,fn='Metal angle transfers palm loads into wrist flange',lim='FourM6x25 palm bolts and fourM6x35 flange bolts are design candidates; torque and fit qualification required')
 for px in [-98,98]:
  for py in [-126,-98]:put('H17_camera_post_'+str(px)+'_'+str(py),cyl(3,68,px,py,26),fn='Metal posts support camera shelf from palm side rails')
 put('H17_camera_carrier',box(204,40,5,-102,-132,94),'frame','Padded removable carrier holds wrist camera above drives')
 put('H18_camera_envelope',box(44,25,44,-22,-128,99),'sensor','Wrist camera observes workpiece and fingers','Envelope only; cable clearance and view calibration required')
# Save geometry and an explanation record for every modeled item.
d.recompute();d.saveAs(str(P/'cad/Paired_Hands_R4.FCStd'));Part.export(parts,str(P/'cad/Paired_Hands_R4.step'))
rows=[];mesh=[]
for o in parts:
 rows.append({'part':o.Name,'role':o.MaterialRole,'function':o.Function,'qualification':o.Qualification,'valid':o.Shape.isValid(),'volume_mm3':o.Shape.Volume})
 vv,ff=o.Shape.tessellate(.5);mesh.append({'name':o.Name,'role':o.MaterialRole,'vertices':[[v.x,v.y,v.z] for v in vv],'faces':ff})
(P/'qa/HAND_COMPONENTS.json').write_text(json.dumps(rows,indent=2));(P/'cad/hand_mesh.json').write_text(json.dumps(mesh));print('HAND_GEOMETRY_VALID',len(parts),flush=True)
A.closeDocument(d.Name)
