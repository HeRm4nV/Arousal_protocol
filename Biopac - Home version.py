#!/usr/bin/env python3.10.9
# coding=utf-8

"""
tested in Python 3.10.9
"""
import pygame , sys, os, serial
from pygame.locals import FULLSCREEN, USEREVENT, KEYDOWN, KEYUP, K_SPACE, K_RETURN, K_ESCAPE, QUIT, Color, K_c
from os.path import isfile, join
from random import shuffle, getrandbits
from time import gmtime, strftime

testing = False

## Configurations:
FullScreenShow = True # Pantalla completa automáticamente al iniciar el experimento
keys = [pygame.K_SPACE] # Teclas elegidas para mano derecha o izquierda
test_name = "AAT"
date_name = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

if os.name == 'posix':
    try:
        os.system("sudo chmod o+rw /dev/ttyUSB0")
        print("serial ttyUSB0 port writable")
    except:
        print("failed to make the serial ttyUSB0 port writable!")
    directory_separator = "/"
elif os.name == 'nt':
    directory_separator = "\\"
else:
    print("OS not supported")

## Image Loading
HAneg_images_list = [join('media', 'images', 'HAneg', f) for f in os.listdir(join('media', 'images', 'HAneg')) if isfile(join('media', 'images', 'HAneg',f))]
HApos_images_list = [join('media', 'images', 'HAneg', f) for f in os.listdir(join('media', 'images', 'HAneg')) if isfile(join('media', 'images', 'HAneg',f))]
LAneg_images_list = [join('media', 'images', 'HAneg', f) for f in os.listdir(join('media', 'images', 'HAneg')) if isfile(join('media', 'images', 'HAneg',f))]
LApos_images_list = [join('media', 'images', 'HAneg', f) for f in os.listdir(join('media', 'images', 'HAneg')) if isfile(join('media', 'images', 'HAneg',f))]

animals_id_list = ["1111", "1201", "1205", "1300", "1313", "1450", "1525", "1602", "1603", "1604", "1605", "1610", "1630", "1661", "1670", "1910", "2688", "8620", "9561"]

# triggers
start_trigger = 300
new_image_trigger = 100 # +50 if is an animal image (+20 if is an HA image, +0 if not)
start_block_trigger = 200 # +20 if block is HA, + 0 if not, + 40 if is second block + 0 if not
space_trigger = 50

base_size = (1024, 768)

## Onscreen instructions
def select_slide(slide_name):
    
    basic_slides = {
        'welcome': [
            u"Bienvenido/a, a este experimento!!!",
            " ",
            u"Se te indicará paso a paso que hacer.",
            " ",
            u"Para avanzar presiona la barra espaciadora."
            ],
        'Instructions': [
            u"Durante los próximos 20 minutos se presentarán una serie de imágenes en la pantalla",
            u"del computador y al mismo tiempo, escucharás música a través de los auriculares.",
            " ",
            u"Presta por favor mucha atención a dichas imágenes. Se van a presentar",
            u"todo tipo de escenas con personas, animales y naturaleza.",
            " ",
            u"Cada vez que observes una imagen que contenga animales, cualquier",
            u"tipo de animal, presiona la barra espaciadora del computador.",
            " ",
            u"Para comenzar presiona la barra espaciadora."
            ],
        'farewell': [
            u"El Experimento ha terminado.",
            "",
            u"Muchas gracias por su colaboración!!"
            ]
        }

    selected_slide = basic_slides[slide_name]
    
    return (selected_slide)

def send_trigger(latency):
    """Sends a trigger to the parallell port"""
    try:
        if not testing:
            ser.open()  # Open port
        pygame.time.delay(latency)  # Keep port open for some ms
        if not testing:
            ser.close()  # Get back to zero after some ms
        print('Trigger with latency of ' + str(latency) + ' ms was sent')
    except:
        pass
        print('Failed to open the port for ' + str(latency) + ' ms')

def init_com(baudrate= 115200):
    """Creates and tests a serial port"""
    global ser
    ser = serial.Serial()
    if os.name == 'posix':
        ser.port = "/dev/ttyUSB0" # may be called something different
    elif os.name == 'nt':
        ser.port = "COM3" # may be called something different
        ser.baudrate = baudrate
        try:
            ser.open()
            print('Serial port opened in COM4')
            ser.close()
            print("COM4")
        except:
            try:
                ser.port = "COM4"
                ser.open()
                print('Serial port opened in COM3')
                ser.close()
                print("COM3")
            except:
                pass
                print('The serial port couldn\'t be opened')

