import bpy
import os


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
    
    start = bpy.props.IntProperty()
    
    end = bpy.props.IntProperty()

    expanded = bpy.props.BoolProperty(default=True)
    
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    
    frame_range_from_file = bpy.props.BoolProperty(default=False, name="Frame range from file")
    
    name = bpy.props.StringProperty()
    
    render = bpy.props.BoolProperty(default=True)
        


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
    
    if not context.scene.hibernate:
            
        command = compileCommand()
        #Running the command directly requires an extra set of quotes around the command, batch does not
        command = 'start cmd /k " "' + command + ' "'
        command.replace('\\','/')
        print(command)
        os.system(command)
                        
    else:
                        
        command = compileCommand()
        command = 'CALL "' + command
        fileName = 'batchRender.bat'
        writeBatFile(fileName, command)
        print(command)
        os.system('start cmd /k "' + os.path.split(bpy.data.filepath)[0] + '\\' + fileName + '"')
        
        

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
            
    batFile.write(fileContent)
    batFile.write("\n")
    batFile.write("\n")
    batFile.write("shutdown -h")
    batFile.close()    



def batchJobAdd(context):
    
    newBatchJob = context.scene.batch_jobs.add()
    newBatchJob.name = "Batch Job " + str(len(bpy.context.scene.batch_jobs))
    newBatchJob.start = bpy.context.scene.frame_start
    newBatchJob.end = bpy.context.scene.frame_end
    newBatchJob.filepath = bpy.data.filepath
    
    
    
def batchJobRemove(self, context):
    
    context.scene.batch_jobs.remove(self.index)
    
    for index, batchJob in enumerate(context.scene.batch_jobs):
        
        batchJob.name = "Batch Job "+str(index+1)    
        
    
        
def batchJobMove(self, context):
    
    if self.direction == "Up":    
        
        context.scene.batch_jobs.move(self.index, self.index - 1)    

    elif self.direction == "Down":
        
        context.scene.batch_jobs.move(self.index, self.index + 1)



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
        row.operator("command_prompt.open", icon="CONSOLE")
        row = layout.row()
        row.prop(context.scene, "copy_blendfile_path", text="Copy path")
        col = row.column()
        col.enabled = context.scene.copy_blendfile_path
        col.prop(context.scene, "background", text="Background")
        
        row = layout.row()
        row.label(text="Batch render:")
        
        row = layout.row()
        row.operator("command_prompt.batch_render", icon="RENDER_ANIMATION")
        
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
        
        row = layout.row()
        row.operator("command_prompt.batch_job_add", icon="ZOOMIN")
        
        for index, batchJob in enumerate(context.scene.batch_jobs):
            
            box = layout.box()
            
            split = box.split(0.6)
            
            expandedIcon = "TRIA_RIGHT"
            if batchJob.expanded:
                expandedIcon = "TRIA_DOWN"
            
            row = split.row()
            row.prop(batchJob, "expanded", text="", emboss=False, icon=expandedIcon)
            row.prop(batchJob, "name", text="", emboss=False)
            
            renderIcon = "RESTRICT_RENDER_ON"
            if batchJob.render:
                renderIcon = "RESTRICT_RENDER_OFF"
            
            row = split.row()
            row.prop(batchJob, "render", text="", emboss=False, icon=renderIcon)
            
            column = row.column()
            row = column.row(align=True)
            operator = row.operator("command_prompt.batch_job_move", text="", icon="TRIA_UP")
            operator.direction = "Up"
            operator.index = index             
            operator = row.operator("command_prompt.batch_job_move", text="", icon="TRIA_DOWN")
            operator.direction = "Down" 
            operator.index = index
            
            column = row.column()
            row = column.row()
            row.operator("command_prompt.batch_job_remove", text="", emboss=False, icon="X").index = index
            
            if batchJob.expanded:
            
                row = box.row()
                row.prop(batchJob, "filepath", text="")
                
                row = box.row()
                row.prop(batchJob, "frame_range_from_file")
                            
                row = box.row(align=True)
                row.enabled = not batchJob.frame_range_from_file
                
                row.prop(batchJob, "start")
                row.prop(batchJob, "end")
                        
   



class OpenCommandPromptOperator(bpy.types.Operator):
    """Open an empty Command Prompt Window"""
    bl_idname = "command_prompt.open"
    bl_label = "Open Command Prompt"


    def execute(self, context):
        openCommandPrompt(context)
        return {'FINISHED'}
    
    

class BatchRenderOperator(bpy.types.Operator):
    """Run the batch render"""
    bl_idname = "command_prompt.batch_render"
    bl_label = "Run batch render"


    def execute(self, context):
        runBatchRender(context)
        return {'FINISHED'}
    
    
    
class BatchJobRemoveOperator(bpy.types.Operator):
    """Add a new batch render job"""
    bl_idname = "command_prompt.batch_job_add"
    bl_label = "Add batch render job"


    def execute(self, context):
        batchJobAdd(context)
        return {'FINISHED'}  

    
    
class BatchJobRemoveOperator(bpy.types.Operator):
    """Remove the selected batch render job"""
    bl_idname = "command_prompt.batch_job_remove"
    bl_label = "Remove batch render job"

    index = bpy.props.IntProperty()

    def execute(self, context):
        batchJobRemove(self, context)
        return {'FINISHED'}  
     
     
         
class BatchJobMoveOperator(bpy.types.Operator):
    """Move the selected batch render job up or down"""
    bl_idname = "command_prompt.batch_job_move"
    bl_label = "Move batch render job"

    index = bpy.props.IntProperty()
    direction = bpy.props.StringProperty(default="Up")

    def execute(self, context):
        batchJobMove(self, context)
        return {'FINISHED'}       
     
    
        
def register():

    bpy.utils.register_module(__name__)



def unregister():
    
    bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
    register() 
    
    
#register()   