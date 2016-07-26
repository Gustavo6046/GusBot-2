import glob
import os
import json
import ntpath

def fetch_name(filepath):
    return os.path.splitext(ntpath.basename(filepath))[0]

def register_all_plugins():	
	plugin_list = [fetch_name(module) for module in glob.glob("plugins/*.py") if os.path.isfile(module)]

	json.dump(plugin_list, open("pluginlist.json", "w"))
	
	return plugin_list
	
if __name__ == "__main__":
	print "Registered following plugins into JSON list: " + " ".join(register_all_plugins())