## Text Functions
def setfonts():
    """Sets font parameters"""
    global bigchar, char, charnext
    pygame.font.init()
    font     = join('media', 'Arial_Rounded_MT_Bold.ttf')
    bigchar  = pygame.font.Font(font, 96)
    char     = pygame.font.Font(font, 32)
    charnext = pygame.font.Font(font, 24)

def render_textrect(string, font, rect, text_color, background_color, justification=1):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 left-justified
                    1 (default) horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    import pygame

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.
    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    
                    raise Exception("The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise Exception("Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise Exception("Invalid justification argument: " + str(justification))
        accumulated_height += font.size(line)[1]

    return final_lines, surface

def paragraph_old(text, just_info, key, rise = 0, color = None):
    """Organizes a text into a paragraph"""
    screen.fill(background)
    row = center[1] - 20 * len(text)

    if color == None:
        color = char_color

    for line in text:
        phrasebox = pygame.Rect((resolution[0]/8, rise + 0 + row, resolution[0]*6/8, resolution[1]*5/8))
        final_lines, phrase = render_textrect(line.strip(u'\u200b'), char,  pygame.Rect((resolution[0]/8, resolution[1]/8, resolution[0]*6/8, resolution[1]*6/8)), color, background)
        screen.blit(phrase, phrasebox)
        row += 40 * len(final_lines)
    if just_info:
        if key == K_SPACE:
            foot = "Para continuar presione la BARRA ESPACIADORA..."
        elif key == K_RETURN:
            foot = "Para continuar presione la tecla ENTER..."
    else:
        foot = ""
    nextpage = charnext.render(foot, True, charnext_color)
    nextbox  = nextpage.get_rect(left = 15, bottom = resolution[1] - 15)
    screen.blit(nextpage, nextbox)
    pygame.display.flip()

def paragraph(text, key = None, no_foot = False, color = None):
    """Organizes a text into a paragraph"""
    screen.fill(background)
    row = center[1] - 20 * len(text)

    if color == None:
        color = char_color
    
    for line in text:
        phrase = char.render(line, True, char_color)
        phrasebox = phrase.get_rect(centerx=center[0], top=row)
        screen.blit(phrase, phrasebox)
        row += 40
    if key != None:
        if key == K_SPACE:
            foot = u"Para continuar presione la BARRA ESPACIADORA..."
        elif key == K_RETURN:
            foot = u"Para continuar presione la tecla ENTER..."
    else:
        foot = u"Responda con la fila superior de teclas de numéricas"
    if no_foot:
        foot = ""
    nextpage = charnext.render(foot, True, charnext_color)
    nextbox = nextpage.get_rect(left=15, bottom=resolution[1] - 15)
    screen.blit(nextpage, nextbox)
    pygame.display.flip()

def slide(text, info, key, limit_time = 0):
    """Organizes a paragraph into a slide"""
    paragraph(text, info, key)
    wait_time = wait(key, limit_time)
    return wait_time

## Program Functions
def init():
    """Init display and others"""
    setfonts()
    global screen, resolution, center, background, char_color, charnext_color, fix, fixbox, fix_think, fixbox_think, izq, der, quest, questbox
    pygame.init() # soluciona el error de inicializacion de pygame.time
    pygame.display.init()
    pygame.display.set_caption(test_name)
    pygame.mouse.set_visible(False)
    if FullScreenShow:
        resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        screen     = pygame.display.set_mode(resolution, FULLSCREEN)
    else:
        try:
            resolution = pygame.display.list_modes()[3]
        except:
            resolution = (1280, 720)
        screen     = pygame.display.set_mode(resolution)
    center = (int(resolution[0] / 2), int(resolution[1] / 2))
    izq = (int(resolution[0] / 8), (int(resolution[1] / 8)*7))
    der = ((int(resolution[0] / 8)*7), (int(resolution[1] / 8)*7))
    background     = Color('lightgray')
    char_color     = Color('black')
    charnext_color = Color('lightgray')
    fix            = char.render('+', True, char_color)
    fixbox         = fix.get_rect(centerx = center[0], centery = center[1])
    fix_think      = bigchar.render('+', True, Color('red'))
    fixbox_think   = fix.get_rect(centerx = center[0], centery = center[1])
    quest          = bigchar.render('?', True, char_color)
    questbox       = quest.get_rect(centerx = center[0], centery = center[1])
    screen.fill(background)
    pygame.display.flip()

def blackscreen(blacktime = 0):
    """Erases the screen"""
    screen.fill(background)
    pygame.display.flip()
    pygame.time.delay(blacktime)

def ends():
    """Closes the show"""
    blackscreen()
    dot    = char.render('.', True, char_color)
    dotbox = dot.get_rect(left = 15, bottom = resolution[1] - 15)
    screen.blit(dot, dotbox)
    pygame.display.flip()
    while True:
        for evento in pygame.event.get():
            if evento.type == KEYUP and evento.key == K_ESCAPE:
                pygame_exit()

def pygame_exit():
    pygame.quit()
    sys.exit()

def wait(key, limit_time):
    """Hold a bit"""

    TIME_OUT_WAIT = USEREVENT + 1
    if limit_time != 0:
        pygame.time.set_timer(TIME_OUT_WAIT, limit_time, loops = 1)

    tw = pygame.time.get_ticks()

    switch = True
    while switch:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame_exit()
            elif event.type == KEYUP:
                if event.key == key:
                    switch = False
            elif event.type == TIME_OUT_WAIT and limit_time != 0:
                switch = False

    pygame.time.set_timer(TIME_OUT_WAIT, 0)
    pygame.event.clear()                    # CLEAR EVENTS
                
    return (pygame.time.get_ticks() - tw)

def image_in_center(picture):
    center = [int(resolution[0] / 2), int(resolution[1] / 2)]
    return [x - picture.get_size()[count]/2 for count, x in enumerate(center)]

def create_image_list():
    global HAneg_images_list, HApos_images_list, LAneg_images_list, LApos_images_list

    shuffle(HAneg_images_list)
    shuffle(HApos_images_list)
    shuffle(LAneg_images_list)
    shuffle(LApos_images_list)

    middle_index = 25

    HAneg_images_list_first = HAneg_images_list[:middle_index]
    HApos_images_list_first = HApos_images_list[:middle_index]
    LAneg_images_list_first = LAneg_images_list[:middle_index]
    LApos_images_list_first = LApos_images_list[:middle_index]

    HAneg_images_list_second = HAneg_images_list[middle_index:50]
    HApos_images_list_second = HApos_images_list[middle_index:50]
    LAneg_images_list_second = LAneg_images_list[middle_index:50]
    LApos_images_list_second = LApos_images_list[middle_index:50]


    blocks = [
        [HAneg_images_list_first, HApos_images_list_second], 
        [HApos_images_list_first, HAneg_images_list_second], 
        [LAneg_images_list_first, LApos_images_list_second], 
        [LApos_images_list_first, LAneg_images_list_second]
    ]

    returned_blocks = [[],[],[],[]]

    for counter, block in enumerate(blocks):
        actual_balance = 0

        for _ in range(len(block[0]) + len(block[1])):
            if actual_balance == 0:
                selector = getrandbits(1)
            elif actual_balance == 1:
                selector = 0
            elif actual_balance == -1:
                selector = 1
            returned_blocks[counter].append(block[selector].pop(0))
            if selector == 0:
                actual_balance -= 1
            elif selector == 1:
                actual_balance += 1

    return returned_blocks

def show_image(image, scale):
    screen.fill(background)
    picture = pygame.image.load(image)
    picture = pygame.transform.scale(picture, [int(scale[0]), int(scale[1])])
    screen.blit(picture,image_in_center(picture))
        
    pygame.display.flip()

def save_user(dfile, subj_name, subj_type, block_number, image_type, image_id, rt):
    dfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (subj_name.lower(), subj_type.upper(), block_number, image_type, image_id, (rt != 0), rt, (image_id in animals_id_list)==(rt != 0)))

