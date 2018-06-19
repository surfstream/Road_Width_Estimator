from tkinter import *
import math
from pixel import Pixel
window = Tk()
road_pixels = []
road_canvas = Canvas(window, width=800, height=600)
road_canvas.pack()

def draw_line():
    pixels = []
    for pixel in road_pixels:
        pixels.append(pixel.coord)

    road_canvas.create_line(pixels, fill="green")

def draw_road():
    global road_pixels
    for pixel in road_pixels:
        if pixel.is_road:
            road_color = "blue"
        else:
            print("Non road")
            road_color = "red"
            print(pixel.coord)
        
        pixel_colored = [pixel.coord[0], pixel.coord[1], pixel.coord[0], pixel.coord[1]]
        road_canvas.create_line(100,100,100,100, fill="red")

def dist(p_1, p_2):
    return math.sqrt((math.pow(p_2.coord[0] - p_1.coord[0], 2)) +
                     (math.pow(p_2.coord[1] - p_1.coord[1], 2)))

def find_coord(coord, dist_ratio):
    return (road_pixels[0].coord[coord] +
            (dist_ratio *
             (road_pixels[len(road_pixels)-1].coord[coord] -
              road_pixels[0].coord[coord])))


def find_pixel(dist_to_pixel, seg_len):
    return Pixel((find_coord(0, (dist_to_pixel/seg_len)),
                  find_coord(1, (dist_to_pixel/seg_len))))

def calc_pixel_line():
    seg_len = dist(road_pixels[0], road_pixels[len(road_pixels)-1])
    index = 1
    for pixel_index in range(0, round(seg_len)-2, 2):
        dist_to_n_pixel = pixel_index+2
        road_pixels.insert(index, find_pixel(dist_to_n_pixel, seg_len))
        index += 1

def click(event):
    if len(road_pixels) < 3:
        print("clicked at", event.x, event.y)
        road_pixels.append(Pixel((event.x, event.y)))
        if len(road_pixels) == 2:
            calc_pixel_line()
            draw_line()
    elif len(road_pixels) > 2:
        print("Reaching coloring part")
        draw_road()

road_canvas.bind("<Button-1>", click)

mainloop()
