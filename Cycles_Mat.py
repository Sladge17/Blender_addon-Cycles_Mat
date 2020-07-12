bl_info = {
    "name": 'TestTask "Convert material"',
    "author": "Sosov Maxim",
    "version": (0, 1),
    "blender": (2, 79),
    "location": "Properties > Material > Custom Changing",
    "description": "Convert existing material to Cycles material, with mixed two random colors",
    "warning": "",
    "wiki_url": "",
    "category": "Material"
    }

import bpy
import random

def rgbcolor():
    color = [0]*3
    for i in range(len(color)):
        color[i] = round(random.random(), 3)
    color.append(1)
    return tuple(color)

def parsname(struct:str):
    start = struct.find('(')+2
    end = struct.find(')', -1)-2
    return struct[start: end]


class СonvertMaterial(bpy.types.Operator):
    bl_idname="sm.convmat"
    bl_label="Сonvert material"
    
    def execute(self,context):
        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            bpy.context.scene.render.engine = 'CYCLES'
            
        obj = bpy.context.active_object
        mat_name = parsname(str(obj.data.materials[0]))

        bpy.data.materials.remove(bpy.data.materials.get(mat_name))
        mat = bpy.data.materials.new(mat_name)

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        for i in nodes:
            nodes.remove(i)

        node_fresnel = nodes.new(type='ShaderNodeFresnel')
        node_fresnel.inputs[0].default_value = 2.7
        node_fresnel.location = -450, 400

        node_rgb1= nodes.new(type='ShaderNodeRGB')
        node_rgb1.outputs[0].default_value = rgbcolor()
        node_rgb1.location = -450, 290

        node_rgb2= nodes.new(type='ShaderNodeRGB')
        node_rgb2.outputs[0].default_value = rgbcolor()
        node_rgb2.location = -450, 100

        node_mix = nodes.new(type='ShaderNodeMixRGB')
        link_fresnel_mix = links.new(node_fresnel.outputs[0], node_mix.inputs[0])
        link_rgb1_mix = links.new(node_rgb1.outputs[0], node_mix.inputs[1])
        link_rgb2_mix = links.new(node_rgb2.outputs[0], node_mix.inputs[2])
        node_mix.location = -200, 300

        node_glossyBSDF = nodes.new(type='ShaderNodeBsdfGlossy')
        link_mix_glossy = links.new(node_mix.outputs[0], node_glossyBSDF.inputs[0])
        roughness = 0.2
        node_glossyBSDF.inputs[1].default_value = roughness
        node_glossyBSDF.location = 20, 300

        mat_output = nodes.new('ShaderNodeOutputMaterial')
        link_glossy_mat = links.new(node_glossyBSDF.outputs[0], mat_output.inputs[0])
        mat_output.location = 280, 280

        mesh = bpy.context.object.data
        mesh.materials.clear()
        mesh.materials.append(mat)
        
        return{'FINISHED'}
    

class CustomPanel(bpy.types.Panel):
    bl_label = "Custom Changing"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 2
        row.operator("sm.convmat")


def register():
    bpy.utils.register_class(CustomPanel)
    bpy.utils.register_class(СonvertMaterial)

def unregister():
    bpy.utils.unregister_class(CustomPanel)
    bpy.utils.unregister_class(СonvertMaterial)

if __name__ == "__main__":
    register()
