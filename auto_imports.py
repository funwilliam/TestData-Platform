import os

def generate_app_initFiles():
    """預生成 '__init__.py'"""
    app_init_file = os.path.join('app', '__init__.py')
    if os.path.exists(app_init_file):
        try:
            os.remove(app_init_file)
        except:
            return
        
    for directory in ['helpers', 'models', 'routes']:
        priority_config_path = os.path.join('app', directory, 'priority.txt')
        priority = []

        if os.path.exists(priority_config_path):
            with open(priority_config_path, 'r', encoding='utf-8') as file:
                for line in file:
                    priority.append('app.' + directory + line.strip())

        with open(app_init_file, 'a', encoding='utf-8') as file:
            for module_path in priority:
                file.write(f'from {module_path} import *\n')

            for childlevel in os.listdir(os.path.join('app', directory)):
                if childlevel != '__pycache__' and childlevel != '__init__.py' and childlevel.endswith('.py'):
                    module_path = 'app.' + directory + '.' + os.path.splitext(childlevel)[0]
                    try:
                        priority.index(module_path)
                    except:
                        file.write(f'from {module_path} import *\n')

generate_app_initFiles()