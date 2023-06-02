import sys
import os
import glfw

from shader import *

# keys for the configuration json file
INPUT_FOLDER_KEY = "Input folder"
TEMPLATE_FOLDER_KEY = "Template folder"
OUTPUT_FOLDER_KEY = "Output folder"
PROC_FOLDER_KEY = "Processed shaders folder"
VERT_EXTENSION_KEY = "Vertex extensions"
FRAG_EXTENSION_KEY = "Fragment extensions"
GEOM_EXTENSION_KEY = "Geometry extensions"


def main():

    if len(sys.argv) < 2:
        print("Please provide the path to the configuration JSON file as the first parameter.")
        return

    try:
        f = open(sys.argv[1])
    except IOError as e:
        print(f"File '{sys.argv[1]}' not found ({e}).")
        return

    data = json.load(f)

    input_folder = os.path.normpath(data[INPUT_FOLDER_KEY])
    template_folder = os.path.normpath(data[TEMPLATE_FOLDER_KEY])
    output_folder = os.path.normpath(data[OUTPUT_FOLDER_KEY])
    proc_folder = None
    vert_extensions = tuple(data[VERT_EXTENSION_KEY])
    frag_extensions = tuple(data[FRAG_EXTENSION_KEY])
    geom_extensions = tuple(data[GEOM_EXTENSION_KEY])

    if PROC_FOLDER_KEY in data:
        proc_folder = os.path.normpath(data[PROC_FOLDER_KEY])

    print(f"Input folder: {input_folder}")
    print(f"Template folder: {template_folder}")
    print(f"Output folder: {output_folder}")
    print()

    if not glfw.init():
        print("Unable to initialize GLFW.")
        return

    glfw.window_hint(glfw.VISIBLE, False)
    window = glfw.create_window(10, 10, "hidden window", None, None)

    if not window:
        print("Unable to create window.")
        glfw.terminate()
        return

    glfw.make_context_current(window)

    collection = ShaderCollection(input_folder)

    for file in os.listdir(input_folder):

        filename = os.fsdecode(file)

        shader = None

        if filename.endswith(vert_extensions):
            print("- Vertex:   " + filename)
            shader = collection.add(filename, ShaderType.VERTEX)

        elif filename.endswith(frag_extensions):
            print("- Fragment: " + filename)
            shader = collection.add(filename, ShaderType.FRAGMENT)

        elif filename.endswith(geom_extensions):
            print("- Geometry: " + filename)
            shader = collection.add(filename, ShaderType.GEOMETRY)

        if shader and proc_folder:
            # write the processed shaders code
            out_file = open(os.path.join(proc_folder, filename), 'w+')
            out_file.write(shader.source)
            out_file.close()

    template_env = Environment(loader=FileSystemLoader(template_folder),
                               trim_blocks=True, lstrip_blocks=True)

    for file in os.listdir(template_folder):

        filename = os.fsdecode(file)
        template = template_env.get_template(filename)

        # render output
        output = template.render({"collection": collection})

        # write output file
        out_file = open(os.path.join(output_folder, filename), 'w+')
        out_file.write(output)
        out_file.close()

    print()
    print("Done!")

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
