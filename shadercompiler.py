import getopt
import sys
import os

import glfw

from shader import *


def main():

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

    arguments, values = getopt.getopt(sys.argv[1:], "i:p:t:o:", "")

    input_folder = arguments[0][1]
    program_file = arguments[1][1]
    template_folder = arguments[2][1]
    output_folder = arguments[3][1]

    collection = ShaderCollection(input_folder)

    directory = os.fsencode(input_folder)

    vert_extensions = (".vert", ".vertex")
    frag_extensions = (".frag", ".fragment")
    geom_extensions = (".geom", ".geometry")

    for file in os.listdir(directory):

        filename = os.fsdecode(file)

        if filename.endswith(vert_extensions):
            collection.add(filename, ShaderType.VERTEX)

        elif filename.endswith(frag_extensions):
            collection.add(filename, ShaderType.FRAGMENT)

        elif filename.endswith(geom_extensions):
            collection.add(filename, ShaderType.GEOMETRY)

    lines = open(program_file, 'r').readlines()

    for program_line in lines:
        (p_name, shaders) = [x.strip() for x in program_line.split(":")]
        shaders = [x.strip() for x in shaders.split(",")]
        collection.add_program(p_name, shaders)

    template_env = Environment(loader=FileSystemLoader(template_folder))

    for file in os.listdir(template_folder):

        filename = os.fsdecode(file)
        template = template_env.get_template(filename)

        # render output
        output = template.render({"collection": collection})

        # write output file
        out_file = open(os.path.join(output_folder, filename), 'w+')
        out_file.write(output)
        out_file.close()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
