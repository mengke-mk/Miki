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

def generate_meta(args):
    p = u'<meta name = "description" content="' + args['title']  + '">'
    p += u'<meta name = "Keywords" content="' + args['tags'] + '">'
    return p

def md2html(md_pwd, mdp, template, root_path, des):
    try:
        template = open('template/'+template+'.html','r').read()
        utils = open('template/utils.html').read()
        md = open(md_pwd, 'r').read()
    except:
        tool.log('error')('file not found')
        return 
    mdp.renderer.reset_toc()
    args, md = meta.parse(md)
    if args['categories'] == 'draft':
        return args
    md = Environment().from_string(utils+md).render()
    content = mdp(md) 
    args['content'] = content
    args['root_path'] = root_path
    args['meta'] = generate_meta(args)
    args['this_href'] = "blog.septicmk.com/" +  args['categories'] + '/' + args['shortcut'] + '.html'
    html = Environment().from_string(template).render(**args)
    try:
        _pwd = os.path.join(des, args['categories'], args['shortcut']+'.html')
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
    if root_path == '':
        des = 'html'
    else:
        des = 'html_test'

    pwd = os.getcwd()
    _pwd = os.path.join(pwd, des)
    if not os.path.exists(_pwd):
        os.makedirs(_pwd)
    if not os.path.exists(os.path.join(_pwd, "source")):
        shutil.copytree("source", os.path.join(_pwd, "source"))
    dist = {}

    for md_pwd in get_post_list(os.path.join(pwd, "post")):
        args = md2html(md_pwd, mdp, template, root_path, des)
        url = args['shortcut']
        title = args['title'] 
        categories = args['categories']
        if categories in dist.keys():
            dist[categories].append((url,title))
        else:
            dist[categories] = []
            dist[categories].append((url,title))
    if 'draft' in dist.keys():
        del dist['draft']
    try:
        template = open('template/index.html','r').read()
    except:
        tool.log('error')('index template not found')

    html = Environment().from_string(template).render(dist=dist, root_path=root_path) 
    f = open( des + '/index.html', 'w')
    f.write(html)

def get_mod_time(pwd):
    import time
    FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
    ft = time.localtime(os.stat(pwd).st_mtime)
    return time.strftime(FORMAT,ft)

def sitemap_update():
    pwd = os.getcwd()
    _pwd = os.path.join(pwd,'html','sitemap.xml')
    des = open(_pwd, 'w')
    conf = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
      http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
"""
    conf += u"<url><loc>http://blog.septicmk.com/</loc>"
    conf += u"<lastmod>"+ get_mod_time("html/index.html") +u"</lastmod>"
    conf += u"<changefreq>weekly</changefreq>"
    conf += u"<priority>1.00</priority></url>"
    list_dirs = os.walk('html')
    for root, dirs, files in list_dirs:
        for f in files:
            if f.endswith('.html') and f!="google7b6f6c7b39c2bc4e.html" and f!='baidu_verify_lk0v2QeMl2.html':
                conf += u"<url><loc>http://blog.septicmk.com/"+ os.path.join(root, f)[5:] + u"</loc>"
                conf += u"<lastmod>"+ get_mod_time(os.path.join(root,f)) + u"</lastmod>"
                conf += u"<changefreq>weekly</changefreq>"
                conf += u"<priority>0.80</priority></url>"
    conf += u"</urlset>"
    des.write(conf)

if __name__ == '__main__':
    renderer = TocRenderer(linenos=True, inlinestyles=False)
    #renderer.reset_toc()
    mdp = mistune.Markdown(escape=True, renderer=renderer)
    if len(sys.argv) == 1:
        md2html_all(mdp, 'post', '')
    elif sys.argv[1] == 'test':
        md2html_all(mdp, 'post', '/home/septicmk/blog/html_test')
    elif sys.argv[1] == 'sitemap':
        sitemap_update()

