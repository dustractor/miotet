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

"""
        For tetgen, credit belongs to Doctor Hang Si of WAIS [NMSC]

        tetgen website:

        http://wias-berlin.de/software/tetgen/

"""


bl_info = {
        "name": "SimpleTetgenOp",
        "description":"Send the selected mesh to tetgen and create new mesh object from result.",
        "author":"dustractor@gmail.com",
        "version":(0,42),
        "blender":(2,80,0),
        "location":"3D-View Tools -> miotet",
        "warning":"",
        "wiki_url":"",
        "category": "Import-Export"
        }

import bpy
import os
import subprocess
import re

commented = re.compile("^\s*#.*").match

def read_tetgen_output(f):
    tdata = open(f,"r").readlines() 
    validlines = [line.rstrip() for line in tdata if not commented(line)]
    (header,*data) = validlines
    return header,data

def obj2tet(tetbin,obj,args):
    tempdir = bpy.app.tempdir
    tempfile = os.path.join(tempdir,obj.name + ".ply")
    tempnode = os.path.join(tempdir,obj.name + ".1.node")
    bpy.ops.export_mesh.ply(filepath=tempfile)
    tetcmd = [tetbin]
    tetargs = args.split()
    tetcmd.extend(tetargs)
    tetcmd.append(tempfile)
    proc = subprocess.Popen(tetcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    outs,errs = proc.communicate()
    if len(errs):
        print("errs:",errs)
        return
    return tempnode


class MIOTET_OT_tetgen_io(bpy.types.Operator):
    bl_idname = "miotet.tetgen_io"
    bl_label = "Miotet:Tetgen IO"
    bl_options = {"REGISTER"}
    filepath: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(default="*.node", options={'HIDDEN'})
    conv_args: bpy.props.StringProperty(default="-pq1.414a.1O10")
    def invoke(self,context,event):
        if context.active_object and context.active_object.type == "MESH":
            prefs = context.preferences.addons["miotet"].preferences
            tet_binpath = prefs.path_to_tetgen_binary
            tet_input_obj = context.active_object
            tet_args = self.conv_args
            self.filepath = obj2tet(tet_binpath,tet_input_obj,tet_args)
            if not os.path.isfile(self.filepath):
                return {"CANCELLED"}
            else:
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
        elemfile = tx['ele']
        vh,vd = read_tetgen_output(vertfile)
        eh,ed = read_tetgen_output(elemfile)
        vcount,vdim,datalayers,boundaries = map(int,vh.split())
        elemct,npertet,rgnattr = map(int,eh.split())
        vertices = list(list(map(float,_.split()[1:])) for _ in vd)
        faces = []
        elems = list(list(map(int,_.split()[1:])) for _ in ed)
        for e in elems:
            faces.extend([
                    [e[0],e[1],e[2]],
                    [e[0],e[1],e[3]],
                    [e[0],e[2],e[3]],
                    [e[1],e[2],e[3]]])
        mesh = bpy.data.meshes.new("tetmesh")
        mesh.from_pydata(vertices,[],faces)
        ob = bpy.data.objects.new("tet",mesh)
        context.collection.objects.link(ob)
        return {"FINISHED"}


class MIOTET_PT_miotet_panel(bpy.types.Panel):
    bl_label = "tetgen io"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "tetgen"
    def draw(self,context):
        layout = self.layout
        layout.enabled = context.active_object and context.active_object.type == "MESH"
        for arg in context.preferences.addons["miotet"].preferences.arguments.split(":"):
            layout.operator("miotet.tetgen_io",text=arg).conv_args = arg


class Miotet(bpy.types.AddonPreferences):
    bl_idname = __package__
    path_to_tetgen_binary: bpy.props.StringProperty(subtype="FILE_PATH",default="tetgen")
    arguments: bpy.props.StringProperty(default="-p:-pq:-pqO10:-pq1.414a.1O10")

    def draw(self,context):
        layout = self.layout
        layout.label("Multiple entries may be separated by commas.")
        layout.separator()
        layout.prop(self,"arguments")
        layout.separator()
        box = layout.box()
        for arg in self.arguments.split(":"):
            box.label(arg)
        layout.separator()
        box = layout.box()
        row = box.row()
        row.prop(self,"path_to_tetgen_binary")
        layout.label(self.path_to_tetgen_binary)


def register():
    bpy.utils.register_class(Miotet)
    bpy.utils.register_class(MIOTET_OT_tetgen_io)
    bpy.utils.register_class(MIOTET_PT_miotet_panel)

def unregister():
    bpy.utils.unregister_class(MIOTET_PT_miotet_panel)
    bpy.utils.unregister_class(MIOTET_OT_tetgen_io)
    bpy.utils.unregister_class(Miotet)
    

