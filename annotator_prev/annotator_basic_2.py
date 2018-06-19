#!/usr/bin/env python

# example scribblesimple.py
# implementation annotator_basic.py

 # GTK - The GIMP Toolkit
 # Copyright (C) 1995-1997 Peter Mattis, Spencer Kimball and Josh MacDonald
 # Copyright (C) 2001-2004 John Finlay
 #
 # Modified to behave as an annotation tool by Biswas Parajuli.
 # bp11d@my.fsu.edu, Florida State University
 #
 # This library is free software; you can redistribute it and/or
 # modify it under the terms of the GNU Library General Public
 # License as published by the Free Software Foundation; either
 # version 2 of the License, or (at your option) any later version.
 #
 # This library is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 # Library General Public License for more details.
 #
 # You should have received a copy of the GNU Library General Public
 # License along with this library; if not, write to the
 # Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 # Boston, MA 02111-1307, USA.


import pygtk

import gtk

from math import sqrt

class Annotate:
    ''' Annotation class '''

    def __init__(self, img_name, annotations):
        self.bg_img = img_name
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(self.bg_img)
        #self.bg_pixmap, self.mask = self.pixbuf.render_pixmap_and_mask()
        self.tmp_pixmap, tmp_mask = self.pixbuf.render_pixmap_and_mask()

        self.width = self.pixbuf.get_width()
        self.height = self.pixbuf.get_height()

        self.init_polygons = {}
        self.annot_save_file = "edited_annotations.txt"
        self.load_annotations_from_file(annotations)

        self.edit_on_click = False
        self.chosen_polyline = None
        self.chosen_polygon = -1
        self.chosen_polygon_point = -1

        self.top_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.top_window.set_name ("Test Input")
        self.top_window.set_usize(800, 800)

        self.vboxOuter = gtk.VBox(False, 0)
        self.top_window.add(self.vboxOuter)
        self.vboxOuter.show()

        # Quit event
        self.top_window.connect("destroy", lambda w: gtk.main_quit())

        # Add scrolled window to the vbox
        self.scrolled_window = gtk.ScrolledWindow()
        #self.scrolled_window.set_border_width(10)
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        self.vboxOuter.pack_start(self.scrolled_window, gtk.TRUE, gtk.TRUE, 0)
        self.scrolled_window.show()
        self.scrolled_window.connect("key_press_event", self.key_press_event)

        # Add a vbox to the scrolled window
        self.vboxInner = gtk.VBox()
        self.scrolled_window.add_with_viewport(self.vboxInner)
        self.vboxInner.show()

        # Create the drawing area
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.set_size_request(self.width, self.height)
        self.vboxInner.pack_start(self.drawing_area, True, True, 0)

        self.drawing_area.show()


        # Signals used to handle backing pixmap
        self.drawing_area.connect("expose_event", self.expose_event)
        #self.drawing_area.connect("configure_event", self.configure_event)

        # Event signals
        #self.drawing_area.connect("motion_notify_event", motion_notify_event)
        self.drawing_area.connect("button_press_event", self.button_press_event)

        self.drawing_area.set_flags(gtk.CAN_FOCUS)    # To enable key press events for drawing area
        self.drawing_area.set_events(gtk.gdk.EXPOSURE_MASK
                                | gtk.gdk.LEAVE_NOTIFY_MASK
                                | gtk.gdk.BUTTON_PRESS_MASK
                                | gtk.gdk.KEY_PRESS_MASK
                                | gtk.gdk.POINTER_MOTION_MASK
                                | gtk.gdk.POINTER_MOTION_HINT_MASK)

        self.top_window.show()
        gtk.main()


    def draw_annotations(self, widget, event):
        '''
            Draw the existing polygons. Each polygon is an annotation
        '''
        for pkey in self.init_polygons.keys():
            for rect in self.init_polygons[pkey]:
                for i in range(len(rect)):
                    self.draw_brush(widget, rect[i-1][0], rect[i-1][1])
                    self.draw_line(widget, rect[i-1], rect[i])
                    self.draw_brush(widget, rect[i][0], rect[i][1])

        return True

    def load_annotations_from_file(self, fname):
        '''
           Format of each line:
           <polyline index>::<list of segments corresponding to the polylines>
        '''
        lines = [line.strip('\n').split('::') for line in open(fname, 'r').readlines()]
        for line in lines:
            polyline_index = line[0]
            if polyline_index not in self.init_polygons.keys():
                self.init_polygons[polyline_index] = []

            line = line[1].split('), ')
            tmp = []
            for tup in line:
                tup = tup.split(',')
                tmp.append((float(tup[0].strip('[()]')), float(tup[1].strip('[()]'))))
            self.init_polygons[polyline_index].append(tmp)

    # Draw a rectangle on the screen
    def draw_brush(self, widget, x, y):
        rect = (int(x-5), int(y-5), 10, 10)
        gc = widget.get_style().black_gc
        gc.set_foreground(gtk.gdk.Color('#00f'))
        self.tmp_pixmap.draw_rectangle(gc, True,
                                       rect[0], rect[1], rect[2], rect[3])
        widget.queue_draw_area(rect[0], rect[1], rect[2], rect[3])

    # Draw a line on the screen
    def draw_line(self, widget, p, q):
        gc = widget.get_style().black_gc
        gc.set_foreground(gtk.gdk.Color('#00f'))
        #tmp_pixmap, bg_mask = pixbuf.render_pixmap_and_mask()
        self.tmp_pixmap.draw_line(gc, int(p[0]), int(p[1]), int(q[0]), int(q[1]))
        #widget.queue_draw_area(int(p[0]), int(p[1]), int(q[0]), int(q[1]))
        widget.queue_draw_area(0, 0, self.width, self.height)

    def expose_event(self, widget, event):
        x , y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().white_gc,
                                    self.tmp_pixmap, x, y, x, y, width, height)
        return False

    def button_press_event(self, widget, event):

        if event.button == 1 and self.tmp_pixmap != None:
            if self.edit_on_click:
                if self.chosen_polygon == -1:
                    self.choose_polygon(event.x, event.y)
                else:
                    # Edit the polygon
                    self.init_polygons[self.chosen_polyline][self.chosen_polygon][self.chosen_polygon_point] = (int(event.x), int(event.y))
                    # Update the pixmap for new drawing of polygons
                    self.tmp_pixmap, self.tmp_mask = self.pixbuf.render_pixmap_and_mask()
                    self.draw_annotations(widget, event)
                    self.chosen_polygon = -1

            else:
                pass
                '''
                if too_close(clicked_points, (event.x, event.y)) != -1:
                    # enclosed structure has been found, so draw lines
                    # and empty the list of clicked points
                    for i in range(len(clicked_points)):
                        draw_line(widget, clicked_points[i-1], clicked_points[i])
                    #print clicked_points
                    clicked_points = []
                else:
                    clicked_points.append((event.x, event.y))
                    draw_brush(widget, event.x, event.y)
                '''
        return True

    def key_press_event(self, widget, event):
        '''
            Event for saving the current edited display as image
        '''
        pressed_key = gtk.gdk.keyval_name(event.keyval)
        if pressed_key == 's':
            self.save_curr_annotations()

        elif pressed_key == 'l':
            self.draw_annotations(widget, event)

        elif pressed_key == 'e':
            self.edit_on_click = True

        return True

    def choose_polygon(self, x, y):
        for pkey in self.init_polygons.keys():
            for index, rect in enumerate(self.init_polygons[pkey]):
                point_indx = too_close(rect, (x, y))
                if point_indx != -1:
                    self.chosen_polyline = pkey
                    self.chosen_polygon = index
                    self.chosen_polygon_point = point_indx
                    break

    def save_curr_annotations(self):
        '''
            
        '''
        #from __future__ import print_function
        #import pickle
        fp = open(self.annot_save_file, 'w')
        for pkey in self.init_polygons.keys():
            for rect in self.init_polygons[pkey]:
                #print (str(pkey) + '::', end='', file=f)
                to_write =  str(pkey) + '::' + str(rect) + '\n'
                fp.write(to_write)
                #fp.write(str(pkey) + '::')
                #pickle.dump(rect, fp)
                #fp.write('\n')
                #print (rect)
        fp.close()
            

def too_close(point_list, curr_point):
    '''
        Check if current point is too close to any of the points in point_list
        Return the index of the closest point
    '''
    if len(point_list) < 1:
        return -1

    if curr_point in point_list:
        return point_list.index(curr_point)

    # Start computing the distance
    for i, point in enumerate(point_list):
        if distance(point, curr_point) < 6.0:
            return i

    return -1

def distance(p, q):
    return sqrt( (p[0] - q[0])**2 + (p[1] - q[1])**2 )

if __name__ == "__main__":
    #Annotate('roads_sc_sat.tif', 'sc_sat_annot.txt')
    Annotate('roads_sc_sat.tif', 'sc_sat_annot.txt')

