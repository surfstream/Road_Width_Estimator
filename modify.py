from tkinter import *
import random
import math
#from pixel import Pixel
window = Tk()
road_pixels = []
road_canvas = Canvas(window, width=800, height=600)
road_canvas.pack()
def draw_line():
    pixels = []
    for pixel in road_pixels:
        pixels.append(pixel)

    road_canvas.create_line(road_pixels, fill="green")

def find_line2(start_px, end_px):
    print("find line 2")
    delta_x = end_px[0] - start_px[0]
    delta_y = end_px[1] - start_px[1]
    delta_err = float('%.1f'%(delta_y / delta_x)) # Assume deltax != 0 (line is not vertical),
        # note that this division needs to be done in a way that preserves the fractional part
    err = 0 # No error at start
    print(delta_err)
    i = 1
    from bresenham import bresenham
    print(list(bresenham(start_px[0], start_px[1], end_px[0], end_px[1])))

    for x in range(start_px[0]+1, end_px[0]):
        print("loop")
        y = (delta_err*(x-start_px[0])) + start_px[1]
        road_pixels.insert(i, (x,y))
        i += 1

def perpendicular_test(start_px,end_px):
    find_line2

def dist(p_1, p_2):
    return math.sqrt((math.pow(p_2[0] - p_1[0], 2)) +
                     (math.pow(p_2[1] - p_1[1], 2)))

def find_coord1(start_px, diff, axis, movement):
    a = 0 if axis=='x' else 1
    if(diff > 0):
            return start_px[a] + movement
    elif(diff < 0):
            return start_px[a] - movement
    else:
        return start_px[a]

def find_coord(coord, dist_ratio):
	return (road_pixels[0][coord] +
            (dist_ratio *
             (road_pixels[len(road_pixels)-1][coord] -
                road_pixels[0][coord])))

def find_pixel(dist_to_pixel, line_len):
    return (find_coord(0, (dist_to_pixel/sline_len)),
                  find_coord(1, (dist_to_pixel/line_len)))
def find_pixel_line(start_px, end_px):
    diff_x = end_px[0] - start_px[0]
    diff_y = end_px[1] - start_px[1]
    pixel_num = abs(diff_y) if diff_x == 0 else abs(diff_x)
    for index in range(1, pixel_num):
         x = find_coord1(start_px, diff_x, 'x', index)
         y = 0
         if(end_px[1] != road_pixels[index-1][1]):
             y = find_coord1(start_px, diff_y, 'y', index)
         else:
             y = end_px[1]
         road_pixels.insert(index,(x,y))
         print(road_pixels[index])
    return

def calc_pixel_line():
    line_len = dist(road_pixels[0], road_pixels[len(road_pixels)-1])
    index = 1
    for pixel_index in range(0, round(line_len)-2, 2):
        dist_to_n_pixel = pixel_index+2
        road_pixels.insert(index, find_pixel(dist_to_n_pixel, line_len))
        index += 1

def click(event):
    if len(road_pixels) < 3:
        print("clicked at", event.x, event.y)
        road_pixels.append((event.x, event.y))
        if len(road_pixels) == 2:
            road_canvas.unbind("<Button-1>")
            #find_pixel_line(road_pixels[0], road_pixels[len(road_pixels)-1])
            find_line2(road_pixels[0], road_pixels[len(road_pixels)-1])
            draw_line()
            for item in road_pixels:
            	print(item)	            	

def classifier_color(event):
	for item in road_pixels:
		rand=random.randint(0,1)
		if(rand):	
			road_canvas.create_line(item,item,fill="red")

road_canvas.bind("<Button-1>", click)
road_canvas.bind("<Button-3>", classifier_color)


mainloop() 