# Batch Render Tools

**Note**:
>+ *Currently Windows only. More info [here](#compatibility).*
>+ *Also, while I have used this add-on on very long renders without any problems, please be advised that you use this at your own risk. I suggest doing a short test render before anything big to make sure it works as you expect it to.*

---

Batch Render Tools is a series of tools to help doing batch renders of single or multiple files in Blender. Batch render tools can render many different files at once, each with their own frame ranges if desired (otherwise it uses the frame range in the target file). Simply add a batch job and browse to the desired blend file. Re-order the jobs if you want them rendered in a specific order (render happens from top to bottom).

If you have a folder of blends and want to quickly add them as jobs then you can use '**[Batch jobs from directory](#batchJobsFromDirectory)**' in the '*Additional Tools*' menu (shown below) to browse to a folder and generate the batch jobs. Alternatively, also from the '*Additional Tools*' menu, you can export the batch jobs as a Windows Batch file (.bat) using the '**[Generate .bat file](#generateBatFile)**' tool.

Enabling the add-on adds two panels to the 'Render' tab of the 'Properties Editor':
 - Batch Render Tools - The main panel for adding, managing and rendering batch render jobs.
 - Command Prompt Tools - a small panel for quickly opening the command prompt in the Blender installation directory.

## Batch Render Tools Panels:

| Batch Render Tools Panel: | Additional Tools Menu: | Command Prompt Tools Panel: |
| ------------- | ------------- | ------------- |
| ![Batch Render Tools Panel](/batchRenderTools README images/batchRenderTools Main.png) | ![Additional Tools Menu](/batchRenderTools README images/batchRenderTools Additional Tools.png) | ![Command Prompt Tools Panel](/batchRenderTools README images/batchRenderTools Command Prompt Tools.png) 

## Batch Render Tools Options:

+ **Run batch render**

  Renders all the batch jobs. The button will be disabled if there are no render jobs or if one or more jobs has an invalid filepath. Blender will not only remain active while rendering, but can be completely closed. To cancel the render close the command prompt window.

+ **Hibernate**

  Option to hibernate the computer after batch rendering. (Don't know if you have to explicitly [enable this in Windows first](https://support.microsoft.com/en-gb/kb/920730))

+ **Batch jobs summary**

  A summary of all the batch jobs: Number of batch jobs, Number of batch jobs set to render, Number of total frames that will be rendered.

+ **Add batch render job**

  Adds a new batch render job using the current blender file as the filepath (if blend file is saved, otherwise will be blank and display an error).

+ **Expand all batch jobs**

  Changes the display mode of all batch jobs to 'expanded'.

+ **Collapse all batch jobs**

  Changes the display mode of all batch jobs to 'collapsed'.

+ <a name="generateBatFile"></a>**Generate .bat file**

  Generates a windows Batch file with all the commands necessary to render the batch jobs.

+ <a name="batchJobsFromDirectory"></a>**Batch jobs from directory**

  Loads a directory of blend files as separate batch jobs.

+ **Delete all batch jobs**

  Deletes all the batch render jobs.

###Batch Job Options:

+ **Name**

  Name of the batch job to identify it. Will use the name of the blend file when using '**[Batch jobs from directory](#batchJobsFromDirectory)**'.

+ **Render**

  Whether or not the batch job will be included in the render. Means you don't have to delete a job (and lose its settings) if you want to temporarily keep a job from rendering.

+ **Copy**

  Make a copy of the batch job.

+ **Move Up/Down**

  Re-order the batch jobs. Order affects the render order (top to bottom).

+ **Delete**

  Delete the batch job.

+ <a name="filepath"></a>**Filepath**

  Filepath to the blend to be rendered. By default this will be set to the current blend file (if the blend file is saved, otherwise will be blank and display an error until a valid filepath is supplied).

+ <a name="frameRangeFromFile"></a>**Frame range from file**
 
  Use the frame range set in the target file (specified by '[**Filepath**](#filepath)') instead of specifying a custom one.

+ **Start**
 
  If '[**Frame range from file**](#frameRangeFromFile)' is disabled you can set which frame to start rendering from.

+ **End**

  If '[**Frame range from file**](#frameRangeFromFile) is disabled you can set which frame to rendering to.

## Command Prompt Tools Options:

+ <a name="openCommandPrompt"></a>**Open Command Prompt**

  Opens a command prompt window in the blender installation directory.

+ <a name="copyPath"></a>**Copy path**

  When '[**Open Command Prompt**](#openCommandPrompt)' is clicked the path to the current blend file will be copied to the clipboard.

+ **Background**

  If '[**Copy path**](#copyPath)' is enabled then the background option can be enabled which will mean blender's background command (`blender -b`) will also be copied to the clipboard. E.g. with this option enabled you will be able to paste this into the newly opened command prompt:
  
  `blender -b "PATHTOBLEND" `
  
  ## <a name="compatibility">Compatibility
  
  Unfortunately, this add-on is Windows only. I don't like making things for only one OS, but this was more a script I made to help me during a production that I decided to polish and publish, as opposed to an add-on I specifically decided to make for the Blender community. I don't know of a more OS agnostic way of doing things at the moment (I've tried) and I don't have access to the other OSs to make the specific changes each OS would need.
  
  I'm currently using `os.system` to open a Command Prompt, which is the Windows specific part. The advantage of opening a command prompt over using something like `subprocess.call` is that it is a) Non-blocking, b) Shows feedback from Blender on the progress of the render, c) Allows the render to be cancelled by simply closing the Command Prompt window and d) Doesn't require Blender to be open during rendering (aside from starting the render). If someone knows of a more generic way to do this that will work for other OSs, I am open to hearing them.
