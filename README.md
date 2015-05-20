brython-slideshow
=================

This module is used to develop in-browser slideshows

It is developed in Python and runs with [Brython](http://brython.info). To
install it, copy the file slideshow.py in the same folder as the HTML file
holding the presentation (an example of such HTML file is given below)

It exposes a single function :

`show(path, zone, page_num=0)`

where _path_ is the relative or absolute URL of the presentation, and _zone_
is a reference of the DOM element (usually a DIV) where the presentation is
inserted

The presentation itself is a text file, supporting the following syntax
elements :

1. Directives for the whole document
------------------------------------

This information must be on the first lines of the presentation

Their syntax is : `@key value` where _key_ can currently take the following
values :

- title : the title of the presentation. If provided, the matching _value_
will be printed at the bottom of each slide

- pagenum : if provided, the current page number and the total number of
pages in the presentation will be printed at the bottom of each page

2. Directives inside a slide
---------------------------- 

`../..` at the beginning of a line indicates the end of the current slide

`@pause` inside a page puts the presentation on hold until a navigation key
is pressed

The content of a slide is written using the markdown syntax

3. Table of contents
--------------------

Inside a slide, a line starting with `@index ` creates an element in the
presentation table of contents. The text following `@index` will be displayed
in a box at the top of the document ; selecting this text will show the page
where the index was defined

4. Navigation
-------------

Navigation inside the slideshow can be done
- with the keyboard arrows (left, right, up, down)
- with the table of content, if any
- by clicking on the horizontal line at the bottom of each page

4. Example
----------

Presentation file "demo.pss" :

    @title My presentation
    @pagenum True
    
    Brython
    =======
    
    ../..
    @index Introduction
    
    What is Brython ?
    =================
    
    - an implementation of Python 3 for web browsers
    
    - an interface with DOM elements and events
    
    ../..
    @index Getting started
    Getting started
    ===============

    Visit the [Brython site](http://brython.info) for demos and documentation
    

HTML page for the presentation :

    <html>

    <head>
    <script src="http://brython.info/src/brython.js">
    <title>Brython slideshow demo</title>
    
    <script type="text/python">
    from browser import document
    import slideshow
    
    slideshow.show("demo.pss", document["content"])
    </script>
    
    </head>

    <body>
    <div id="content"></div>
    </body>
    
    </html>
    