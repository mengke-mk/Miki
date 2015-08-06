#coding=utf-8
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from jinja2 import Environment
import plugin.tool as tool
from plugin import highlight, toc, meta

class TocRenderer(highlight.HighlightMixin, toc.TocMixin ,mistune.Renderer):
    pass

def get_post_list(pwd):
    for root,dirs,files in os.walk(pwd):
        for filespath in files:
            yield os.path.join(root,filespath)

def md2html(md_pwd, mdp, template, root_path):
    try:
        template = open('template/'+template+'.html','r').read()
        utils = open('template/utils.html').read()
        md = open(md_pwd, 'r').read()
    except:
        tool.log('error')('file not found')
        return 
    mdp.renderer.reset_toc()
    args, md = meta.parse(md)
    md = Environment().from_string(utils+md).render()
    content = mdp(md) 
    args['content'] = content
    args['root_path'] = root_path
    html = Environment().from_string(template).render(**args)
    try:
        _pwd = os.path.join('html', args['categories'], args['title']+'.html')
        _dir = os.path.dirname(_pwd)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        f = open(_pwd,'w')
        f.write(html)
        return args
    except:
        tool.log('error')('html dir not found')


def md2html_all(mdp, template, root_path):
    import shutil
    pwd = os.getcwd()
    _pwd = os.path.join(pwd, "html")
    if not os.path.exists(_pwd):
        os.makedirs(_pwd)
    if not os.path.exists(os.path.join(_pwd, "source")):
        shutil.copytree("source", os.path.join(_pwd, "source"))
    dist = {}
    for md_pwd in get_post_list(os.path.join(pwd, "post")):
        args = md2html(md_pwd, mdp, template, root_path)
        title = args['title']
        categories = args['categories']
        if categories in dist.keys():
            dist[categories].append(title)
        else:
            dist[categories] = []
            dist[categories].append(title)
    try:
        template = open('template/index.html','r').read()
    except:
        tool.log('error')('index template not found')
    html = Environment().from_string(template).render(dist=dist, root_path=root_path) 
    f = open('html/index.html', 'w')
    f.write(html)

if __name__ == '__main__':
    renderer = TocRenderer(linenos=True, inlinestyles=False)
    #renderer.reset_toc()
    mdp = mistune.Markdown(escape=True, renderer=renderer)
    md2html_all(mdp, 'post')
