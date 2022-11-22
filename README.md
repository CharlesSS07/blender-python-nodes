# Blender Python Nodes
This is a blender addon that enables python programming using only blender nodes! Help wanted!

![a python node tree](/readme-assets/a_python_node_tree.png)
![another python node tree](/readme-assets/another_python_node_tree_shape_example.png)
![a python node](/readme-assets/a_python_node.png)

# How to Install into blender:
  1. run `./prepare-blender-addon.sh` in this directory (this is a convenience script)
  2. load blender, install the `pynodes.zip` file created by the previous line. Click [here](https://www.youtube.com/watch?v=vYh1qh9y1MI) to see how to install addons in blender.

# How to develop this addon:
  1. use `which blender` to find the location of your blender executable installation
  2. modify BLENDER_EXECUTABLE in blender-nodes.py to the absolut path of your executable (see blender-nodes.py for example) (this is a convenience script which automatically installs the addon into blender upon loading up)
  3. make some changes... (copy one of the files in pynodes/nodes/ and modify the `init` function of the node to add/remove input and output sockets, change up the `run` function to access your own sockets, and execute your desired code.). See PythonPrintResultBaseNode.py for a very basic base node behavior (it prints out the output to the terminal).

# Terminology:
  * Base node - node which executes the tree it is connected to return the result (could be saving contents to a file, printing result to terminal, displaying the result somewhere in blender, uploading something to the cloud, or sending an email)
  * Node - has inputs and outputs, but will never be executed unless attached to a base node

# How do we get the python functions, and parameters?
We use introspection to put all global modules into the add menu, and recursibly discover all modules. This means if you import ANY python library into the environment used by blender, you can access its functions. We try to use python to get the parameters, and when we cant, we use some clever regex. This approach does not always work unfortunatley. At the moment, many python builtins (such as exec, print, and hundreds more basic python functions) don't work welle because python can't tell us their exact parameter signature. See `pynodes/nodes/AutoNodeTypeAdder.py` for the functions used to do this upon addon registration.

# Visions:
  1. an open source deep fake creation tool
  2. an ide for arbitrary python logic
  3. a way for incorporating all the functionality of gmic, and ffmpeg into the blender compositor
  4. a more descriptive, easily interpretable way for high-level programming

# TODO:
  ~~1. make currently-running node glow/change color to green~~

  ~~2. make errors turn node red,~~ and be traceable

  ~~3. auto convert python functions into nodes~~ (has some issues such as converting builtin funcitons which have no signature)

  ~~4. auto convert python modules into nodes in categories~~ (perhaps wasn't a particularly useful feature, now its just hard to find anything

  - Run all functions and interpret python in seperate python interepreter module? So it is scoped together and doesn't clash with scope of run method in node class?
        - nodes could be "compiled" into a "file" (or just large string) for running, for speed and seperation

  5. implement blender utility nodes:

      1. mix node, compositiong nodes, color ramp, noise generation...
      2. input from rendered scenes, compositor nodes, texture nodes
      3. input from motion tracking, drivers...
      ~~4. bpy commands...~~

  6. impelemnt lots of NNs into python modules and nodes to be used artstically by blender users with little-no code expierence

      1. cyclegan x -> y, person to tom cruz or tom hanks for example. (floor -> beach, person -> celebrity, stone -> wood, greenscreen -> mask, ...)
      2. pose transfer for dancing (https://aliaksandrsiarohin.github.io/first-order-model-website/)
      3. up-resolution, infilling, image-generation, frame-interpolation
      4. material-manipulation in still frames (change glossyness/other attributes of masked object)
      5. insert smoke simulation, fluid simulation, fire
      6. automatic vegtation insert: trees, plants, plants from picture, bark, rocks, rotateable, clouds
      7. automatic time of day, re-lighting gan
      8. realism filter. go from cg environments to real-looking environment
      9. automatic depth inference from single image, and multiple images
      10. gmic qt filters node
      11. glsl, osl filters node
      12. nft-generator gan
      13. expieremental: object re-orientation gan

  7. dictionary creation node (fill in sockets as values, and use text input as key)

  8. special functions like if, while, for, try, def, class

  9. implement async

# Goals:

  1. be able to make crazy tiktoks of people without them knowing using only dfs

  2. make ai-augmented art directly in blender

  3. enable anyone to create high-quality visuals with little-to no monetary investment of their own
