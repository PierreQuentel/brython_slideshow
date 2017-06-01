from browser import document, html, window
import markdown
import highlight

def escape(html):
    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')
    return html
       
def _keydown(ev, path, zone, page):
    if ev.keyCode in [39, 40]: # key right or down : next page
        show(path, zone, page + 1)
        ev.preventDefault()    
    elif ev.keyCode in [37, 38]: #key left or up: previous page
        show(path, zone, page - 1)
        ev.preventDefault()

def keydown(ev, slideshow, zone):
    if ev.keyCode in [39, 40]: # key right or down : next page
        slideshow.page_num += 1
        if slideshow.page_num >= len(slideshow.pages):
            slideshow.page_num = 0
        show_page(slideshow, zone, slideshow.page_num)
        ev.preventDefault()  
    elif ev.keyCode in [37, 38]: #key left or up: previous page
        slideshow.page_num -= 1
        if slideshow.page_num < 0:
            slideshow.page_num = len(slideshow.pages) - 1
        show_page(slideshow, zone, slideshow.page_num)
        ev.preventDefault()  

def move_to(ev, slideshow, zone):
    pc = (ev.x - ev.target.abs_left) / ev.target.width
    nb_pages = len(slideshow.pages) - 1
    page = round(nb_pages * pc)
    slideshow.page_num = page
    new_pos = '%spx' %(ev.x  -ev.target.abs_left - 
        (document['tl_pos'].width / 2))
    # show page at specified position
    show_page(slideshow, zone, page)
    # set new cursor position
    document['tl_pos'].style.left = new_pos

def click_on_tl_pos(ev):
    # don't move if user clicks on current timeline position
    ev.stopPropagation()

class Slideshow:

    def __init__(self, path):
        qs = window.Date.new().getTime()
        self.src = src = open(path+'?foo=%s' %qs).read()
        self.title = ''
        self.show_page_num = False
        
        # table of contents : matches matter with page number
        self.contents = []
        
        # directives for the document
        while src.startswith('@'):
            line_end = src.find('\n')
            key,value = src[:line_end].split(' ', 1)
            if key=='@title':
                self.title = value
            elif key=='@pagenum':
                self.show_page_num = True
            elif key=="@index":
                self.contents.append([value, 0])
            src = src[line_end + 1:]

        self.pages = []
        lines = []
        for line in src.split('\n'):
            if line.startswith('../..'):
                self.pages.append('\n'.join(lines))
                lines = []
            elif line.startswith('@pause'):
                self.pages.append('\n'.join(lines))
            elif line.startswith('@index'):
                self.contents.append([line.split(' ', 1)[1], len(self.pages)])
            else:
                lines.append(line)

        if lines:
            self.pages.append('\n'.join(lines))
            
def show(path, zone, page_num=None):
    slideshow = Slideshow(path)
    
    if page_num is None:
        page_num = 0
        # check if page num was stored in a cookie
        cookies = document.cookie
        if cookies:
            elts = dict([x.strip() for x in cookie.split('=')] 
                for cookie in cookies.split(";"))
            if "page" in elts:
                page_num = int(elts["page"])
    if page_num < 0:
        page_num = 0
    elif page_num >= len(slideshow.pages):
        page_num = len(slideshow.pages) - 1

    slideshow.page_num = page_num
    document.unbind('keydown')
    document.bind('keydown',lambda ev:keydown(ev, slideshow, zone))
    
    show_page(slideshow, zone, page_num)

def run_code(ev):
    print(ev.target.text)
    
def show_page(slideshow, zone, page_num):
    # if table of contents is not empty, add it
    if slideshow.contents:
        toc = html.SELECT(name="toc")
        toc.bind('change', lambda ev: show_page(slideshow, zone, 
            int(ev.target.options[ev.target.selectedIndex].value)))
        for content in slideshow.contents:
            toc <= html.OPTION(content[0], value=content[1],
                selected=page_num>=content[1])

    slideshow.page_num = int(page_num)
    
    # store page num in a cookie
    document.cookie = "page={}".format(page_num)

    zone.clear()
    
    body = html.DIV()
    body.html = markdown.mark(slideshow.pages[page_num])[0]

    wh = window.innerHeight
    fontSize = int(18 * window.innerHeight / 800)
    body.style.fontSize = "{}px".format(fontSize)
    
    if slideshow.contents:
        body = html.DIV(toc + body)

    footer = html.DIV(Id="footer")
    footer.style.fontSize = "{}px".format(fontSize)
    if slideshow.title:
        footer <= html.DIV(slideshow.title,style=dict(display='inline'))
    if slideshow.show_page_num:
        footer <= html.SPAN(' (%s/%s)' %(page_num+1, len(slideshow.pages)),
            style=dict(display='inline'))
    timeline = html.DIV(Id='timeline')
    timeline.style.height = "{}px".format(int(fontSize/2))
    tl_pos = html.DIV(Id='tl_pos')
    timeline <= tl_pos
    timeline.bind('click', lambda ev:move_to(ev, slideshow, zone))
    tl_pos.bind('click', click_on_tl_pos)

    zone <= body + footer + timeline

    wh = window.innerHeight
    tl_pos.style.left = '%spx' %(timeline.width*page_num/len(slideshow.pages))
    document["cours"].style.minHeight = "{}px".format(int(wh * 0.9))
    
    for elt in zone.get(selector='.python'):
        src = elt.text.strip()
        width = max(len(line) for line in src.split('\n'))
        width = max(width, 30)
        # replace element content by highlighted code
        elt.html = highlight.highlight(src).html
        elt.style.width = '%sem' %int(0.7*width)
        elt.bind('click', run_code)

    for elt in zone.get(selector='.python-console'):
        src = elt.text.strip()
        lines = src.split('\n')
        result = ''
        py = ''
        py_starts = []
        for line in lines:
            if line.startswith('>>>') or line.startswith('...'):
                py += line[4:]+'\n'
                py_starts.append('<span class="python-prompt">{}</span>'.format(line[:3]))
            else:
                if py:
                    colored = highlight.highlight(py).html
                    colored_lines = colored.split('\n')
                    if result:
                        result += '\n'
                    result += '\n'.join(start+' '+line
                        for (start, line) in zip(py_starts, colored_lines))
                    py = ''
                    py_starts = []
                else:
                    line = escape(line)
                result += '\n' + line
        if py:
            colored = highlight.highlight(py).html
            colored_lines = colored.split('\n')
            if result:
                result += '\n'
            result += '\n'.join(start+' '+line
                for (start, line) in zip(py_starts, colored_lines))
            py = ''
            py_starts = []

        elt.html = result
