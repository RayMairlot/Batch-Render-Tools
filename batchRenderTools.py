import bpy
import os
from bpy_extras.io_utils import ImportHelper


bl_info = {
    "name": "Batch Render Tools",
    "author": "Ray Mairlot",
    "version": (0, 5),
    "blender": (2, 77, 0),
    "location": "Properties > Render > Batch Render Tools",
    "description": "A series of tools to help with managing batch renders",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
    }


class batchJobsPropertiesGroup(bpy.types.PropertyGroup):
    
    start = bpy.props.IntProperty(description="Frame to start rendering from")
    
    end = bpy.props.IntProperty(description="Frame to render to")

    expanded = bpy.props.BoolProperty(default=True)
    
    filepath = bpy.props.StringProperty(description="Location of the blend file to render")
    
    frame_range_from_file = bpy.props.BoolProperty(default=False, name="Frame range from file", description="Use the frame range set in the file")
    
    name = bpy.props.StringProperty(description="Name of the render job")
    
    render = bpy.props.BoolProperty(default=True, description="Include this job when 'Run batch render' is pressed")
        


bpy.utils.register_class(batchJobsPropertiesGroup)


bpy.types.Scene.copy_blendfile_path = bpy.props.BoolProperty(default=True, description="Copy the current blend file's path to the clipboard")

bpy.types.Scene.background = bpy.props.BoolProperty(default=True, description="Copied path has 'background' (-b) command")

bpy.types.Scene.batch_jobs = bpy.props.CollectionProperty(type=batchJobsPropertiesGroup)

bpy.types.Scene.hibernate = bpy.props.BoolProperty(default=False, name="Hibernate", description="Hibernate the computer after rendering")
    


def openCommandPrompt(context):

    binaryPath = os.path.split(bpy.app.binary_path)[0]

    binaryPath = binaryPath.replace('\\', '/' )

    os.system("start cmd /K cd "+binaryPath)
    
    if context.scene.copy_blendfile_path:
        
        blenderCommand = ""
        
        if context.scene.background:
            
            blenderCommand = "blender -b "
            
        bpy.context.window_manager.clipboard = blenderCommand+'"'+bpy.data.filepath+'" '
        
        

def runBatchRender(context):
                
    command = compileCommand()    
    
    hibernate = ""
    if context.scene.hibernate:
        hibernate = "shutdown -h"
    
    #Running the command directly requires an extra set of quotes around the command, batch does not
    command = 'start cmd /k " "' + command + ' " ' + hibernate
    command.replace('\\','/')
    print(command)
    os.system(command)
                                          
#    command = compileCommand()
#    command = 'CALL "' + command
#    fileName = 'batchRender.bat'
#    writeBatFile(fileName, [command, "shutdown -h"])
#    print(command)
#    os.system('start cmd /k "' + os.path.split(bpy.data.filepath)[0] + '\\' + fileName + '"')        
        

def compileCommand():
            
    command = bpy.app.binary_path + '" -b '
    
    batchJobs = [batchJob for batchJob in bpy.context.scene.batch_jobs if batchJob.render]
    
    for batchJob in batchJobs:
        
        frameRange = ""
        
        if not batchJob.frame_range_from_file:    
            
            frameRange = ' -s ' + str(batchJob.start) + ' -e ' + str(batchJob.end)
        
        command += '"' + batchJob.filepath + '"' + frameRange + ' -a ' 

    return command

    #os.system('start cmd /k "'+binaryPath+'" -b '+blendFilePath+' -s 1 -e 3 -a '+blendFilePath+' -s 10 -e 12 -a')



def writeBatFile(fileName, fileContent):
    
    batFile = open(fileName, 'w')
    
    for command in fileContent:
            
        batFile.write(command)
        batFile.write("\n")
        batFile.write("\n")
        
    batFile.close()    



def batchJobAdd(self, context, filepath="", blenderFile=""):
    
    newBatchJob = context.scene.batch_jobs.add()
    newBatchJob.name = "Batch Job " + str(len(bpy.context.scene.batch_jobs))
    newBatchJob.start = bpy.context.scene.frame_start
    newBatchJob.end = bpy.context.scene.frame_end
    
    if filepath == "":
    
        newBatchJob.filepath = bpy.data.filepath
    
    else:
        
        newBatchJob.filepath = os.path.join(filepath, blenderFile)
        newBatchJob.frame_range_from_file = self.frame_range_from_file
        newBatchJob.expanded = self.expanded
        
        
    
def batchJobRemove(self, context):
    
    context.scene.batch_jobs.remove(self.index)
            
        
        
def batchJobMove(self, context):
    
    if self.direction == "Up":    
        
        context.scene.batch_jobs.move(self.index, self.index - 1)    

    elif self.direction == "Down":
        
        context.scene.batch_jobs.move(self.index, self.index + 1)
        

        