def show_images(image_list, dfile, subj_name, subj_type, block_number):    
    image_change = USEREVENT + 5

    pygame.time.set_timer(image_change, 6000, loops = 50)

    done = False
    count = 0

    screen.fill(background)
    pygame.display.flip()

    tw = pygame.time.get_ticks()
    rt = 0

    show_image(image_list[count], base_size)
    # start block trigger 1 to 4 +20 if block is HA, + 0 if not, + 40 if is second block + 0 if not
    send_trigger(start_block_trigger + (20 if image_list[count].split(directory_separator)[-2] == 'HApos' else 0) + (40 if block_number >= 3 else 0)) # start block trigger 1 to 4
    count += 1

    while not done:
        for event in pygame.event.get():
            if event.type == KEYUP and event.key == K_ESCAPE:
                pygame_exit()

            elif event.type == KEYUP and event.key == K_c:
                done=True

            elif event.type == KEYDOWN and event.key == K_SPACE:
                rt = pygame.time.get_ticks() - tw
                send_trigger(space_trigger)

            elif event.type == image_change:        
                print(pygame.time.get_ticks() - tw)

                show_image(image_list[count], base_size)
                # Exposure image trigger +50 if is an animal image (+20 if is an HA image, +0 if not)
                send_trigger(new_image_trigger + (50 if image_list[count].split(directory_separator)[-1][:-4] in animals_id_list else 0) + (20 if image_list[count].split(directory_separator)[-2] == 'HApos' else 0))

                dfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (subj_name.lower(), subj_type.upper(), block_number, image_list[count].split(directory_separator)[-2], image_list[count].split(directory_separator)[-1][:-4], (rt != 0), rt, (image_list[count].split(directory_separator)[-1][:-4] in animals_id_list)==(rt != 0)))

                # reset variables to default
                tw = pygame.time.get_ticks()
                rt = 0
                count += 1

                if count >= 50:
                    done = True

    pygame.time.set_timer(image_change, 0)

    pygame.event.clear()                    # CLEAR EVENTS

