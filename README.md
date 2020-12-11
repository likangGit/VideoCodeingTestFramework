# Video Coding Test Framework

To test some video coding method, We design this framework.  

## Run
1. modify "config.yaml"  
   **note:** the order of stage means the order of execution. If you want to change order of execution, you can just exchange the order of stage in 'config.yaml'.  
   **note:** the method name below the stage name means what method you want to execute in this stage. You can use one or several methods in one stage. If you don not want to execute the method, you can just comment it.
2. run command `python main.py`
   
## Develop
The framework is designed to add modules in the form of plug-ins. You can add your own plugin by follwing the setps below:
1. create a python file in path "module/"
2. Write your own code by imitating the code in 'frame_rate.py' or 'ffmpeg_resolution.py' and add it to the new python file
3. add config information in config.yaml according to the code you wrote.