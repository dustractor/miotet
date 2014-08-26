# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
        "name": "miotet",
        "description":"my io for tetgen",
        "author":"dustractor",
        "version":(0,1),
        "blender":(2,71,0),
        "location":"",
        "warning":"",
        "wiki_url":"",
        "category": "Import-Export"
        }

import bpy
import os
import subprocess
import re

commented = re.compile("^\s*#.*").match

def read_(f):
    tdata = open(f,"r").readlines() 
    validlines = [line.rstrip() for line in tdata if not commented(line)]
    (header,*data) = validlines
    return header,data

def obj2tet(obj,args):
    tempdir = bpy.app.tempdir
    here = os.path.dirname(__file__)
    tempfile = os.path.join(tempdir,obj.name + ".ply")
    tempnode = os.path.join(tempdir,obj.name + ".1.node")
    bpy.ops.export_mesh.ply(filepath=tempfile)
    tetbin = os.path.join(here,"tetgen")
    tetcmd = [tetbin]
    tetargs = args.split()
    tetcmd.extend(tetargs)
    tetcmd.append(tempfile)
    print("tetcmd:",tetcmd)
    proc = subprocess.Popen(tetcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    outs,errs = proc.communicate()
    print("outs:",outs)
    print("errs:",errs)
    return tempnode


class MIOTET_OT_tetgen_import(bpy.types.Operator):
    bl_idname = "miotet.tetgen_import"
    bl_label = "Miotet:Tetgen Import"
    bl_options = {"REGISTER","UNDO"}
    filepath = bpy.props.StringProperty()
    filter_glob = bpy.props.StringProperty(default="*.node", options={'HIDDEN'})
    conv_args = bpy.props.StringProperty(default="-pq1.414a.1")
    def invoke(self,context,event):
        if context.active_object and context.active_object.type == "MESH":
            self.filepath = obj2tet(context.active_object,self.conv_args)
            return self.execute(context)
            
        else:
            context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    def execute(self,context):
        print(self,"loading",self.filepath)
        nodefile = self.filepath
        nodedir = os.path.dirname(nodefile)
        nodename = os.path.basename(nodefile)
        nnpre = nodename.rpartition(".")[0]
        tx = {}
        for t in os.listdir(nodedir):
            if t.startswith(nnpre):
                k = t.rpartition(".")[2]
                tx[k] = os.path.join(nodedir,t)

        vertfile = tx['node']
        facefile = tx['face']
        elemfile = tx['ele']
        vh,vd = read_(vertfile)
        fh,fd = read_(facefile)
        eh,ed = read_(elemfile)
        vcount,vdim,datalayers,boundaries = map(int,vh.split())
        fcount,idk = map(int,fh.split())
        elemct,npertet,rgnattr = map(int,eh.split())
        vertices = list(list(map(float,_.split()[1:])) for _ in vd)
        faces = []#list(list(map(int,_.split()[1:-1])) for _ in fd)
        elems = list(list(map(int,_.split()[1:])) for _ in ed)
        for e in elems:
            faces.append([e[0],e[1],e[2]])
            faces.append([e[0],e[1],e[3]])
            faces.append([e[0],e[2],e[3]])
            faces.append([e[1],e[2],e[3]])
        mesh = bpy.data.meshes.new("tetmesh")
        mesh.from_pydata(vertices,[],faces)
        ob = bpy.data.objects.new("tet",mesh)
        context.scene.objects.link(ob)

        return {"FINISHED"}

def register():
    bpy.utils.register_module(__name__)
    

def unregister():
    bpy.utils.unregister_module(__name__)
    

