import sys
import os
import glfw
import pathlib
import configparser
from queue import Queue
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from shader import *

# keys for the configuration json file
INPUT_FOLDER_KEY = "Input folder"
TEMPLATE_FOLDER_KEY = "Template folder"
OUTPUT_FOLDER_KEY = "Output folder"
PROC_FOLDER_KEY = "Processed shaders folder"
VERT_EXTENSION_KEY = "Vertex extensions"
FRAG_EXTENSION_KEY = "Fragment extensions"
GEOM_EXTENSION_KEY = "Geometry extensions"

main_thread_queue = Queue()


class Config:

    def __init__(self, file):
        config = configparser.ConfigParser()
        config.read_file(file)
        def_data = config['DEFAULT']

        self.input_folder = os.path.normpath(def_data[INPUT_FOLDER_KEY])
        self.template_folder = os.path.normpath(def_data[TEMPLATE_FOLDER_KEY])
        self.output_folder = os.path.normpath(def_data[OUTPUT_FOLDER_KEY])
        self.proc_folder = None
        self.vert_extensions = tuple(json.loads(def_data[VERT_EXTENSION_KEY]))
        self.frag_extensions = tuple(json.loads(def_data[FRAG_EXTENSION_KEY]))
        self.geom_extensions = tuple(json.loads(def_data[GEOM_EXTENSION_KEY]))

        if PROC_FOLDER_KEY in def_data:
            self.proc_folder = os.path.normpath(def_data[PROC_FOLDER_KEY])


def run(config_file, verbose=1):

    try:
        f = open(config_file)
    except IOError as e:
        print(f"File '{config_file}' not found ({e}).")
        return

    # change the working directory so that every path is relative
    # to the configuration json file
    os.chdir(pathlib.Path(config_file).parent.resolve())

    cf = Config(f)

    if verbose > 1:
        print(f"Input folder: {cf.input_folder}")
        print(f"Template folder: {cf.template_folder}")
        print(f"Output folder: {cf.output_folder}")
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

    collection = ShaderCollection(cf.input_folder)

    for file in os.listdir(cf.input_folder):

        filename = os.fsdecode(file)
        sh_type = None

        if filename.endswith(cf.vert_extensions):
            sh_type = ShaderType.VERTEX

        elif filename.endswith(cf.frag_extensions):
            sh_type = ShaderType.FRAGMENT

        elif filename.endswith(cf.geom_extensions):
            sh_type = ShaderType.GEOMETRY

        if not sh_type:
            continue

        if verbose > 1:
            print(f"» {sh_type}: " + filename)

        shader = collection.add(filename, sh_type)

        if cf.proc_folder:
            # write the processed shaders code
            out_file = open(os.path.join(cf.proc_folder, filename), 'w+')
            out_file.write(shader.source)
            out_file.close()

    template_env = Environment(loader=FileSystemLoader(cf.template_folder),
                               trim_blocks=True, lstrip_blocks=True)

    for file in os.listdir(cf.template_folder):

        filename = os.fsdecode(file)
        template = template_env.get_template(filename)

        # render output
        output = template.render({"collection": collection})

        # write output file
        out_file = open(os.path.join(cf.output_folder, filename), 'w+')
        out_file.write(output)
        out_file.close()

    if verbose > 1:
        print()

    if verbose > 0:
        print("Processing complete!")

    glfw.destroy_window(window)
    glfw.terminate()

    return cf


class FileChangeHandler(FileSystemEventHandler):

    def __init__(self, cf_file, extensions):
        self.extensions = extensions
        self.cf_file = cf_file

    def dispatch(self, event):

        if event.is_directory:
            return

        _, ext = os.path.splitext(event.src_path)

        if ext.endswith("~"):
            # temporary file, we skip it
            return

        if len(self.extensions) == 0 or ext in self.extensions:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Detected changes in {event.src_path}")
            main_thread_queue.put(lambda: run(self.cf_file))


def main():

    if len(sys.argv) < 2:
        print("Please provide the path to the configuration .ini file as the first parameter.")
        return

    watch = sys.argv[1].lower() == "-w"

    cf_path = sys.argv[1] if not watch else sys.argv[2]

    cf = run(cf_path, 2)

    if not watch:
        return

    print("Monitoring input and template folders for changes...")
    print()

    # event handler for shaders
    eh_shaders = FileChangeHandler(
        cf_path, cf.frag_extensions + cf.geom_extensions + cf.vert_extensions
    )

    # event handler for templates
    eh_temp = FileChangeHandler(cf_path, ())

    # input folder observer
    in_obs = Observer()
    in_obs.schedule(eh_shaders, cf.input_folder, recursive=True)
    in_obs.start()

    # template folder observer
    temp_obs = Observer()
    temp_obs.schedule(eh_temp, cf.template_folder, recursive=True)
    temp_obs.start()

    try:
        while True:
            f = main_thread_queue.get(True)
            f()

    except KeyboardInterrupt:
        in_obs.stop()
        temp_obs.stop()

    in_obs.join()
    temp_obs.join()


if __name__ == "__main__":
    main()
