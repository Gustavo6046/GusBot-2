import plugincon
import urllib2
import tinyurl


@plugincon.easy_bot_command("latex")
def latex_query(message, raw):
    if raw:
        return

    return "Rendered LaTeX: " + list(tinyurl.create("https://latex.codecogs.com/gif.latex?" + urllib2.quote(message["body"])))[0]
