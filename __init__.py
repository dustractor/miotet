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
        "name": "Miotet",
        "description":"Send the selected mesh to tetgen and create new mesh object from result.",
        "author":"dustractor@gmail.com",
        "version":(0,44),
        "blender":(2,80,0),
        "location":"3D-View Tools -> miotet",
        "warning":"",
        "wiki_url":"",
        "category": "Import-Export"
        }

import bpy
from subprocess import run,Popen,PIPE
from re import compile as re
from pathlib import Path
from sys import platform
from shlex import quote

commented = re("^\s*#.*").match


def find_binary(binary_name):
    wcmd = ["which","where.exe"][platform=="win32"]
    binpath = Path(run([wcmd,binary_name],capture_output=True).stdout.decode().strip()).resolve()
    if binpath.is_file():
        return str(binpath)
    

default_tetgen_binary = find_binary("tetgen")
print("default_tetgen_binary:",default_tetgen_binary)

def read_tetgen_output(f):
    tdata = open(f,"r").readlines() 
    validlines = [line.rstrip() for line in tdata if not commented(line)]
    (header,*data) = validlines
    return header,data

def obj2tet(tetbin,obj,args):
    tempdir = Path(bpy.app.tempdir)
    tempfile = tempdir/(obj.name + ".ply")
    tempnode = tempdir/(obj.name + ".1.node")
    print("export ply ...",end="")
    bpy.ops.export_mesh.ply(filepath=str(tempfile),use_ascii=True,use_selection=True)
    print("ply export ok")
    tetcmd = [tetbin]
    tetargs = list(map(quote,args.split()))
    tetcmd.extend(tetargs)
    tetcmd.append(str(tempfile))
    proc = Popen(tetcmd,stdout=PIPE,stderr=PIPE)
    outs,errs = proc.communicate()
    if len(errs):
        print("errs:",errs)
        return "-n/a-"
    print(outs.decode())
    if tempnode.is_file():
        return str(tempnode)
    else:
        return ""


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
            tetgenbin_p = prefs.tetgenbin
            print("tetgenbin_p:",tetgenbin_p)
            tet_input_obj = context.active_object
            print("tet_input_obj:",tet_input_obj)
            tet_args = self.conv_args
            print("tet_args:",tet_args)
            self.filepath = obj2tet(tetgenbin_p,tet_input_obj,tet_args)
            if not Path(self.filepath).is_file():
                print("self.filepath:",self.filepath)
                print("not a file!")
                return {"CANCELLED"}
            else:
                return self.execute(context)
        else:
            context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self,context):
        print("loading:",self.filepath)
        nodefile = Path(self.filepath)
        print("nodefile:",nodefile)
        nodedir = nodefile.parent
        print("nodedir:",nodedir)
        siblings = dict()
        
        for p in nodedir.iterdir():
            print("p:",p)
            if p.stem == nodefile.stem:
                siblings[p.suffix] = str(p)
        print("siblings:",siblings)
        vertfile = siblings.get(".node",None)
        elemfile = siblings.get(".ele",None)
        print("vertfile,elemfile:",vertfile,elemfile)
        if not(vertfile and elemfile):
            print("F")
            return {"CANCELLED"}
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
    tetgenbin: bpy.props.StringProperty(subtype="FILE_PATH",default=default_tetgen_binary)
    arguments: bpy.props.StringProperty(default="-p:-pq:-pqO10:-pq1.414a.1O10")

    def draw(self,context):
        layout = self.layout
        layout.label(text="Multiple entries may be separated by commas.")
        layout.separator()
        layout.prop(self,"arguments")
        layout.separator()
        box = layout.box()
        for arg in self.arguments.split(":"):
            box.label(text=arg)
        layout.separator()
        box = layout.box()
        row = box.row()
        row.prop(self,"tetgenbin")
        layout.label(text=self.tetgenbin)


def register():
    bpy.utils.register_class(Miotet)
    bpy.utils.register_class(MIOTET_OT_tetgen_io)
    bpy.utils.register_class(MIOTET_PT_miotet_panel)

def unregister():
    bpy.utils.unregister_class(MIOTET_PT_miotet_panel)
    bpy.utils.unregister_class(MIOTET_OT_tetgen_io)
    bpy.utils.unregister_class(Miotet)
    

