import shutil

hits =['source', 'sitemap.xml', '.git', 'google7b6f6c7b39c2bc4e.html', 'CNAME', 'baidu_verify_lk0v2QeMl2.html']

import os 
def clean(rootDir): 
    for lists in os.listdir(rootDir): 
        path = os.path.join(rootDir, lists) 
        if os.path.basename(path) not in hits:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            if os.path.isdir(path): 
                clean(path) 
clean('html')
clean('html_test')