def batchJobCopy(self, context):
    
    newBatchJob = context.scene.batch_jobs.add()
    
    for property in context.scene.batch_jobs[self.index].items():
        
        newBatchJob[property[0]] = property[1]
        
    newBatchJob.name = "Batch Job " + str(len(bpy.context.scene.batch_jobs))
            
             
        
def batchJobDeleteAll(self, context):
        
    bpy.context.scene.batch_jobs.clear()    
    
    
    
def batchJobExpandAll(self, context):
            
    for batchJob in context.scene.batch_jobs:
        
        batchJob.expanded = self.expand



def batchJobsFromDirectory(self, context):
    
    filepath = self.filepath
        
    if os.path.isfile(filepath):
        
        filepath = os.path.split(filepath)[0]    
    
    
    blendFiles = [file for file in os.listdir(filepath) if os.path.splitext(file)[1] == ".blend"]
    
    for blenderFile in blendFiles:
        
        batchJobAdd(self, context, filepath, blenderFile)
    
        
        
def selectBlendFile(self, context):
            
    context.scene.batch_jobs[self.index].filepath = self.filepath   
        
        
        
def batchJobConvertToBatFile(self, context):
    
    command = compileCommand()
    command = 'CALL "' + command
    fileName = self.filepath
    
    commands = []
    commands.append(command)
    
    if context.scene.hibernate:
    
        commands.append("shutdown -h")
                
    writeBatFile(fileName, commands)
                        


class BatchJobsFromDirectoryOperator(bpy.types.Operator, ImportHelper):
    """Generate batch jobs from a folder of blends you want to render"""    
    bl_idname = "batch_render_tools.batch_jobs_from_directory"
    bl_label = "Batch jobs from directory"


    filter_glob = bpy.props.StringProperty(default="*.blend",options={'HIDDEN'})
    
    filename = bpy.props.StringProperty(default="")
    
    frame_range_from_file = bpy.props.BoolProperty(default=False, name="Frame ranges from files") 
    expanded = bpy.props.BoolProperty(default=True, name="Expanded")
            
            
    def execute(self, context):
        
        batchJobsFromDirectory(self, context)
        
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        
        self.filename = ""
        
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}
    
    
    
class SelectBlendFileOperator(bpy.types.Operator, ImportHelper):
    """Select the blend file for this batch job"""
    bl_idname = "batch_render_tools.select_blend_file"
    bl_label = "Select blend file"

    index = bpy.props.IntProperty(options={'HIDDEN'})

    filter_glob = bpy.props.StringProperty(default="*.blend",options={'HIDDEN'})
                       
    def execute(self, context):
        
        selectBlendFile(self, context)
        
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        
        #self.filename = ""
        
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}    
    

    
class BatchJobsConvertToBatFileOperator(bpy.types.Operator, ImportHelper):
    """Convert the batch jobs to a .bat file of commands"""
    bl_idname = "batch_render_tools.convert_to_bat"
    bl_label = "Generate .bat file from batch jobs"


    filter_glob = bpy.props.StringProperty(default="*.bat",options={'HIDDEN'})
        
        
    def execute(self, context):
                        
        batchJobConvertToBatFile(self, context)
        
        return {'FINISHED'}
    
    
    def invoke(self, context, event):
        
        self.filename = "batchRender.bat"
        
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}
        
      

class BatchJobsMenu(bpy.types.Menu):
    bl_label = "Batch Jobs Menu"
    bl_idname = "RENDER_MT_batch_jobs"

    def draw(self, context):
        layout = self.layout

        layout.operator("batch_render_tools.expand_all_batch_jobs", text="Expand all batch jobs", icon="TRIA_DOWN_BAR").expand = True
        layout.operator("batch_render_tools.expand_all_batch_jobs", text="Collapse all batch jobs", icon="TRIA_UP_BAR").expand = False
        layout.operator("batch_render_tools.convert_to_bat", text="Generate .bat file", icon="LINENUMBERS_ON")
        layout.operator("batch_render_tools.batch_jobs_from_directory", text="Batch jobs from directory", icon="FILESEL")
        layout.operator("batch_render_tools.delete_all_batch_jobs", icon="X")



class CommandPromptPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Command Prompt Tools"
    bl_idname = "OBJECT_PT_command_prompt_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("batch_render_tools.browse_to_blend", icon="CONSOLE")
        row = layout.row()
        row.prop(context.scene, "copy_blendfile_path", text="Copy path")
        col = row.column()
        col.enabled = context.scene.copy_blendfile_path
        col.prop(context.scene, "background", text="Background")
        
        row = layout.row()
        row.label(text="Batch render:")
        
        row = layout.row()
        row.operator("batch_render_tools.run_batch_render", icon="RENDER_ANIMATION")
        
        row = layout.row()
        row.prop(context.scene, "hibernate")
        
        row = layout.row()
        row.label("Manage Batch Jobs:")
        
        row = layout.row()
        row.label("Number of batch jobs: "+str(len(context.scene.batch_jobs)))
        
        frames = 0
        for batchJob in context.scene.batch_jobs:
            frames += batchJob.end - batchJob.start
        
        row = layout.row()    
        row.label("Number of frames: "+str(frames))
        
        row = layout.row(align=True)
        row.operator("batch_render_tools.add_batch_job", icon="ZOOMIN")
        row.menu(BatchJobsMenu.bl_idname, text="", icon="DOWNARROW_HLT")
        
        for index, batchJob in enumerate(context.scene.batch_jobs):
            
            box = layout.box()
                        
            expandedIcon = "TRIA_RIGHT"
            if batchJob.expanded:
                expandedIcon = "TRIA_DOWN"
            row = box.row(align=True)
            row.prop(batchJob, "expanded", text="", emboss=False, icon=expandedIcon)
            row.prop(batchJob, "name", text="")
            
            row.separator()
            
            row.prop(batchJob, "render", text="", icon="RESTRICT_RENDER_OFF")
            row.operator("batch_render_tools.copy_batch_job", text="", icon="GHOST").index = index
            
            row.separator()
                            
            operator = row.operator("batch_render_tools.move_batch_job", text="", icon="TRIA_UP")
            operator.direction = "Up"
            operator.index = index             
            operator = row.operator("batch_render_tools.move_batch_job", text="", icon="TRIA_DOWN")
            operator.direction = "Down" 
            operator.index = index
            
            row.separator()
            
            row.operator("batch_render_tools.remove_batch_job", text="", emboss=False, icon="X").index = index
            
            if batchJob.expanded:
            
                row = box.row(align=True)
                row.prop(batchJob, "filepath", text="")
                row.operator("batch_render_tools.select_blend_file", text="", icon="FILESEL").index = index
                
                row = box.row()
                row.prop(batchJob, "frame_range_from_file")
                            
                row = box.row(align=True)
                row.enabled = not batchJob.frame_range_from_file
                
                row.prop(batchJob, "start")
                row.prop(batchJob, "end")
                        
   

class OpenCommandPromptOperator(bpy.types.Operator):
    """Open an empty Command Prompt Window"""
    bl_idname = "batch_render_tools.browse_to_blend"
    bl_label = "Open Command Prompt"


    def execute(self, context):
        openCommandPrompt(context)
        return {'FINISHED'}
    
    

class BatchRenderOperator(bpy.types.Operator):
    """Run the batch render"""
    bl_idname = "batch_render_tools.run_batch_render"
    bl_label = "Run batch render"


    def execute(self, context):
        runBatchRender(context)
        return {'FINISHED'}
    
    
    
class BatchJobRemoveOperator(bpy.types.Operator):
    """Add a new batch render job"""
    bl_idname = "batch_render_tools.add_batch_job"
    bl_label = "Add batch render job"


    def execute(self, context):
        batchJobAdd(self, context)
        return {'FINISHED'}  

    
    
class BatchJobRemoveOperator(bpy.types.Operator):
    """Remove the selected batch render job"""
    bl_idname = "batch_render_tools.remove_batch_job"
    bl_label = "Remove batch render job"

    index = bpy.props.IntProperty()

    def execute(self, context):
        batchJobRemove(self, context)
        return {'FINISHED'}  
     
     
         
class BatchJobMoveOperator(bpy.types.Operator):
    """Move the selected batch render job up or down"""
    bl_idname = "batch_render_tools.move_batch_job"
    bl_label = "Move batch render job"

    index = bpy.props.IntProperty()
    direction = bpy.props.StringProperty(default="Up")

    def execute(self, context):
        batchJobMove(self, context)
        return {'FINISHED'}    
    
    
    
class BatchJobCopyOperator(bpy.types.Operator):
    """Copy the selected batch render"""
    bl_idname = "batch_render_tools.copy_batch_job"
    bl_label = "Copy the batch render job"
    
    index = bpy.props.IntProperty()
    
    def execute(self, context):
        batchJobCopy(self, context)
        return {'FINISHED'}  
    
    
    
class BatchJobDeleteAllOperator(bpy.types.Operator):
    """Delete all the batch render jobs"""
    bl_idname = "batch_render_tools.delete_all_batch_jobs"
    bl_label = "Delete all batch jobs"
        
    def execute(self, context):
        batchJobDeleteAll(self, context)
        return {'FINISHED'}   
    
    
    
class BatchJobExpandAllOperator(bpy.types.Operator):
    """Expand/collapse all the batch render jobs"""
    bl_idname = "batch_render_tools.expand_all_batch_jobs"
    bl_label = "Delete all batch jobs"
    
    expand = bpy.props.BoolProperty()
        
    def execute(self, context):
        batchJobExpandAll(self, context)
        return {'FINISHED'}   
    
    
                                        
def register():

    bpy.utils.register_module(__name__)



def unregister():
    
    bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
    register() 
    
    
#register()   