## Main Function
def main():
    """Game's main loop"""

    if not testing:
        init_com()

    # Si no existe la carpeta data se crea
    if not os.path.exists('data/'):
        os.makedirs('data/')

    bfile = open('list.csv', 'w')
    bfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % ("First List", " ", "Second List", " ", "Third List", " ", "Fourth List", " "))
    bfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % ("Image", "Type", "Image", "Type", "Image", "Type", "Image", "Type"))

    image_list = create_image_list()

    for i in range(len(image_list[0])):
        bfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (
            int(image_list[0][i].split(directory_separator)[-1][:-4]), image_list[0][i].split(directory_separator)[-2],
            int(image_list[1][i].split(directory_separator)[-1][:-4]), image_list[1][i].split(directory_separator)[-2],
            int(image_list[2][i].split(directory_separator)[-1][:-4]), image_list[2][i].split(directory_separator)[-2],
            int(image_list[3][i].split(directory_separator)[-1][:-4]), image_list[3][i].split(directory_separator)[-2],    
        ))
    bfile.close()
    
    # Username = correo_type(?)
    uid = input("Ingrese el ID del participante y presione ENTER para iniciar: ")

    while( len(uid.split("_")) != 2 or (uid.split("_")[1].upper() != 'HA' and uid.split("_")[1].upper() != 'LA') ):
        os.system('cls')
        print("ID ingresado no cumple con las condiciones, contacte con el encargado...")
        subj_name = input("Ingrese el ID del participante y presione ENTER para iniciar: ")

    subj_name, subj_type = uid.lower().split("_")

    # Iniciador de Pygame
    pygame.init()

    csv_name  = join('data', date_name + '_' + subj_name + '.csv')
    dfile = open(csv_name, 'w')
    dfile.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % ("Sujeto", "Tipo Sujeto", "Bloque", "TipoImagen", "IdImagen", "Respuesta", "TReaccion", "Acierto"))
    dfile.flush()

    init()
    pygame.mixer.pre_init(48000, -16, 2, 512)
    pygame.mixer.init()
    pygame.mixer.music.set_volume(2)

    # Import song
    selected_sound = pygame.mixer.Sound('media/audio/%s.mp3' % (subj_type.upper()))

    send_trigger(start_trigger)

    # first 2 blocks are HA, second 2 blocks are LA
    if subj_type.lower() == 'ha':
        block1_images = image_list[0]
        block2_images = image_list[2]
        block3_images = image_list[1]
        block4_images = image_list[3]
    else:
        block1_images = image_list[2]
        block2_images = image_list[0]
        block3_images = image_list[3]
        block4_images = image_list[1]
    
    '''
    correo@gmail.com_LA
    correo@gmail.com_HA
    - primera instruction general
    - Bloque 1, 50 imágenes del tipo seleccionado del sujeto
    - Bloque 2, 50 imágenes del tipo contrario al sujeto
    - Bloque 3, 50 imágenes del tipo seleccionado del sujeto
    - Bloque 4, 50 imágenes del tipo contrario al sujeto
    '''

    #carga de lista de imágenes, return ([first_image_list, second_image_list, third_image_list, fourth_image_list])  
    slide(select_slide('welcome'), False , K_SPACE)

    slide(select_slide('Instructions'), False , K_SPACE)

    #starting sound
    selected_sound.play()

    show_images(block1_images, dfile, subj_name, subj_type, 1)
    dfile.flush()
    show_images(block2_images, dfile, subj_name, subj_type, 2)
    dfile.flush()
    
    show_images(block3_images, dfile, subj_name, subj_type, 3)
    dfile.flush()
    
    show_images(block4_images, dfile, subj_name, subj_type, 4)
    dfile.flush()
    
    slide(select_slide('farewell'), True , K_SPACE)
    dfile.close()
    ends()

## Experiment starts here...
if __name__ == "__main__":
    main()
